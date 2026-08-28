import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import time

from app.prompts.taxonomy import GROUPS_TEMPLATE, SKILLS_TEMPLATE
from app.services.llm_client import LLMUnavailableError, generate_json

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "taxonomy.json"

MIN_ENTRIES = 30
MAX_ENTRIES = 60
DELAY_SECONDS = 2


def generate_groups() -> list[dict]:
    result = generate_json(GROUPS_TEMPLATE)
    if not isinstance(result, list):
        return []

    groups = []
    for item in result:
        key = (item.get("key") or "").strip()
        labels = item.get("labels") or {}
        description = (item.get("description") or "").strip()

        if key and labels:
            groups.append({"key": key, "labels": labels, "description": description})

    return groups


def generate_skills(group: dict) -> list[dict]:
    prompt = SKILLS_TEMPLATE.format(
        group=group["key"],
        description=group["description"],
        minimum=MIN_ENTRIES,
        maximum=MAX_ENTRIES,
    )

    result = generate_json(prompt)
    return result if isinstance(result, list) else []


def run():
    print("generating groups...")

    try:
        groups = generate_groups()
    except LLMUnavailableError as error:
        print(f"failed: {error}")
        return

    if not groups:
        print("no groups returned")
        return

    print(f"{len(groups)} groups")
    print()

    skills = []
    seen = set()

    for position, group in enumerate(groups, start=1):
        try:
            entries = generate_skills(group)
        except LLMUnavailableError as error:
            print(f"{group['key']}: failed ({error})")
            continue

        added = 0

        for entry in entries:
            name = (entry.get("name") or "").strip()
            if not name:
                continue

            key = name.lower()
            if key in seen:
                continue

            seen.add(key)
            skills.append(
                {
                    "name": name,
                    "group": group["key"],
                    "aliases": [
                        alias.strip()
                        for alias in entry.get("aliases", [])
                        if alias and alias.strip()
                    ],
                    "source": "llm",
                }
            )
            added += 1

        print(f"{position:2}/{len(groups)}  {group['key']:24} {added:3} entries")
        time.sleep(DELAY_SECONDS)

    output = {
        "groups": [
            {"key": group["key"], "labels": group["labels"]} for group in groups
        ],
        "skills": skills,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print(f"groups: {len(groups)}  skills: {len(skills)}")
    print(f"written to {OUTPUT_PATH}")


if __name__ == "__main__":
    run()