from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Skill, SkillGroup
from app.schemas.skill import SkillGroupOut, SkillOut

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
                (s for s in group.skills if not s.is_deprecated),
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
        .filter(Skill.is_deprecated.is_(False))
        .order_by(Skill.name)
        .all()
    )

    return [SkillOut(id=skill.id, name=skill.name) for skill in skills]