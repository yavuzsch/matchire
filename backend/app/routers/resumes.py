from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_candidate
from app.models import Resume, User
from app.schemas.resume import ResumeCreate, ResumeOut

router = APIRouter(prefix="/resumes", tags=["resumes"])


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
            detail="Zaten bir özgeçmişiniz var, güncelleme yapabilirsiniz",
        )

    resume = Resume(candidate_id=current_user.id, **body.model_dump())
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/me", response_model=ResumeOut)
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).first()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Henüz özgeçmiş oluşturmadınız",
        )
    return resume


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
            detail="Henüz özgeçmiş oluşturmadınız",
        )

    for key, value in body.model_dump().items():
        setattr(resume, key, value)

    db.commit()
    db.refresh(resume)
    return resume