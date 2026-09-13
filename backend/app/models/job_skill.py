import enum

from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SkillRequirement(str, enum.Enum):
    MANDATORY = "mandatory"
    REQUIRED = "required"
    OPTIONAL = "optional"


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (UniqueConstraint("job_id", "skill_id"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    requirement = Column(SAEnum(SkillRequirement), nullable=False)
    weight = Column(Integer, nullable=False, default=1)

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill")


class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    __table_args__ = (UniqueConstraint("resume_id", "skill_id"),)

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill")