from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    phone = Column(String)
    skills = Column(ARRAY(String))
    experience_years = Column(Integer, default=0)

    education_level = Column(String)
    university = Column(String)
    field = Column(String)

    projects = Column(Text)
    certifications = Column(Text)
    languages = Column(JSON)

    candidate = relationship("User")