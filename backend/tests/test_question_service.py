from unittest.mock import patch

import pytest

from app.models import Job
from app.services.llm_client import LLMUnavailableError
from app.services.question_service import QUESTION_COUNT, build_prompt, generate_questions


def make_job(**kwargs) -> Job:
    defaults = {
        "title": "Backend Developer",
        "required_skills": ["Python", "FastAPI"],
        "experience_years": 3,
        "language": "tr",
    }
    defaults.update(kwargs)
    return Job(**defaults)


class TestBuildPrompt:
    def test_includes_job_details(self):
        prompt = build_prompt(make_job())

        assert "Backend Developer" in prompt
        assert "Python, FastAPI" in prompt
        assert "3" in prompt
        assert str(QUESTION_COUNT) in prompt

    def test_handles_empty_skills(self):
        prompt = build_prompt(make_job(required_skills=[]))

        assert "-" in prompt

    def test_does_not_leak_company_name(self):
        job = make_job()
        job.company_name = "Secret Company"

        assert "Secret Company" not in build_prompt(job)


class TestGenerateQuestions:
    def test_returns_cleaned_list(self):
        with patch(
            "app.services.question_service.generate_json",
            return_value=["  Question 1  ", "Question 2"],
        ):
            assert generate_questions(make_job()) == ["Question 1", "Question 2"]

    def test_drops_empty_entries(self):
        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1", "", "   "],
        ):
            assert generate_questions(make_job()) == ["Question 1"]

    def test_returns_empty_when_response_is_not_a_list(self):
        with patch(
            "app.services.question_service.generate_json",
            return_value={"questions": ["Question"]},
        ):
            assert generate_questions(make_job()) == []

    def test_propagates_llm_error(self):
        with patch(
            "app.services.question_service.generate_json",
            side_effect=LLMUnavailableError("503"),
        ):
            with pytest.raises(LLMUnavailableError):
                generate_questions(make_job())