from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SkillGroup(Base):
    __tablename__ = "skill_groups"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, unique=True, index=True)
    position = Column(Integer, nullable=False, default=0)

    labels = relationship("SkillGroupLabel", back_populates="group", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="group")


class SkillGroupLabel(Base):
    __tablename__ = "skill_group_labels"
    __table_args__ = (UniqueConstraint("group_id", "language"),)

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("skill_groups.id"), nullable=False)
    language = Column(String, nullable=False, index=True)
    label = Column(String, nullable=False)

    group = relationship("SkillGroup", back_populates="labels")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    group_id = Column(Integer, ForeignKey("skill_groups.id"), nullable=False)
    source = Column(String, nullable=False, default="llm")
    is_deprecated = Column(Boolean, nullable=False, default=False, server_default="false")
    is_verified = Column(Boolean, nullable=False, default=True, server_default="true")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    group = relationship("SkillGroup", back_populates="skills")
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
    normalized_text = Column(String, nullable=False, index=True)
    seen_count = Column(Integer, nullable=False, default=1)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())