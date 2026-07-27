import enum

from sqlalchemy import Column, Integer, Float, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    INTERVIEW = "interview"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "candidate_id"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    compatibility_score = Column(Float, default=0.0)
    interview_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)

    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.PENDING)

    job = relationship("Job")
    candidate = relationship("User")