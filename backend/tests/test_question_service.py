from unittest.mock import patch

import pytest

from app.models import Job, JobSkill, Skill, SkillGroup, SkillRequirement, User, UserRole
from app.services.llm_client import LLMUnavailableError
from app.services.question_service import QUESTION_COUNT, build_prompt, generate_questions


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
def prompt_skills(db):
    group = SkillGroup(key="backend", position=0)
    db.add(group)
    db.flush()

    created = {}

    for name in ["Python", "FastAPI"]:
        skill = Skill(name=name, group_id=group.id, source="llm")
        db.add(skill)
        db.flush()
        created[name] = skill

    db.commit()
    return created


def make_job(db, employer, skill_items=None, **kwargs) -> Job:
    defaults = {
        "employer_id": employer.id,
        "title": "Backend Developer",
        "company_name": "Test AS",
        "experience_years": 3,
        "language": "tr",
    }
    defaults.update(kwargs)

    job = Job(**defaults)
    db.add(job)
    db.flush()

    for skill, requirement in skill_items or []:
        db.add(
            JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                requirement=requirement,
                weight=1,
            )
        )

    db.commit()
    db.refresh(job)
    return job


class TestBuildPrompt:
    def test_includes_job_details(self, db, employer, prompt_skills):
        job = make_job(
            db,
            employer,
            [
                (prompt_skills["Python"], SkillRequirement.REQUIRED),
                (prompt_skills["FastAPI"], SkillRequirement.REQUIRED),
            ],
        )

        prompt = build_prompt(job)

        assert "Backend Developer" in prompt
        assert "Python" in prompt
        assert "FastAPI" in prompt
        assert "3" in prompt
        assert str(QUESTION_COUNT) in prompt

    def test_handles_empty_skills(self, db, employer):
        prompt = build_prompt(make_job(db, employer))

        assert "-" in prompt

    def test_excludes_optional_skills(self, db, employer, prompt_skills):
        job = make_job(
            db,
            employer,
            [
                (prompt_skills["Python"], SkillRequirement.REQUIRED),
                (prompt_skills["FastAPI"], SkillRequirement.OPTIONAL),
            ],
        )

        prompt = build_prompt(job)

        assert "Python" in prompt
        assert "FastAPI" not in prompt

    def test_does_not_leak_company_name(self, db, employer):
        job = make_job(db, employer, company_name="Secret Company")

        assert "Secret Company" not in build_prompt(job)


class TestGenerateQuestions:
    def test_returns_cleaned_list(self, db, employer):
        job = make_job(db, employer)

        with patch(
            "app.services.question_service.generate_json",
            return_value=["  Question 1  ", "Question 2"],
        ):
            assert generate_questions(job) == ["Question 1", "Question 2"]

    def test_drops_empty_entries(self, db, employer):
        job = make_job(db, employer)

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1", "", "   "],
        ):
            assert generate_questions(job) == ["Question 1"]

    def test_returns_empty_when_response_is_not_a_list(self, db, employer):
        job = make_job(db, employer)

        with patch(
            "app.services.question_service.generate_json",
            return_value={"questions": ["Question"]},
        ):
            assert generate_questions(job) == []

    def test_propagates_llm_error(self, db, employer):
        job = make_job(db, employer)

        with patch(
            "app.services.question_service.generate_json",
            side_effect=LLMUnavailableError("503"),
        ):
            with pytest.raises(LLMUnavailableError):
                generate_questions(job)