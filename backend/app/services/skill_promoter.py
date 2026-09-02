from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Skill, SkillAlias, SkillGroup, User
from app.prompts.taxonomy import PROMOTE_TEMPLATE
from app.services.llm_client import generate_json
from app.services.skill_resolver import record_unknown, resolve

DAILY_LIMIT = 3


class SkillRejectedError(Exception):
    pass


class SkillLimitError(Exception):
    pass


def count_today(db: Session, user: User) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=1)

    return (
        db.query(Skill)
        .filter(Skill.created_by == user.id, Skill.created_at >= since)
        .count()
    )


def build_prompt(db: Session, term: str) -> str:
    groups = db.query(SkillGroup).order_by(SkillGroup.position).all()
    lines = [f"- {group.key}" for group in groups]

    return PROMOTE_TEMPLATE.format(term=term, groups="\n".join(lines))


def promote(db: Session, term: str, user: User) -> Skill:
    text = (term or "").strip()

    if not text:
        raise SkillRejectedError("empty term")

    existing = resolve(db, text)
    if existing:
        add_alias(db, existing, text)
        return existing

    if count_today(db, user) >= DAILY_LIMIT:
        raise SkillLimitError("daily limit reached")

    result = generate_json(build_prompt(db, text))

    if not isinstance(result, dict) or not result.get("accepted"):
        record_unknown(db, text)
        raise SkillRejectedError("not a valid skill")

    name = (result.get("name") or "").strip()
    group_key = (result.get("group") or "").strip()

    if not name or not group_key:
        record_unknown(db, text)
        raise SkillRejectedError("incomplete response")

    group = db.query(SkillGroup).filter(SkillGroup.key == group_key).first()
    if group is None:
        record_unknown(db, text)
        raise SkillRejectedError("unknown group")

    canonical = resolve(db, name)
    if canonical:
        add_alias(db, canonical, text)
        return canonical

    skill = Skill(
        name=name,
        group_id=group.id,
        source="user",
        is_verified=False,
        created_by=user.id,
    )
    db.add(skill)
    db.flush()

    aliases = result.get("aliases") or []
    for alias in [*aliases, text]:
        add_alias(db, skill, alias)

    return skill


def add_alias(db: Session, skill: Skill, alias: str) -> None:
    text = (alias or "").strip()

    if not text or text.lower() == skill.name.lower():
        return

    exists = db.query(SkillAlias).filter(SkillAlias.alias.ilike(text)).first()
    if exists:
        return

    db.add(SkillAlias(alias=text, skill_id=skill.id))