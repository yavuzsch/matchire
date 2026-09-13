from pydantic import BaseModel, Field


class SkillOut(BaseModel):
    id: int
    name: str


class SkillGroupOut(BaseModel):
    key: str
    label: str
    skills: list[SkillOut]


class SkillProposal(BaseModel):
    term: str = Field(min_length=1, max_length=100)


class SkillProposalOut(BaseModel):
    id: int
    name: str
    is_verified: bool