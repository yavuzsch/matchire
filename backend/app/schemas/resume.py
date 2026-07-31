from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import EducationLevel, TechField


class ResumeCreate(BaseModel):
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: int = 0

    education_level: EducationLevel | None = None
    university: str | None = None
    field: TechField | None = None

    projects: str | None = None
    certifications: str | None = None
    languages: dict[str, str] = Field(default_factory=dict)


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    phone: str | None
    skills: list[str]
    experience_years: int
    education_level: EducationLevel | None
    university: str | None
    field: TechField | None
    projects: str | None
    certifications: str | None
    languages: dict[str, str]