from unittest.mock import patch

import pytest

from app.models import Skill, SkillGroup, UnknownSkill
from app.services.job_parser import MAX_SKILLS, parse_job


@pytest.fixture
def taxonomy(db):
    group = SkillGroup(key="backend", position=0)
    db.add(group)
    db.flush()

    for name in ["Python", "Django", "Docker", "Redis"]:
        db.add(Skill(name=name, group_id=group.id, source="llm"))

    db.commit()


def response(skills=None, **overrides):
    payload = {
        "title": "Backend Developer",
        "company_name": "Test AS",
        "location": "Istanbul",
        "description": "We are hiring",
        "skills": skills if skills is not None else [],
        "experience_years": 3,
        "education_level": "bachelor",
        "field": "software_development",
    }
    payload.update(overrides)
    return payload


class TestBasicFields:
    def test_extracts_plain_fields(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(),
        ):
            result = parse_job(db, "job text", "tr")

        assert result["title"] == "Backend Developer"
        assert result["company_name"] == "Test AS"
        assert result["location"] == "Istanbul"
        assert result["experience_years"] == 3
        assert result["education_level"] == "bachelor"
        assert result["field"] == "software_development"

    def test_rejects_invalid_education_level(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(education_level="university"),
        ):
            result = parse_job(db, "job text", "tr")

        assert result["education_level"] is None

    def test_rejects_invalid_field(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(field="accounting"),
        ):
            result = parse_job(db, "job text", "tr")

        assert result["field"] is None

    def test_clamps_experience(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(experience_years=200),
        ):
            result = parse_job(db, "job text", "tr")

        assert result["experience_years"] == 50

    def test_handles_non_dict_response(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=["unexpected"],
        ):
            result = parse_job(db, "job text", "tr")

        assert result["title"] is None
        assert result["skills"] == []


class TestSkills:
    def test_resolves_known_skills(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[
                    {"name": "Python", "requirement": "mandatory"},
                    {"name": "Docker", "requirement": "optional"},
                ]
            ),
        ):
            result = parse_job(db, "job text", "tr")

        names = [item["name"] for item in result["skills"]]
        assert names == ["Python", "Docker"]

    def test_assigns_weight_by_requirement(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[
                    {"name": "Python", "requirement": "mandatory"},
                    {"name": "Django", "requirement": "required"},
                    {"name": "Docker", "requirement": "optional"},
                ]
            ),
        ):
            result = parse_job(db, "job text", "tr")

        weights = {item["name"]: item["weight"] for item in result["skills"]}
        assert weights == {"Python": 3, "Django": 2, "Docker": 1}

    def test_defaults_unknown_requirement(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[{"name": "Python", "requirement": "nice to have"}]
            ),
        ):
            result = parse_job(db, "job text", "tr")

        assert result["skills"][0]["requirement"] == "required"
        assert result["skills"][0]["weight"] == 2

    def test_records_unmatched_skills(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[
                    {"name": "Python", "requirement": "required"},
                    {"name": "Svelte", "requirement": "required"},
                ]
            ),
        ):
            result = parse_job(db, "job text", "tr")
        db.commit()

        assert result["unmatched_skills"] == ["Svelte"]
        assert db.query(UnknownSkill).count() == 1

    def test_removes_duplicates(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[
                    {"name": "Python", "requirement": "mandatory"},
                    {"name": "python", "requirement": "optional"},
                ]
            ),
        ):
            result = parse_job(db, "job text", "tr")

        assert len(result["skills"]) == 1
        assert result["skills"][0]["requirement"] == "mandatory"

    def test_caps_skill_count(self, db, taxonomy):
        entries = [
            {"name": f"Skill {index}", "requirement": "required"}
            for index in range(MAX_SKILLS + 5)
        ]

        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(skills=entries),
        ):
            result = parse_job(db, "job text", "tr")
        db.commit()

        assert len(result["unmatched_skills"]) == MAX_SKILLS

    def test_ignores_malformed_entries(self, db, taxonomy):
        with patch(
            "app.services.job_parser.generate_json",
            return_value=response(
                skills=[
                    {"name": "Python", "requirement": "required"},
                    "not a dict",
                    {"requirement": "required"},
                    {"name": "   ", "requirement": "required"},
                ]
            ),
        ):
            result = parse_job(db, "job text", "tr")

        assert len(result["skills"]) == 1