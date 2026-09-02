from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core import errors
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Skill, SkillGroup, User
from app.schemas.skill import SkillGroupOut, SkillOut, SkillProposal, SkillProposalOut
from app.services.llm_client import LLMUnavailableError
from app.services.skill_promoter import SkillLimitError, SkillRejectedError, promote

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillGroupOut])
def list_skills(
    lang: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    language = lang or settings.DEFAULT_LANGUAGE
    groups = db.query(SkillGroup).order_by(SkillGroup.position).all()
    result = []

    for group in groups:
        labels = {label.language: label.label for label in group.labels}
        label = (
            labels.get(language)
            or labels.get(settings.DEFAULT_LANGUAGE)
            or group.key
        )

        skills = [
            SkillOut(id=skill.id, name=skill.name)
            for skill in sorted(
                (
                    s
                    for s in group.skills
                    if not s.is_deprecated and s.is_verified
                ),
                key=lambda item: item.name.lower(),
            )
        ]

        if skills:
            result.append(SkillGroupOut(key=group.key, label=label, skills=skills))

    return result


@router.get("/flat", response_model=list[SkillOut])
def list_skills_flat(db: Session = Depends(get_db)):
    skills = (
        db.query(Skill)
        .filter(Skill.is_deprecated.is_(False), Skill.is_verified.is_(True))
        .order_by(Skill.name)
        .all()
    )

    return [SkillOut(id=skill.id, name=skill.name) for skill in skills]


@router.post("/propose", response_model=SkillProposalOut, status_code=status.HTTP_201_CREATED)
def propose_skill(
    body: SkillProposal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        skill = promote(db, body.term, current_user)
    except SkillLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": errors.SKILL_LIMIT_REACHED},
        )
    except SkillRejectedError:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": errors.SKILL_REJECTED},
        )
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": errors.LLM_UNAVAILABLE},
        )

    db.commit()
    db.refresh(skill)

    return SkillProposalOut(
        id=skill.id, name=skill.name, is_verified=skill.is_verified
    )