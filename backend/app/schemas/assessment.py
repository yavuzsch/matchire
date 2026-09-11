from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    question_text: str
    is_selected: bool


class QuestionForCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str


class AssessmentSession(BaseModel):
    questions: list[QuestionForCandidate]
    started_at: datetime | None
    time_limit_minutes: int | None


class QuestionSelect(BaseModel):
    question_ids: list[int]


class AnswerItem(BaseModel):
    question_id: int
    answer_text: str


class AnswerSubmit(BaseModel):
    answers: list[AnswerItem]


class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    answer_text: str


class AnswerReview(BaseModel):
    question_text: str
    answer_text: str
    is_correct: bool | None
    score: float