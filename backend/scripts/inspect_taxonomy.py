import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PATH = BASE_DIR / "data" / "taxonomy.json"


def run():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    groups = {g["key"]: g["labels"] for g in data["groups"]}
    counter = Counter(s["group"] for s in data["skills"])

    print(f"groups: {len(groups)}  skills: {len(data['skills'])}")
    print()

    for key, labels in groups.items():
        tr = labels.get("tr", "")
        en = labels.get("en", "")
        print(f"{counter[key]:3}  {key:24} {tr:28} {en}")

    print()
    print("sample entries:")
    for skill in data["skills"][:20]:
        aliases = ", ".join(skill["aliases"])
        print(f"  {skill['name']:28} {skill['group']:24} {aliases}")


if __name__ == "__main__":
    run()