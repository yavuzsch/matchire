import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

from app.core.database import SessionLocal
from app.models import Skill, SkillAlias, SkillGroup, SkillGroupLabel

BASE_DIR = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = BASE_DIR / "data" / "taxonomy.json"


def run():
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()

    groups = {}

    for position, item in enumerate(data["groups"]):
        group = db.query(SkillGroup).filter(SkillGroup.key == item["key"]).first()

        if group is None:
            group = SkillGroup(key=item["key"], position=position)
            db.add(group)
            db.flush()
        else:
            group.position = position

        existing = {label.language: label for label in group.labels}

        for language, text in item["labels"].items():
            if language in existing:
                existing[language].label = text
            else:
                db.add(
                    SkillGroupLabel(group_id=group.id, language=language, label=text)
                )

        groups[item["key"]] = group

    db.commit()

    seen_names = set()
    added = 0
    updated = 0

    for item in data["skills"]:
        group = groups.get(item["group"])
        if group is None:
            continue

        seen_names.add(item["name"].lower())
        skill = db.query(Skill).filter(Skill.name.ilike(item["name"])).first()

        if skill is None:
            skill = Skill(
                name=item["name"],
                group_id=group.id,
                source=item.get("source", "llm"),
            )
            db.add(skill)
            db.flush()
            added += 1
        else:
            skill.group_id = group.id
            skill.is_deprecated = False
            updated += 1

        existing_aliases = {alias.alias.lower() for alias in skill.aliases}

        for alias in item.get("aliases", []):
            if alias.lower() in existing_aliases:
                continue
            if db.query(SkillAlias).filter(SkillAlias.alias.ilike(alias)).first():
                continue
            db.add(SkillAlias(alias=alias, skill_id=skill.id))

    deprecated = 0

    for skill in db.query(Skill).all():
        if skill.name.lower() not in seen_names and not skill.is_deprecated:
            skill.is_deprecated = True
            deprecated += 1

    db.commit()

    total = db.query(Skill).count()
    alias_count = db.query(SkillAlias).count()

    db.close()

    print(f"groups: {len(groups)}")
    print(f"added: {added}  updated: {updated}  deprecated: {deprecated}")
    print(f"total skills: {total}  aliases: {alias_count}")


if __name__ == "__main__":
    run()