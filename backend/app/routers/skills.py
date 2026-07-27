import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/skills", tags=["skills"])

SKILLS_PATH = Path(__file__).resolve().parents[2] / "data" / "skills.json"

with open(SKILLS_PATH, encoding="utf-8") as f:
    SKILLS_DATA = json.load(f)

ALL_SKILLS = sorted(
    {skill for category in SKILLS_DATA["categories"] for skill in category["skills"]}
)


@router.get("")
def list_skills():
    return SKILLS_DATA["categories"]


@router.get("/flat")
def list_skills_flat():
    return ALL_SKILLS