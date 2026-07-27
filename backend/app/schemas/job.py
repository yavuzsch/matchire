from pydantic import BaseModel, ConfigDict, Field


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
    education_level: str | None = None
    field: str | None = None


class JobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str
    location: str | None
    description: str | None
    experience_years: int
    education_level: str | None
    field: str | None


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
    education_level: str | None
    field: str | None