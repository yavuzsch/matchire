from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import get_current_user, require_employer
from app.models import Job, User, UserRole
from app.schemas.job import JobCreate, JobPublic, JobFull

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
    return db.query(Job).order_by(Job.id.desc()).all()


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