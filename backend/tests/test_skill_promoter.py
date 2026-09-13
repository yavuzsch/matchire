from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.models import Skill, SkillAlias, SkillGroup, SkillGroupLabel, UnknownSkill, User, UserRole
from app.services.skill_promoter import (
    DAILY_LIMIT,
    SkillLimitError,
    SkillRejectedError,
    count_today,
    promote,
)


@pytest.fixture
def group(db):
    item = SkillGroup(key="backend_frameworks", position=0)
    db.add(item)
    db.flush()
    db.add(SkillGroupLabel(group_id=item.id, language="tr", label="Backend"))
    db.commit()
    return item


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


def make_skill(db, group, name, aliases=None):
    skill = Skill(name=name, group_id=group.id, source="llm")
    db.add(skill)
    db.flush()

    for alias in aliases or []:
        db.add(SkillAlias(alias=alias, skill_id=skill.id))

    db.commit()
    return skill


def accepted(name, group_key="backend_frameworks", aliases=None):
    return {
        "accepted": True,
        "name": name,
        "group": group_key,
        "aliases": aliases or [],
        "reason": "",
    }


class TestExistingSkill:
    def test_returns_existing_without_llm_call(self, db, group, candidate):
        existing = make_skill(db, group, "React")

        with patch("app.services.skill_promoter.generate_json") as mock_llm:
            result = promote(db, "React", candidate)

        assert result.id == existing.id
        mock_llm.assert_not_called()

    def test_adds_alias_for_known_variant(self, db, group, candidate):
        existing = make_skill(db, group, "React", aliases=["ReactJS"])

        with patch("app.services.skill_promoter.generate_json") as mock_llm:
            result = promote(db, "reactjs", candidate)

        assert result.id == existing.id
        mock_llm.assert_not_called()

    def test_creates_alias_when_llm_maps_to_existing(self, db, group, candidate):
        existing = make_skill(db, group, ".NET")

        with patch(
            "app.services.skill_promoter.generate_json",
            return_value=accepted(".NET"),
        ):
            result = promote(db, "dotnet core", candidate)
        db.commit()

        assert result.id == existing.id
        assert db.query(Skill).count() == 1

        aliases = {alias.alias.lower() for alias in existing.aliases}
        assert "dotnet core" in aliases


class TestAcceptedSkill:
    def test_creates_unverified_skill(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value=accepted("Unity", aliases=["Unity3D"]),
        ):
            skill = promote(db, "unity", candidate)
        db.commit()

        assert skill.name == "Unity"
        assert skill.is_verified is False
        assert skill.source == "user"
        assert skill.created_by == candidate.id

    def test_stores_aliases_and_original_term(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value=accepted("Unity", aliases=["Unity3D"]),
        ):
            skill = promote(db, "unity engine", candidate)
        db.commit()

        aliases = {alias.alias.lower() for alias in skill.aliases}
        assert "unity3d" in aliases
        assert "unity engine" in aliases


class TestRejectedSkill:
    def test_rejected_term_raises(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value={"accepted": False, "reason": "misspelling"},
        ):
            with pytest.raises(SkillRejectedError):
                promote(db, "Pyhton", candidate)

    def test_rejected_term_is_recorded(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value={"accepted": False, "reason": "misspelling"},
        ):
            with pytest.raises(SkillRejectedError):
                promote(db, "Pyhton", candidate)

        db.commit()
        assert db.query(UnknownSkill).count() == 1

    def test_unknown_group_is_rejected(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value=accepted("Unity", group_key="game_development"),
        ):
            with pytest.raises(SkillRejectedError):
                promote(db, "unity", candidate)

    def test_non_dict_response_is_rejected(self, db, group, candidate):
        with patch(
            "app.services.skill_promoter.generate_json",
            return_value=["unexpected"],
        ):
            with pytest.raises(SkillRejectedError):
                promote(db, "something", candidate)

    def test_empty_term_is_rejected(self, db, group, candidate):
        with pytest.raises(SkillRejectedError):
            promote(db, "   ", candidate)


class TestDailyLimit:
    def _create_user_skills(self, db, group, candidate, count):
        for index in range(count):
            db.add(
                Skill(
                    name=f"Skill {index}",
                    group_id=group.id,
                    source="user",
                    is_verified=False,
                    created_by=candidate.id,
                )
            )
        db.commit()

    def test_counts_only_recent(self, db, group, candidate):
        self._create_user_skills(db, group, candidate, 2)

        assert count_today(db, candidate) == 2

    def test_blocks_after_limit(self, db, group, candidate):
        self._create_user_skills(db, group, candidate, DAILY_LIMIT)

        with patch("app.services.skill_promoter.generate_json") as mock_llm:
            with pytest.raises(SkillLimitError):
                promote(db, "Unity", candidate)

        mock_llm.assert_not_called()

    def test_existing_skill_ignores_limit(self, db, group, candidate):
        make_skill(db, group, "React")
        self._create_user_skills(db, group, candidate, DAILY_LIMIT)

        result = promote(db, "React", candidate)

        assert result.name == "React"