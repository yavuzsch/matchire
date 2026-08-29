from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import EducationLevel, TechField


class ResumeCreate(BaseModel):
    phone: str | None = None
    skill_ids: list[int] = Field(default_factory=list)
    experience_years: int = 0

    education_level: EducationLevel | None = None
    university: str | None = None
    field: TechField | None = None

    projects: str | None = None
    certifications: str | None = None
    languages: dict[str, str] = Field(default_factory=dict)


class ResumeSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    name: str


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    phone: str | None
    skills: list[ResumeSkillOut]
    experience_years: int
    education_level: EducationLevel | None
    university: str | None
    field: TechField | None
    projects: str | None
    certifications: str | None
    languages: dict[str, str]


class ResumeParsed(BaseModel):
    phone: str | None = None
    skill_ids: list[int] = Field(default_factory=list)
    skill_names: list[str] = Field(default_factory=list)
    unmatched_skills: list[str] = Field(default_factory=list)
    experience_years: int = 0
    education_level: EducationLevel | None = None
    university: str | None = None
    field: TechField | None = None
    projects: str | None = None
    certifications: str | None = None