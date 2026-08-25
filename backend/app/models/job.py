from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, JSON, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String)
    description = Column(Text)

    required_skills = Column(ARRAY(String))
    mandatory_skills = Column(ARRAY(String))
    optional_skills = Column(ARRAY(String))
    skill_weights = Column(JSON)

    experience_years = Column(Integer, default=0)
    education_level = Column(String)
    field = Column(String)
    language = Column(String, default="tr")
    interview_slots = Column(Integer, default=5)
    interview_weight = Column(Integer, nullable=False, default=50, server_default="50")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    is_closed = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    employer = relationship("User")