from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import require_candidate, require_employer
from app.models import Application, Job, Resume, User
from app.schemas.application import ApplicationCreate, ApplicationOut, CandidateRow
from app.services.matching_service import calculate_compatibility, find_missing_mandatory_skills

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    job = db.query(Job).filter(Job.id == body.job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.JOB_NOT_FOUND},
        )

    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.RESUME_REQUIRED},
        )

    existing = (
        db.query(Application)
        .filter(
            Application.job_id == job.id,
            Application.candidate_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.ALREADY_APPLIED},
        )

    missing_skills = find_missing_mandatory_skills(job, resume)
    if missing_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.MISSING_MANDATORY_SKILLS, "skills": missing_skills},
        )

    compatibility_score = calculate_compatibility(job, resume)

    application = Application(
        job_id=job.id,
        candidate_id=current_user.id,
        compatibility_score=compatibility_score,
        interview_score=0.0,
        total_score=compatibility_score,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/mine", response_model=list[ApplicationOut])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    return (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id)
        .order_by(Application.id.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=list[CandidateRow])
def list_job_applications(
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

    rows = (
        db.query(Application, User)
        .join(User, Application.candidate_id == User.id)
        .filter(Application.job_id == job_id)
        .order_by(Application.total_score.desc())
        .all()
    )

    return [
        CandidateRow(
            application_id=app.id,
            candidate_id=user.id,
            full_name=user.full_name,
            email=user.email,
            compatibility_score=app.compatibility_score,
            interview_score=app.interview_score,
            total_score=app.total_score,
            status=app.status,
        )
        for app, user in rows
    ]