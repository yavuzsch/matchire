from sqlalchemy import Column, Integer, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    is_selected = Column(Boolean, default=False)

    job = relationship("Job")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)

    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean)
    score = Column(Float, default=0.0)

    application = relationship("Application")
    question = relationship("InterviewQuestion")