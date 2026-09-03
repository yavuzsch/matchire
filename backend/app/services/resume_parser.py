from sqlalchemy.orm import Session

from app.prompts import get_prompts
from app.services.llm_client import generate_json
from app.services.skill_resolver import record_unknown, resolve

EDUCATION_LEVELS = {
    "high_school",
    "associate",
    "bachelor",
    "master",
    "doctorate",
}

FIELDS = {
    "software_development",
    "data_science",
    "artificial_intelligence",
    "cyber_security",
    "mobile_development",
    "data_engineering",
    "devops",
    "quality_assurance",
}

MAX_SKILLS = 40


def clean_text(value) -> str | None:
    if not isinstance(value, str):
        return None

    text = value.strip()
    return text or None


def clean_block(value) -> str | None:
    if isinstance(value, str):
        return clean_text(value)

    if not isinstance(value, list):
        return None

    lines = []

    for item in value:
        if isinstance(item, str):
            text = clean_text(item)
            if text:
                lines.append(text)
            continue

        if not isinstance(item, dict):
            continue

        name = clean_text(item.get("name")) or clean_text(item.get("title"))
        description = clean_text(item.get("description"))

        if name and description:
            lines.append(f"{name}: {description}")
        elif name or description:
            lines.append(name or description)

    return "\n".join(lines) or None


def clean_choice(value, allowed: set[str]) -> str | None:
    text = clean_text(value)
    return text if text in allowed else None


def clean_experience(value) -> int:
    try:
        years = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(years, 50))


def resolve_skill_names(db: Session, names: list[str]) -> tuple[list, list[str]]:
    resolved = []
    unmatched = []
    seen = set()

    for name in names:
        skill = resolve(db, name)

        if skill is None:
            record_unknown(db, name)
            unmatched.append(name)
            continue

        if skill.id not in seen:
            seen.add(skill.id)
            resolved.append(skill)

    return resolved, unmatched


def parse_resume(db: Session, text: str, language: str) -> dict:
    prompts = get_prompts(language)
    result = generate_json(prompts.RESUME_TEMPLATE.format(text=text))

    if not isinstance(result, dict):
        result = {}

    raw_skills = result.get("skills")
    names = [
        name
        for name in (raw_skills if isinstance(raw_skills, list) else [])
        if isinstance(name, str) and name.strip()
    ][:MAX_SKILLS]

    resolved, unmatched = resolve_skill_names(db, names)

    return {
        "phone": clean_text(result.get("phone")),
        "skill_ids": [skill.id for skill in resolved],
        "skill_names": [skill.name for skill in resolved],
        "unmatched_skills": unmatched,
        "experience_years": clean_experience(result.get("experience_years")),
        "education_level": clean_choice(result.get("education_level"), EDUCATION_LEVELS),
        "university": clean_text(result.get("university")),
        "field": clean_choice(result.get("field"), FIELDS),
        "projects": clean_block(result.get("projects")),
        "project_summary": clean_text(result.get("project_summary")),
        "certifications": clean_block(result.get("certifications")),
    }