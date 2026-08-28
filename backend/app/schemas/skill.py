from pydantic import BaseModel


class SkillOut(BaseModel):
    id: int
    name: str


class SkillGroupOut(BaseModel):
    key: str
    label: str
    skills: list[SkillOut]