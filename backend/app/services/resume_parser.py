from sqlalchemy.orm import Session

from app.prompts import get_prompts
from app.services.llm_client import generate_json
from app.services.skill_resolver import resolve_many

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


def clean_choice(value, allowed: set[str]) -> str | None:
    text = clean_text(value)
    return text if text in allowed else None


def clean_experience(value) -> int:
    try:
        years = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(years, 50))


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

    resolved = resolve_many(db, names)
    matched = {skill.name.lower() for skill in resolved}
    unmatched = [name for name in names if name.strip().lower() not in matched]

    return {
        "phone": clean_text(result.get("phone")),
        "skill_ids": [skill.id for skill in resolved],
        "skill_names": [skill.name for skill in resolved],
        "unmatched_skills": unmatched,
        "experience_years": clean_experience(result.get("experience_years")),
        "education_level": clean_choice(result.get("education_level"), EDUCATION_LEVELS),
        "university": clean_text(result.get("university")),
        "field": clean_choice(result.get("field"), FIELDS),
        "projects": clean_text(result.get("projects")),
        "project_summary": clean_text(result.get("project_summary")),
        "certifications": clean_text(result.get("certifications")),
    }