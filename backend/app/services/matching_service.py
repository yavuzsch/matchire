from app.models import Job, JobSkill, Resume, SkillRequirement

SKILL_WEIGHT = 0.5
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2

BASE_SCALE = 0.9
OPTIONAL_BONUS = 2
MAX_OPTIONAL_BONUS = 10
FIELD_MISMATCH_PENALTY = 0.7

EDUCATION_LEVELS = {
    "high_school": 1,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "doctorate": 5,
}


def resume_skill_ids(resume: Resume) -> set[int]:
    return {item.skill_id for item in resume.skills}


def job_skills_by_requirement(job: Job, requirement: SkillRequirement) -> list[JobSkill]:
    return [item for item in job.skills if item.requirement == requirement]


def find_missing_mandatory_skills(job: Job, resume: Resume) -> list[str]:
    candidate_ids = resume_skill_ids(resume)

    return [
        item.skill.name
        for item in job_skills_by_requirement(job, SkillRequirement.MANDATORY)
        if item.skill_id not in candidate_ids
    ]


def score_skills(job: Job, resume: Resume) -> float:
    scored = [
        item
        for item in job.skills
        if item.requirement != SkillRequirement.OPTIONAL
    ]

    if not scored:
        return 100.0

    candidate_ids = resume_skill_ids(resume)

    total_weight = sum(item.weight for item in scored)
    matched_weight = sum(
        item.weight for item in scored if item.skill_id in candidate_ids
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

    score = min(candidate / required, 1.0) * 100.0

    if job.field and resume.field and job.field != resume.field:
        score *= FIELD_MISMATCH_PENALTY

    return score


def score_optional(job: Job, resume: Resume) -> float:
    optional = job_skills_by_requirement(job, SkillRequirement.OPTIONAL)

    if not optional:
        return 0.0

    candidate_ids = resume_skill_ids(resume)
    matched = sum(1 for item in optional if item.skill_id in candidate_ids)

    return min(matched * OPTIONAL_BONUS, MAX_OPTIONAL_BONUS)


def calculate_compatibility(job: Job, resume: Resume) -> float:
    base = (
        score_skills(job, resume) * SKILL_WEIGHT
        + score_experience(job, resume) * EXPERIENCE_WEIGHT
        + score_education(job, resume) * EDUCATION_WEIGHT
    )

    total = base * BASE_SCALE + score_optional(job, resume)
    return round(min(total, 100.0), 2)