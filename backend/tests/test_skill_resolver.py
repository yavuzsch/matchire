import pytest

from app.models import Skill, SkillAlias, SkillGroup, UnknownSkill
from app.services.skill_resolver import (
    normalize,
    record_unknown,
    resolve,
    resolve_many,
)


@pytest.fixture
def group(db):
    item = SkillGroup(key="frontend", position=0)
    db.add(item)
    db.commit()
    return item


def make_skill(db, group, name, aliases=None, deprecated=False):
    skill = Skill(
        name=name,
        group_id=group.id,
        source="llm",
        is_deprecated=deprecated,
    )
    db.add(skill)
    db.commit()

    for alias in aliases or []:
        db.add(SkillAlias(alias=alias, skill_id=skill.id))

    db.commit()
    return skill


class TestNormalize:
    def test_strips_punctuation_and_case(self):
        assert normalize("React.js") == "reactjs"
        assert normalize("  REACT JS  ") == "reactjs"
        assert normalize("Node.js") == "nodejs"

    def test_empty_input(self):
        assert normalize("") == ""
        assert normalize(None) == ""


class TestResolve:
    def test_exact_match(self, db, group):
        skill = make_skill(db, group, "React")

        assert resolve(db, "React").id == skill.id

    def test_case_insensitive(self, db, group):
        skill = make_skill(db, group, "React")

        assert resolve(db, "react").id == skill.id

    def test_alias_match(self, db, group):
        skill = make_skill(db, group, "React", aliases=["ReactJS"])

        assert resolve(db, "ReactJS").id == skill.id

    def test_normalized_match(self, db, group):
        skill = make_skill(db, group, "Node.js")

        assert resolve(db, "node js").id == skill.id
        assert resolve(db, "NODEJS").id == skill.id

    def test_does_not_match_different_normalized_form(self, db, group):
        make_skill(db, group, "React")

        assert resolve(db, "react.js") is None

    def test_returns_none_for_unknown(self, db, group):
        make_skill(db, group, "React")

        assert resolve(db, "Svelte") is None

    def test_ignores_deprecated(self, db, group):
        make_skill(db, group, "Backbone", deprecated=True)

        assert resolve(db, "Backbone") is None

    def test_empty_input(self, db, group):
        assert resolve(db, "") is None
        assert resolve(db, "   ") is None

    def test_finds_unverified_skill(self, db, group):
            skill = Skill(
                name="Unity",
                group_id=group.id,
                source="user",
                is_verified=False,
            )
            db.add(skill)
            db.commit()

            assert resolve(db, "Unity").id == skill.id


class TestRecordUnknown:
    def test_creates_entry(self, db):
        record_unknown(db, "Svelte")
        db.commit()

        entry = db.query(UnknownSkill).one()
        assert entry.raw_text == "Svelte"
        assert entry.normalized_text == "svelte"
        assert entry.seen_count == 1

    def test_increments_existing(self, db):
        record_unknown(db, "Svelte")
        db.commit()
        record_unknown(db, "svelte.js")
        db.commit()

        entries = db.query(UnknownSkill).all()
        assert len(entries) == 2

    def test_increments_same_normalized(self, db):
        record_unknown(db, "Svelte")
        db.commit()
        record_unknown(db, "SVELTE")
        db.commit()

        entry = db.query(UnknownSkill).one()
        assert entry.seen_count == 2

    def test_ignores_empty(self, db):
        record_unknown(db, "   ")
        db.commit()

        assert db.query(UnknownSkill).count() == 0


class TestResolveMany:
    def test_resolves_known_and_records_unknown(self, db, group):
        make_skill(db, group, "React", aliases=["ReactJS"])
        make_skill(db, group, "Vue")

        resolved = resolve_many(db, ["react", "ReactJS", "Vue", "Svelte"])
        db.commit()

        names = [skill.name for skill in resolved]
        assert names == ["React", "Vue"]
        assert db.query(UnknownSkill).count() == 1

    def test_handles_empty_list(self, db):
        assert resolve_many(db, []) == []
        assert resolve_many(db, None) == []