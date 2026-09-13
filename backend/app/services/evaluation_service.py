from app.models import AssessmentQuestion
from app.prompts import get_prompts
from app.services.llm_client import generate_json

PASS_THRESHOLD = 50


def build_prompt(question: AssessmentQuestion, answer_text: str, language: str) -> str:
    prompts = get_prompts(language)

    return prompts.EVALUATION_TEMPLATE.format(
        question=question.question_text,
        answer=answer_text,
    )


def evaluate_answer(
    question: AssessmentQuestion, answer_text: str, language: str
) -> tuple[bool, float]:
    if not answer_text.strip():
        return False, 0.0

    result = generate_json(build_prompt(question, answer_text, language))

    if not isinstance(result, dict):
        return False, 0.0

    score = float(result.get("score", 0))
    score = max(0.0, min(score, 100.0))

    return score >= PASS_THRESHOLD, score