from sqlalchemy.orm import Session

from app.models import SkillRequirement
from app.prompts import get_prompts
from app.services.llm_client import generate_json
from app.services.resume_parser import (
    EDUCATION_LEVELS,
    FIELDS,
    clean_choice,
    clean_experience,
    clean_text,
)
from app.services.skill_resolver import record_unknown, resolve

MAX_SKILLS = 15

REQUIREMENTS = {item.value for item in SkillRequirement}
DEFAULT_REQUIREMENT = SkillRequirement.REQUIRED.value

DEFAULT_WEIGHT = {
    SkillRequirement.MANDATORY.value: 3,
    SkillRequirement.REQUIRED.value: 2,
    SkillRequirement.OPTIONAL.value: 1,
}


def parse_job(db: Session, text: str, language: str) -> dict:
    prompts = get_prompts(language)
    result = generate_json(prompts.JOB_TEMPLATE.format(text=text))

    if not isinstance(result, dict):
        result = {}

    raw_skills = result.get("skills")
    entries = raw_skills if isinstance(raw_skills, list) else []

    skills = []
    unmatched = []
    seen = set()

    for entry in entries[:MAX_SKILLS]:
        if not isinstance(entry, dict):
            continue

        name = clean_text(entry.get("name"))
        if not name:
            continue

        requirement = entry.get("requirement")
        if requirement not in REQUIREMENTS:
            requirement = DEFAULT_REQUIREMENT

        skill = resolve(db, name)

        if skill is None:
            record_unknown(db, name)
            unmatched.append(name)
            continue

        if skill.id in seen:
            continue

        seen.add(skill.id)
        skills.append(
            {
                "skill_id": skill.id,
                "name": skill.name,
                "requirement": requirement,
                "weight": DEFAULT_WEIGHT[requirement],
            }
        )

    return {
        "title": clean_text(result.get("title")),
        "company_name": clean_text(result.get("company_name")),
        "location": clean_text(result.get("location")),
        "description": clean_text(result.get("description")),
        "skills": skills,
        "unmatched_skills": unmatched,
        "experience_years": clean_experience(result.get("experience_years")),
        "education_level": clean_choice(result.get("education_level"), EDUCATION_LEVELS),
        "field": clean_choice(result.get("field"), FIELDS),
    }