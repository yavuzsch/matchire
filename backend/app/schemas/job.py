from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import EducationLevel, TechField, Language


class JobCreate(BaseModel):
    title: str
    company_name: str
    location: str | None = None
    description: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    mandatory_skills: list[str] = Field(default_factory=list)
    optional_skills: list[str] = Field(default_factory=list)
    skill_weights: dict[str, int] = Field(default_factory=dict)

    experience_years: int = 0
    education_level: EducationLevel | None = None
    field: TechField | None = None
    language: Language = "tr"
    assessment_slots: int = Field(default=5, ge=1)
    assessment_weight: int = Field(default=50, ge=20, le=80)

    @model_validator(mode="after")
    def check_skill_overlap(self):
        overlap = set(self.optional_skills) & set(self.required_skills)
        if overlap:
            raise ValueError("optional skills cannot overlap with required skills")
        return self


class JobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str
    location: str | None
    description: str | None
    experience_years: int
    education_level: EducationLevel | None
    field: TechField | None
    language: Language
    created_at: datetime


class JobFull(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employer_id: int
    title: str
    company_name: str
    location: str | None
    description: str | None
    required_skills: list[str]
    mandatory_skills: list[str]
    optional_skills: list[str]
    skill_weights: dict[str, int]
    experience_years: int
    education_level: EducationLevel | None
    field: TechField | None
    language: Language
    assessment_slots: int
    assessment_weight: int
    is_active: bool
    is_closed: bool
    created_at: datetime


class JobStatusUpdate(BaseModel):
    is_active: bool | None = None
    is_closed: bool | None = None