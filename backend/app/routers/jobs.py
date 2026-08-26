from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import get_current_user, require_employer
from app.models import Application, AssessmentQuestion, Job, User, UserRole
from app.schemas.job import JobCreate, JobPublic, JobFull, JobStatusUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobFull, status_code=status.HTTP_201_CREATED)
def create_job(
    body: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    job = Job(employer_id=current_user.id, **body.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


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
    return (
        db.query(Job)
        .filter(Job.employer_id == current_user.id)
        .order_by(Job.id.desc())
        .all()
    )


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
        return JobFull.model_validate(job)

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
    return job


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