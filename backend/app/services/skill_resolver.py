import re

from sqlalchemy.orm import Session

from app.models import Skill, SkillAlias, UnknownSkill


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def resolve(db: Session, raw_text: str) -> Skill | None:
    text = (raw_text or "").strip()
    if not text:
        return None

    skill = (
        db.query(Skill)
        .filter(Skill.name.ilike(text), Skill.is_deprecated.is_(False))
        .first()
    )
    if skill:
        return skill

    alias = db.query(SkillAlias).filter(SkillAlias.alias.ilike(text)).first()
    if alias and not alias.skill.is_deprecated:
        return alias.skill

    normalized = normalize(text)
    if not normalized:
        return None

    for candidate in db.query(Skill).filter(Skill.is_deprecated.is_(False)).all():
        if normalize(candidate.name) == normalized:
            return candidate

    for candidate_alias in db.query(SkillAlias).all():
        if normalize(candidate_alias.alias) == normalized:
            if not candidate_alias.skill.is_deprecated:
                return candidate_alias.skill

    return None


def record_unknown(db: Session, raw_text: str) -> None:
    text = (raw_text or "").strip()
    normalized = normalize(text)

    if not normalized:
        return

    existing = (
        db.query(UnknownSkill)
        .filter(UnknownSkill.normalized_text == normalized)
        .first()
    )

    if existing:
        existing.seen_count += 1
    else:
        db.add(UnknownSkill(raw_text=text, normalized_text=normalized))


def resolve_many(db: Session, raw_texts: list[str]) -> list[Skill]:
    resolved = []
    seen_ids = set()

    for raw_text in raw_texts or []:
        skill = resolve(db, raw_text)

        if skill is None:
            record_unknown(db, raw_text)
            continue

        if skill.id not in seen_ids:
            seen_ids.add(skill.id)
            resolved.append(skill)

    return resolved