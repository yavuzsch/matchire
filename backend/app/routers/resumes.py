from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.database import get_db
from app.core.deps import require_candidate
from app.models import Resume, ResumeSkill, Skill, User
from app.schemas.resume import ResumeCreate, ResumeOut, ResumeSkillOut

router = APIRouter(prefix="/resumes", tags=["resumes"])


def build_resume_out(resume: Resume) -> ResumeOut:
    return ResumeOut(
        id=resume.id,
        candidate_id=resume.candidate_id,
        phone=resume.phone,
        skills=[
            ResumeSkillOut(skill_id=item.skill_id, name=item.skill.name)
            for item in resume.skills
        ],
        experience_years=resume.experience_years,
        education_level=resume.education_level,
        university=resume.university,
        field=resume.field,
        projects=resume.projects,
        certifications=resume.certifications,
        languages=resume.languages,
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


def set_resume_skills(db: Session, resume: Resume, skill_ids: list[int]) -> None:
    db.query(ResumeSkill).filter(ResumeSkill.resume_id == resume.id).delete()

    for skill_id in dict.fromkeys(skill_ids):
        db.add(ResumeSkill(resume_id=resume.id, skill_id=skill_id))


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def create_resume(
    body: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    existing = db.query(Resume).filter(Resume.candidate_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.RESUME_ALREADY_EXISTS},
        )

    validate_skill_ids(db, body.skill_ids)

    payload = body.model_dump(exclude={"skill_ids"})
    resume = Resume(candidate_id=current_user.id, **payload)
    db.add(resume)
    db.flush()

    set_resume_skills(db, resume, body.skill_ids)

    db.commit()
    db.refresh(resume)
    return build_resume_out(resume)


@router.get("/me", response_model=ResumeOut)
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.RESUME_NOT_FOUND},
        )

    return build_resume_out(resume)


@router.put("/me", response_model=ResumeOut)
def update_my_resume(
    body: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": errors.RESUME_NOT_FOUND},
        )

    validate_skill_ids(db, body.skill_ids)

    for key, value in body.model_dump(exclude={"skill_ids"}).items():
        setattr(resume, key, value)

    set_resume_skills(db, resume, body.skill_ids)

    db.commit()
    db.refresh(resume)
    return build_resume_out(resume)