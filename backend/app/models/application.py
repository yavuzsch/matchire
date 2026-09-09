import enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ASSESSMENT = "assessment"
    COMPLETED = "completed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "candidate_id"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    compatibility_score = Column(Float, default=0.0)
    assessment_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)

    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    assessment_started_at = Column(DateTime(timezone=True), nullable=True)
    hidden_by_candidate = Column(Boolean, nullable=False, default=False, server_default="false")

    job = relationship("Job")
    candidate = relationship("User")