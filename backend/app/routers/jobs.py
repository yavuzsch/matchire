from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_employer
from app.models import Application, AssessmentQuestion, Job, JobSkill, Skill, User, UserRole
from app.schemas.job import (
    JobCreate,
    JobFull,
    JobParsed,
    JobParseIn,
    JobPublic,
    JobSkillOut,
    JobStatusUpdate,
)
from app.services.job_parser import parse_job
from app.services.llm_client import LLMUnavailableError

router = APIRouter(prefix="/jobs", tags=["jobs"])


def build_job_full(job: Job) -> JobFull:
    return JobFull(
        id=job.id,
        employer_id=job.employer_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        description=job.description,
        skills=[
            JobSkillOut(
                skill_id=item.skill_id,
                name=item.skill.name,
                requirement=item.requirement,
                weight=item.weight,
            )
            for item in job.skills
        ],
        experience_years=job.experience_years,
        education_level=job.education_level,
        field=job.field,
        language=job.language,
        assessment_slots=job.assessment_slots,
        assessment_weight=job.assessment_weight,
        is_active=job.is_active,
        is_closed=job.is_closed,
        created_at=job.created_at,
    )


def validate_skill_ids(db: Session, skill_ids: list[int]) -> None:
    if not skill_ids:
        return

    found = (
        db.query(Skill.id)
        .filter(Skill.id.in_(skill_ids), Skill.is_deprecated.is_(False))
        .all()
    )

    if len(found) != len(set(skill_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.SKILL_NOT_FOUND},
        )


@router.post("/parse", response_model=JobParsed)
def parse_job_text(
    body: JobParseIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    try:
        parsed = parse_job(db, body.text, settings.DEFAULT_LANGUAGE)
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": errors.LLM_UNAVAILABLE},
        )

    db.commit()
    return JobParsed(**parsed)


@router.post("", response_model=JobFull, status_code=status.HTTP_201_CREATED)
def create_job(
    body: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    validate_skill_ids(db, [item.skill_id for item in body.skills])

    payload = body.model_dump(exclude={"skills"})
    job = Job(employer_id=current_user.id, **payload)
    db.add(job)
    db.flush()

    for item in body.skills:
        db.add(
            JobSkill(
                job_id=job.id,
                skill_id=item.skill_id,
                requirement=item.requirement,
                weight=item.weight,
            )
        )

    db.commit()
    db.refresh(job)
    return build_job_full(job)


@router.get("", response_model=list[JobPublic])
def list_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.is_active.is_(True))
        .order_by(Job.id.desc())
        .all()
    )


@router.get("/mine", response_model=list[JobFull])
def list_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    jobs = (
        db.query(Job)
        .filter(Job.employer_id == current_user.id)
        .order_by(Job.id.desc())
        .all()
    )

    return [build_job_full(job) for job in jobs]


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.JOB_NOT_FOUND},
        )

    if current_user.role == UserRole.EMPLOYER and job.employer_id == current_user.id:
        return build_job_full(job)

    return JobPublic.model_validate(job)


@router.patch("/{job_id}/status", response_model=JobFull)
def update_job_status(
    job_id: int,
    body: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.JOB_NOT_FOUND},
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": errors.JOB_ACCESS_DENIED},
        )

    if body.is_active is not None:
        job.is_active = body.is_active

    if body.is_closed is not None:
        job.is_closed = body.is_closed

    db.commit()
    db.refresh(job)
    return build_job_full(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.JOB_NOT_FOUND},
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": errors.JOB_ACCESS_DENIED},
        )

    has_applications = (
        db.query(Application).filter(Application.job_id == job.id).first()
    )
    has_questions = (
        db.query(AssessmentQuestion).filter(AssessmentQuestion.job_id == job.id).first()
    )

    if has_applications or has_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.JOB_HAS_ACTIVITY},
        )

    db.delete(job)
    db.commit()