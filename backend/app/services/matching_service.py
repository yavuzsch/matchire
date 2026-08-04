from app.models import Job, Resume

EDUCATION_LEVELS = {
    "high_school": 1,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "doctorate": 5,
}

SKILL_WEIGHT = 0.5
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_all(values: list[str] | None) -> set[str]:
    return {normalize(value) for value in (values or []) if normalize(value)}


def find_missing_mandatory_skills(job: Job, resume: Resume) -> list[str]:
    candidate_skills = normalize_all(resume.skills)
    return [
        skill
        for skill in (job.mandatory_skills or [])
        if normalize(skill) not in candidate_skills
    ]


def score_skills(job: Job, resume: Resume) -> float:
    weights = {
        normalize(skill): weight
        for skill, weight in (job.skill_weights or {}).items()
    }
    if not weights:
        weights = {skill: 1 for skill in normalize_all(job.required_skills)}

    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 100.0

    candidate_skills = normalize_all(resume.skills)
    matched_weight = sum(
        weight for skill, weight in weights.items() if skill in candidate_skills
    )
    return matched_weight / total_weight * 100.0


def score_experience(job: Job, resume: Resume) -> float:
    required = job.experience_years or 0
    if required <= 0:
        return 100.0

    candidate = resume.experience_years or 0
    return min(candidate / required, 1.0) * 100.0


def score_education(job: Job, resume: Resume) -> float:
    required = EDUCATION_LEVELS.get(job.education_level)
    if required is None:
        return 100.0

    candidate = EDUCATION_LEVELS.get(resume.education_level)
    if candidate is None:
        return 0.0

    return min(candidate / required, 1.0) * 100.0


def calculate_compatibility(job: Job, resume: Resume) -> float:
    total = (
        score_skills(job, resume) * SKILL_WEIGHT
        + score_experience(job, resume) * EXPERIENCE_WEIGHT
        + score_education(job, resume) * EDUCATION_WEIGHT
    )
    return round(total, 2)