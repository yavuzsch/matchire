from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category_key = Column(String, nullable=False)

    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False, unique=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    skill = relationship("Skill", back_populates="aliases")


class UnknownSkill(Base):
    __tablename__ = "unknown_skills"

    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(String, nullable=False)
    seen_count = Column(Integer, nullable=False, default=1)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())