from unittest.mock import patch

import pytest

from app.models import Skill, SkillGroup
from app.services.resume_parser import (
    clean_choice,
    clean_experience,
    clean_text,
    parse_resume,
)


@pytest.fixture
def taxonomy(db):
    group = SkillGroup(key="backend", position=0)
    db.add(group)
    db.flush()

    for name in ["Python", "Django", "Docker"]:
        db.add(Skill(name=name, group_id=group.id, source="llm"))

    db.commit()


class TestCleanHelpers:
    def test_clean_text_strips(self):
        assert clean_text("  Istanbul  ") == "Istanbul"

    def test_clean_text_rejects_empty(self):
        assert clean_text("   ") is None
        assert clean_text(None) is None
        assert clean_text(42) is None

    def test_clean_choice_accepts_known(self):
        assert clean_choice("bachelor", {"bachelor", "master"}) == "bachelor"

    def test_clean_choice_rejects_unknown(self):
        assert clean_choice("university", {"bachelor"}) is None

    def test_clean_experience_clamps(self):
        assert clean_experience(3) == 3
        assert clean_experience(-5) == 0
        assert clean_experience(200) == 50

    def test_clean_experience_handles_garbage(self):
        assert clean_experience("three") == 0
        assert clean_experience(None) == 0


class TestParseResume:
    def test_resolves_known_skills(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={
                "skills": ["Python", "Django", "Svelte"],
                "experience_years": 2,
                "education_level": "bachelor",
            },
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["skill_names"] == ["Python", "Django"]
        assert result["unmatched_skills"] == ["Svelte"]
        assert len(result["skill_ids"]) == 2

    def test_rejects_invalid_education_level(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"education_level": "university"},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["education_level"] is None

    def test_rejects_invalid_field(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"field": "accounting"},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["field"] is None

    def test_handles_non_dict_response(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value=["unexpected"],
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["skill_ids"] == []
        assert result["experience_years"] == 0

    def test_ignores_non_string_skills(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"skills": ["Python", 42, None, "  "]},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["skill_names"] == ["Python"]