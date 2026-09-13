from unittest.mock import patch

import pytest

from app.models import Skill, SkillAlias, SkillGroup
from app.services.resume_parser import (
    clean_block,
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


class TestCleanBlock:
    def test_accepts_plain_string(self):
        assert clean_block("  A single line.  ") == "A single line."

    def test_joins_string_list(self):
        assert clean_block(["First", "Second"]) == "First\nSecond"

    def test_joins_dict_list(self):
        value = [
            {"name": "Cargo Tracker", "description": "Unified API layer."},
            {"name": "Pharmacy Finder", "description": "Location based."},
        ]

        assert clean_block(value) == (
            "Cargo Tracker: Unified API layer.\n"
            "Pharmacy Finder: Location based."
        )

    def test_accepts_title_key(self):
        assert clean_block([{"title": "CKAD"}]) == "CKAD"

    def test_keeps_description_without_name(self):
        assert clean_block([{"description": "Only a description."}]) == (
            "Only a description."
        )

    def test_ignores_malformed_items(self):
        assert clean_block(["Valid", 42, None, {}, "  "]) == "Valid"

    def test_returns_none_for_empty(self):
        assert clean_block([]) is None
        assert clean_block(None) is None
        assert clean_block(42) is None


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

    def test_alias_match_is_not_unmatched(self, db, taxonomy):
        skill = db.query(Skill).filter(Skill.name == "Python").first()
        db.add(SkillAlias(alias="Python3", skill_id=skill.id))
        db.commit()

        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"skills": ["Python3"]},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["skill_names"] == ["Python"]
        assert result["unmatched_skills"] == []

    def test_removes_duplicate_resolutions(self, db, taxonomy):
        skill = db.query(Skill).filter(Skill.name == "Python").first()
        db.add(SkillAlias(alias="Python3", skill_id=skill.id))
        db.commit()

        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"skills": ["Python", "Python3"]},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["skill_names"] == ["Python"]
        assert len(result["skill_ids"]) == 1

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

    def test_extracts_project_summary(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"project_summary": "  Built an e-commerce backend.  "},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["project_summary"] == "Built an e-commerce backend."

    def test_missing_project_summary_is_none(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={"skills": ["Python"]},
        ):
            result = parse_resume(db, "cv text", "tr")

        assert result["project_summary"] is None

    def test_accepts_list_projects_and_certifications(self, db, taxonomy):
        with patch(
            "app.services.resume_parser.generate_json",
            return_value={
                "projects": [
                    {"name": "Cargo Tracker", "description": "Unified API layer."},
                    {"name": "Pharmacy Finder", "description": "Location based."},
                ],
                "certifications": ["AWS Certified Developer", "CKAD"],
            },
        ):
            result = parse_resume(db, "cv text", "tr")

        assert "Cargo Tracker: Unified API layer." in result["projects"]
        assert "Pharmacy Finder" in result["projects"]
        assert result["certifications"] == "AWS Certified Developer\nCKAD"