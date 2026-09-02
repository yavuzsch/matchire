from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.job_skill import SkillRequirement
from app.schemas.common import EducationLevel, Language, TechField


class JobSkillIn(BaseModel):
    skill_id: int
    requirement: SkillRequirement
    weight: int = Field(default=1, ge=1, le=3)


class JobSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    name: str
    requirement: SkillRequirement
    weight: int


class JobCreate(BaseModel):
    title: str
    company_name: str
    location: str | None = None
    description: str | None = None
    description_raw: str | None = None

    skills: list[JobSkillIn] = Field(default_factory=list)

    experience_years: int = 0
    education_level: EducationLevel | None = None
    field: TechField | None = None
    language: Language = "tr"
    assessment_slots: int = Field(default=5, ge=1)
    assessment_weight: int = Field(default=50, ge=20, le=80)

    @model_validator(mode="after")
    def check_duplicate_skills(self):
        ids = [item.skill_id for item in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate skill")
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
    skills: list[JobSkillOut]
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


class JobParseIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


class JobSkillParsed(BaseModel):
    skill_id: int
    name: str
    requirement: SkillRequirement
    weight: int


class JobParsed(BaseModel):
    title: str | None = None
    company_name: str | None = None
    location: str | None = None
    description: str | None = None
    skills: list[JobSkillParsed] = Field(default_factory=list)
    unmatched_skills: list[str] = Field(default_factory=list)
    experience_years: int = 0
    education_level: EducationLevel | None = None
    field: TechField | None = None