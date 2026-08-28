import pytest

from app.models import (
    Job,
    JobSkill,
    Resume,
    Skill,
    SkillGroup,
    SkillRequirement,
    User,
    UserRole,
)
from app.services.matching_service import (
    BASE_SCALE,
    calculate_compatibility,
    find_missing_mandatory_skills,
    score_education,
    score_experience,
    score_optional,
    score_skills,
)


@pytest.fixture
def group(db):
    item = SkillGroup(key="frontend", position=0)
    db.add(item)
    db.commit()
    return item


@pytest.fixture
def skills(db, group):
    names = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis"]
    created = {}

    for name in names:
        skill = Skill(name=name, group_id=group.id, source="llm")
        db.add(skill)
        db.flush()
        created[name] = skill

    db.commit()
    return created


@pytest.fixture
def employer(db):
    user = User(
        email="employer@test.com",
        hashed_password="x",
        full_name="Employer",
        role=UserRole.EMPLOYER,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def candidate(db):
    user = User(
        email="candidate@test.com",
        hashed_password="x",
        full_name="Candidate",
        role=UserRole.CANDIDATE,
    )
    db.add(user)
    db.commit()
    return user


def make_job(db, employer, skills=None, **kwargs):
    defaults = {
        "employer_id": employer.id,
        "title": "Backend Developer",
        "company_name": "Test AS",
        "experience_years": 0,
        "education_level": None,
        "field": None,
    }
    defaults.update(kwargs)

    job = Job(**defaults)
    db.add(job)
    db.flush()

    for skill, requirement, weight in skills or []:
        db.add(
            JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                requirement=requirement,
                weight=weight,
            )
        )

    db.commit()
    db.refresh(job)
    return job


def make_resume(db, candidate, skills=None, **kwargs):
    from app.models import ResumeSkill

    defaults = {
        "candidate_id": candidate.id,
        "experience_years": 0,
        "education_level": None,
        "field": None,
    }
    defaults.update(kwargs)

    resume = Resume(**defaults)
    db.add(resume)
    db.flush()

    for skill in skills or []:
        db.add(ResumeSkill(resume_id=resume.id, skill_id=skill.id))

    db.commit()
    db.refresh(resume)
    return resume


class TestScoreSkills:
    def test_returns_100_when_job_requires_nothing(self, db, employer, candidate, skills):
        job = make_job(db, employer)
        resume = make_resume(db, candidate, [skills["Python"]])

        assert score_skills(job, resume) == 100.0

    def test_weighted_intersection(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.REQUIRED, 3),
                (skills["FastAPI"], SkillRequirement.REQUIRED, 3),
                (skills["PostgreSQL"], SkillRequirement.REQUIRED, 2),
                (skills["Docker"], SkillRequirement.REQUIRED, 1),
            ],
        )
        resume = make_resume(
            db,
            candidate,
            [skills["Python"], skills["FastAPI"], skills["PostgreSQL"]],
        )

        assert round(score_skills(job, resume), 2) == 88.89

    def test_mandatory_counts_toward_score(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.MANDATORY, 1),
                (skills["FastAPI"], SkillRequirement.REQUIRED, 1),
            ],
        )
        resume = make_resume(db, candidate, [skills["Python"]])

        assert score_skills(job, resume) == 50.0

    def test_optional_excluded_from_score(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.REQUIRED, 1),
                (skills["Docker"], SkillRequirement.OPTIONAL, 1),
            ],
        )
        resume = make_resume(db, candidate, [skills["Python"]])

        assert score_skills(job, resume) == 100.0


class TestScoreExperience:
    def test_returns_100_when_no_requirement(self, db, employer, candidate):
        job = make_job(db, employer)
        resume = make_resume(db, candidate)

        assert score_experience(job, resume) == 100.0

    def test_partial_experience(self, db, employer, candidate):
        job = make_job(db, employer, experience_years=4)
        resume = make_resume(db, candidate, experience_years=1)

        assert score_experience(job, resume) == 25.0

    def test_caps_at_100(self, db, employer, candidate):
        job = make_job(db, employer, experience_years=2)
        resume = make_resume(db, candidate, experience_years=10)

        assert score_experience(job, resume) == 100.0


class TestScoreEducation:
    def test_returns_100_when_no_requirement(self, db, employer, candidate):
        job = make_job(db, employer)
        resume = make_resume(db, candidate)

        assert score_education(job, resume) == 100.0

    def test_returns_0_when_candidate_has_none(self, db, employer, candidate):
        job = make_job(db, employer, education_level="bachelor")
        resume = make_resume(db, candidate)

        assert score_education(job, resume) == 0.0

    def test_exact_match(self, db, employer, candidate):
        job = make_job(db, employer, education_level="bachelor")
        resume = make_resume(db, candidate, education_level="bachelor")

        assert score_education(job, resume) == 100.0

    def test_higher_level_still_full_score(self, db, employer, candidate):
        job = make_job(db, employer, education_level="bachelor")
        resume = make_resume(db, candidate, education_level="doctorate")

        assert score_education(job, resume) == 100.0

    def test_lower_level_partial(self, db, employer, candidate):
        job = make_job(db, employer, education_level="doctorate")
        resume = make_resume(db, candidate, education_level="bachelor")

        assert score_education(job, resume) == 60.0

    def test_field_mismatch_penalty(self, db, employer, candidate):
        job = make_job(
            db, employer, education_level="bachelor", field="software_development"
        )
        resume = make_resume(
            db, candidate, education_level="bachelor", field="data_science"
        )

        assert score_education(job, resume) == 70.0


class TestScoreOptional:
    def test_returns_0_when_no_optional_skills(self, db, employer, candidate, skills):
        job = make_job(db, employer, [(skills["Python"], SkillRequirement.REQUIRED, 1)])
        resume = make_resume(db, candidate, [skills["Python"]])

        assert score_optional(job, resume) == 0.0

    def test_two_points_per_match(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Docker"], SkillRequirement.OPTIONAL, 1),
                (skills["AWS"], SkillRequirement.OPTIONAL, 1),
            ],
        )
        resume = make_resume(db, candidate, [skills["Docker"], skills["AWS"]])

        assert score_optional(job, resume) == 4.0

    def test_counts_only_matched(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Docker"], SkillRequirement.OPTIONAL, 1),
                (skills["AWS"], SkillRequirement.OPTIONAL, 1),
            ],
        )
        resume = make_resume(db, candidate, [skills["Docker"]])

        assert score_optional(job, resume) == 2.0


class TestMandatorySkills:
    def test_no_missing_when_candidate_has_all(self, db, employer, candidate, skills):
        job = make_job(db, employer, [(skills["Python"], SkillRequirement.MANDATORY, 1)])
        resume = make_resume(db, candidate, [skills["Python"]])

        assert find_missing_mandatory_skills(job, resume) == []

    def test_reports_missing(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.MANDATORY, 1),
                (skills["Redis"], SkillRequirement.MANDATORY, 1),
            ],
        )
        resume = make_resume(db, candidate, [skills["Python"]])

        assert find_missing_mandatory_skills(job, resume) == ["Redis"]

    def test_ignores_non_mandatory(self, db, employer, candidate, skills):
        job = make_job(db, employer, [(skills["Redis"], SkillRequirement.REQUIRED, 1)])
        resume = make_resume(db, candidate)

        assert find_missing_mandatory_skills(job, resume) == []


class TestCalculateCompatibility:
    def test_perfect_candidate_without_bonus(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [(skills["Python"], SkillRequirement.REQUIRED, 1)],
            experience_years=2,
            education_level="bachelor",
        )
        resume = make_resume(
            db,
            candidate,
            [skills["Python"]],
            experience_years=2,
            education_level="bachelor",
        )

        assert calculate_compatibility(job, resume) == round(100 * BASE_SCALE, 2)

    def test_bonus_lifts_score(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.REQUIRED, 1),
                (skills["Docker"], SkillRequirement.OPTIONAL, 1),
            ],
            experience_years=2,
            education_level="bachelor",
        )
        resume = make_resume(
            db,
            candidate,
            [skills["Python"], skills["Docker"]],
            experience_years=2,
            education_level="bachelor",
        )

        assert calculate_compatibility(job, resume) == round(100 * BASE_SCALE + 2, 2)

    def test_never_exceeds_100(self, db, employer, candidate, skills):
        job = make_job(
            db,
            employer,
            [
                (skills["Python"], SkillRequirement.REQUIRED, 1),
                (skills["Docker"], SkillRequirement.OPTIONAL, 1),
                (skills["AWS"], SkillRequirement.OPTIONAL, 1),
                (skills["Redis"], SkillRequirement.OPTIONAL, 1),
                (skills["FastAPI"], SkillRequirement.OPTIONAL, 1),
                (skills["PostgreSQL"], SkillRequirement.OPTIONAL, 1),
            ],
            experience_years=1,
            education_level="bachelor",
        )
        resume = make_resume(
            db,
            candidate,
            list(skills.values()),
            experience_years=5,
            education_level="doctorate",
        )

        assert calculate_compatibility(job, resume) <= 100.0