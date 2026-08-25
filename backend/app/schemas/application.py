from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus
from app.schemas.job import JobPublic


class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    candidate_id: int
    status: ApplicationStatus
    interview_eligible: bool = False
    job: JobPublic | None = None


class CandidateRow(BaseModel):
    application_id: int
    candidate_id: int
    full_name: str
    email: str
    compatibility_score: float
    interview_score: float
    total_score: float
    status: ApplicationStatus