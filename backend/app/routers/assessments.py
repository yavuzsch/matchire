from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import require_candidate, require_employer
from app.models import Application, ApplicationStatus, AssessmentAnswer, AssessmentQuestion, Job, User
from app.schemas.assessment import (
    AnswerOut,
    AnswerReview,
    AnswerSubmit,
    AssessmentResult,
    QuestionForCandidate,
    QuestionOut,
    QuestionSelect,
)
from app.services.assessment_service import is_eligible
from app.services.evaluation_service import evaluate_answer
from app.services.llm_client import LLMUnavailableError
from app.services.question_service import generate_questions

router = APIRouter(prefix="/assessments", tags=["assessments"])


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


def ensure_no_answers(db: Session, job: Job) -> None:
    answered = (
        db.query(AssessmentAnswer)
        .join(AssessmentQuestion, AssessmentAnswer.question_id == AssessmentQuestion.id)
        .filter(AssessmentQuestion.job_id == job.id)
        .first()
    )
    if answered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.ASSESSMENT_ALREADY_STARTED},
        )


@router.post("/jobs/{job_id}/questions", response_model=list[QuestionOut])
def create_questions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = get_owned_job(db, job_id, current_user)
    ensure_no_answers(db, job)

    try:
        generated = generate_questions(job)
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": errors.LLM_UNAVAILABLE},
        )

    db.query(AssessmentQuestion).filter(AssessmentQuestion.job_id == job.id).delete()

    questions = [
        AssessmentQuestion(job_id=job.id, question_text=text) for text in generated
    ]

    db.add_all(questions)
    db.commit()

    return (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.job_id == job.id)
        .order_by(AssessmentQuestion.id)
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
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.job_id == job.id)
        .order_by(AssessmentQuestion.id)
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
    ensure_no_answers(db, job)

    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.job_id == job.id)
        .order_by(AssessmentQuestion.id)
        .all()
    )

    for question in questions:
        question.is_selected = question.id in body.question_ids

    db.commit()

    return questions


@router.get("/applications/{application_id}/questions", response_model=list[QuestionForCandidate])
def list_assessment_questions(
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
            detail={"code": errors.ASSESSMENT_NOT_ELIGIBLE},
        )

    questions = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .order_by(AssessmentQuestion.id)
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
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.application_id == application.id)
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
        db.query(AssessmentAnswer, AssessmentQuestion)
        .join(AssessmentQuestion, AssessmentAnswer.question_id == AssessmentQuestion.id)
        .filter(AssessmentAnswer.application_id == application.id)
        .order_by(AssessmentQuestion.id)
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
            detail={"code": errors.ASSESSMENT_NOT_ELIGIBLE},
        )

    question = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.id == body.question_id,
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .first()
    )
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.QUESTION_NOT_FOUND},
        )

    existing = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.application_id == application.id,
            AssessmentAnswer.question_id == question.id,
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

    answer = AssessmentAnswer(
        application_id=application.id,
        question_id=question.id,
        answer_text=body.answer_text,
        is_correct=is_correct,
        score=score,
    )
    db.add(answer)
    db.flush()

    if application.status == ApplicationStatus.PENDING:
        application.status = ApplicationStatus.ASSESSMENT

    update_assessment_score(db, application, job)
    db.commit()
    db.refresh(answer)

    return answer


@router.get("/applications/{application_id}/result", response_model=AssessmentResult)
def get_assessment_result(
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

    total_questions = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .count()
    )

    answered_count = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.application_id == application.id)
        .count()
    )

    return AssessmentResult(
        application_id=application.id,
        total_questions=total_questions,
        answered_count=answered_count,
        completed=total_questions > 0 and answered_count >= total_questions,
    )


def update_assessment_score(db: Session, application: Application, job: Job) -> None:
    selected_count = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .count()
    )

    if selected_count == 0:
        return

    answers = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.application_id == application.id)
        .all()
    )

    total = sum(answer.score for answer in answers)
    application.assessment_score = round(total / selected_count, 2)

    completed = len(answers) >= selected_count

    if completed:
        weight = job.assessment_weight / 100
        application.total_score = round(
            application.compatibility_score * (1 - weight)
            + application.assessment_score * weight,
            2,
        )
        application.status = ApplicationStatus.COMPLETED
    else:
        application.total_score = application.compatibility_score