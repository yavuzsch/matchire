from app.models import Job, SkillRequirement
from app.prompts import get_prompts
from app.services.llm_client import generate_json

QUESTION_COUNT = 8


def build_prompt(job: Job) -> str:
    prompts = get_prompts(job.language)

    names = [
        item.skill.name
        for item in job.skills
        if item.requirement != SkillRequirement.OPTIONAL
    ]

    return prompts.QUESTION_TEMPLATE.format(
        count=QUESTION_COUNT,
        title=job.title,
        skills=", ".join(names) or "-",
        experience_years=job.experience_years or 0,
    )


def generate_questions(job: Job) -> list[str]:
    questions = generate_json(build_prompt(job))

    if not isinstance(questions, list):
        return []

    return [str(question).strip() for question in questions if str(question).strip()]