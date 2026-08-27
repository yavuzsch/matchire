from app.models import Job, Resume
from app.services.matching_service import (
    BASE_SCALE,
    calculate_compatibility,
    find_missing_mandatory_skills,
    score_education,
    score_experience,
    score_optional,
    score_skills,
)


def make_job(**kwargs) -> Job:
    defaults = {
        "required_skills": [],
        "mandatory_skills": [],
        "optional_skills": [],
        "skill_weights": {},
        "experience_years": 0,
        "education_level": None,
        "field": None,
    }
    defaults.update(kwargs)
    return Job(**defaults)


def make_resume(**kwargs) -> Resume:
    defaults = {
        "skills": [],
        "experience_years": 0,
        "education_level": None,
        "field": None,
    }
    defaults.update(kwargs)
    return Resume(**defaults)


class TestScoreSkills:
    def test_returns_100_when_job_requires_nothing(self):
        job = make_job()
        resume = make_resume(skills=["Python"])
        assert score_skills(job, resume) == 100.0

    def test_weighted_intersection(self):
        job = make_job(
            required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
            skill_weights={"Python": 3, "FastAPI": 3, "PostgreSQL": 2, "Docker": 1},
        )
        resume = make_resume(skills=["Python", "FastAPI", "PostgreSQL"])
        assert round(score_skills(job, resume), 2) == 88.89

    def test_falls_back_to_equal_weights(self):
        job = make_job(required_skills=["Python", "Java"])
        resume = make_resume(skills=["Python"])
        assert score_skills(job, resume) == 50.0

    def test_is_case_insensitive(self):
        job = make_job(required_skills=["Python"], skill_weights={"Python": 1})
        resume = make_resume(skills=["  python  "])
        assert score_skills(job, resume) == 100.0


class TestScoreExperience:
    def test_returns_100_when_no_requirement(self):
        assert score_experience(make_job(), make_resume()) == 100.0

    def test_partial_experience(self):
        job = make_job(experience_years=4)
        resume = make_resume(experience_years=1)
        assert score_experience(job, resume) == 25.0

    def test_caps_at_100(self):
        job = make_job(experience_years=2)
        resume = make_resume(experience_years=10)
        assert score_experience(job, resume) == 100.0


class TestScoreEducation:
    def test_returns_100_when_no_requirement(self):
        assert score_education(make_job(), make_resume()) == 100.0

    def test_returns_0_when_candidate_has_none(self):
        job = make_job(education_level="bachelor")
        assert score_education(job, make_resume()) == 0.0

    def test_exact_match(self):
        job = make_job(education_level="bachelor")
        resume = make_resume(education_level="bachelor")
        assert score_education(job, resume) == 100.0

    def test_higher_level_still_full_score(self):
        job = make_job(education_level="bachelor")
        resume = make_resume(education_level="doctorate")
        assert score_education(job, resume) == 100.0

    def test_lower_level_partial(self):
        job = make_job(education_level="doctorate")
        resume = make_resume(education_level="bachelor")
        assert score_education(job, resume) == 60.0

    def test_field_mismatch_penalty(self):
        job = make_job(education_level="bachelor", field="software_development")
        resume = make_resume(education_level="bachelor", field="data_science")
        assert score_education(job, resume) == 70.0


class TestScoreOptional:
    def test_returns_0_when_no_optional_skills(self):
        assert score_optional(make_job(), make_resume()) == 0.0

    def test_two_points_per_match(self):
        job = make_job(optional_skills=["Docker", "AWS"])
        resume = make_resume(skills=["Docker", "AWS"])
        assert score_optional(job, resume) == 4.0

    def test_caps_at_10(self):
        job = make_job(optional_skills=["A", "B", "C", "D", "E", "F", "G"])
        resume = make_resume(skills=["A", "B", "C", "D", "E", "F", "G"])
        assert score_optional(job, resume) == 10.0


class TestMandatorySkills:
    def test_no_missing_when_candidate_has_all(self):
        job = make_job(mandatory_skills=["Python"])
        resume = make_resume(skills=["Python"])
        assert find_missing_mandatory_skills(job, resume) == []

    def test_reports_missing(self):
        job = make_job(mandatory_skills=["Python", "Java"])
        resume = make_resume(skills=["Python"])
        assert find_missing_mandatory_skills(job, resume) == ["Java"]


class TestCalculateCompatibility:
    def test_perfect_candidate_without_bonus(self):
        job = make_job(
            required_skills=["Python"],
            skill_weights={"Python": 1},
            experience_years=2,
            education_level="bachelor",
        )
        resume = make_resume(
            skills=["Python"],
            experience_years=2,
            education_level="bachelor",
        )
        assert calculate_compatibility(job, resume) == round(100 * BASE_SCALE, 2)

    def test_bonus_lifts_score(self):
        job = make_job(
            required_skills=["Python"],
            skill_weights={"Python": 1},
            optional_skills=["Docker"],
            experience_years=2,
            education_level="bachelor",
        )
        resume = make_resume(
            skills=["Python", "Docker"],
            experience_years=2,
            education_level="bachelor",
        )
        assert calculate_compatibility(job, resume) == round(100 * BASE_SCALE + 2, 2)

    def test_never_exceeds_100(self):
        job = make_job(
            required_skills=["Python"],
            skill_weights={"Python": 1},
            optional_skills=["A", "B", "C", "D", "E"],
            experience_years=1,
            education_level="bachelor",
        )
        resume = make_resume(
            skills=["Python", "A", "B", "C", "D", "E"],
            experience_years=5,
            education_level="doctorate",
        )
        assert calculate_compatibility(job, resume) <= 100.0