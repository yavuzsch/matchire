from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import require_candidate, require_employer
from app.models import Application, InterviewAnswer, InterviewQuestion, Job, User
from app.schemas.interview import (
    AnswerOut,
    AnswerReview,
    AnswerSubmit,
    InterviewResult,
    QuestionForCandidate,
    QuestionOut,
    QuestionSelect,
)
from app.services.evaluation_service import evaluate_answer
from app.services.interview_service import is_eligible
from app.services.llm_client import LLMUnavailableError
from app.services.question_service import generate_questions

router = APIRouter(prefix="/interviews", tags=["interviews"])


def get_owned_job(db: Session, job_id: int, employer: User) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.JOB_NOT_FOUND},
        )

    if job.employer_id != employer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": errors.JOB_ACCESS_DENIED},
        )

    return job


@router.post("/jobs/{job_id}/questions", response_model=list[QuestionOut])
def create_questions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = get_owned_job(db, job_id, current_user)

    try:
        generated = generate_questions(job)
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": errors.LLM_UNAVAILABLE},
        )

    db.query(InterviewQuestion).filter(InterviewQuestion.job_id == job.id).delete()

    questions = [
        InterviewQuestion(job_id=job.id, question_text=text) for text in generated
    ]

    db.add_all(questions)
    db.commit()

    return (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.job_id == job.id)
        .order_by(InterviewQuestion.id)
        .all()
    )


@router.get("/jobs/{job_id}/questions", response_model=list[QuestionOut])
def list_questions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = get_owned_job(db, job_id, current_user)

    return (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.job_id == job.id)
        .order_by(InterviewQuestion.id)
        .all()
    )


@router.put("/jobs/{job_id}/questions", response_model=list[QuestionOut])
def select_questions(
    job_id: int,
    body: QuestionSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = get_owned_job(db, job_id, current_user)

    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.job_id == job.id)
        .order_by(InterviewQuestion.id)
        .all()
    )

    for question in questions:
        question.is_selected = question.id in body.question_ids

    db.commit()

    return questions


@router.get("/applications/{application_id}/questions", response_model=list[QuestionForCandidate])
def list_interview_questions(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.candidate_id == current_user.id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.APPLICATION_NOT_FOUND},
        )

    job = db.query(Job).filter(Job.id == application.job_id).first()

    if not is_eligible(db, job, application):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": errors.INTERVIEW_NOT_ELIGIBLE},
        )

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.job_id == job.id,
            InterviewQuestion.is_selected.is_(True),
        )
        .order_by(InterviewQuestion.id)
        .all()
    )

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.NO_QUESTIONS_SELECTED},
        )

    return questions


@router.get("/applications/{application_id}/answers", response_model=list[AnswerOut])
def list_answers(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.candidate_id == current_user.id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.APPLICATION_NOT_FOUND},
        )

    return (
        db.query(InterviewAnswer)
        .filter(InterviewAnswer.application_id == application.id)
        .all()
    )


@router.get("/applications/{application_id}/review", response_model=list[AnswerReview])
def review_answers(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.APPLICATION_NOT_FOUND},
        )

    get_owned_job(db, application.job_id, current_user)

    rows = (
        db.query(InterviewAnswer, InterviewQuestion)
        .join(InterviewQuestion, InterviewAnswer.question_id == InterviewQuestion.id)
        .filter(InterviewAnswer.application_id == application.id)
        .order_by(InterviewQuestion.id)
        .all()
    )

    return [
        AnswerReview(
            question_text=question.question_text,
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            score=answer.score,
        )
        for answer, question in rows
    ]


@router.post("/applications/{application_id}/answers", response_model=AnswerOut)
def submit_answer(
    application_id: int,
    body: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.candidate_id == current_user.id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.APPLICATION_NOT_FOUND},
        )

    job = db.query(Job).filter(Job.id == application.job_id).first()

    if not is_eligible(db, job, application):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": errors.INTERVIEW_NOT_ELIGIBLE},
        )

    question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.id == body.question_id,
            InterviewQuestion.job_id == job.id,
            InterviewQuestion.is_selected.is_(True),
        )
        .first()
    )
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.QUESTION_NOT_FOUND},
        )

    existing = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.application_id == application.id,
            InterviewAnswer.question_id == question.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.ALREADY_ANSWERED},
        )

    try:
        is_correct, score = evaluate_answer(question, body.answer_text, job.language)
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": errors.LLM_UNAVAILABLE},
        )

    answer = InterviewAnswer(
        application_id=application.id,
        question_id=question.id,
        answer_text=body.answer_text,
        is_correct=is_correct,
        score=score,
    )
    db.add(answer)
    db.flush()

    update_interview_score(db, application, job)
    db.commit()
    db.refresh(answer)

    return answer


def update_interview_score(db: Session, application: Application, job: Job) -> None:
    selected_count = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.job_id == job.id,
            InterviewQuestion.is_selected.is_(True),
        )
        .count()
    )

    answers = (
        db.query(InterviewAnswer)
        .filter(InterviewAnswer.application_id == application.id)
        .all()
    )

    if selected_count == 0:
        return

    total = sum(answer.score for answer in answers)
    application.interview_score = round(total / selected_count, 2)

    if answers:
        application.total_score = round(
            (application.compatibility_score + application.interview_score) / 2, 2
        )
    else:
        application.total_score = application.compatibility_score