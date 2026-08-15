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


class QuestionSelect(BaseModel):
    question_ids: list[int]


class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str


class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    answer_text: str
    is_correct: bool | None
    score: float


class AnswerReview(BaseModel):
    question_text: str
    answer_text: str
    is_correct: bool | None
    score: float


class InterviewResult(BaseModel):
    application_id: int
    interview_score: float
    total_score: float
    answered_count: int