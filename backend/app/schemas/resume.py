from pydantic import BaseModel, ConfigDict, Field


class ResumeCreate(BaseModel):
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: int = 0

    education_level: str | None = None
    university: str | None = None
    field: str | None = None

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
    education_level: str | None
    university: str | None
    field: str | None
    projects: str | None
    certifications: str | None
    languages: dict[str, str]