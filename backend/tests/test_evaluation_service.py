from unittest.mock import patch

from app.models import AssessmentQuestion
from app.services.evaluation_service import PASS_THRESHOLD, build_prompt, evaluate_answer


def make_question(text="What does yield do in Python?") -> AssessmentQuestion:
    return AssessmentQuestion(question_text=text)


class TestBuildPrompt:
    def test_includes_question_and_answer(self):
        question = make_question("Question text")
        prompt = build_prompt(question, "Answer text", "tr")

        assert "Question text" in prompt
        assert "Answer text" in prompt


class TestEvaluateAnswer:
    def test_empty_answer_scores_zero_without_llm_call(self):
        question = make_question()

        with patch("app.services.evaluation_service.generate_json") as mock_llm:
            result = evaluate_answer(question, "   ", "tr")

        assert result == (False, 0.0)
        mock_llm.assert_not_called()

    def test_high_score_is_correct(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"is_correct": True, "score": 90},
        ):
            is_correct, score = evaluate_answer(question, "Creates a generator", "tr")

        assert is_correct is True
        assert score == 90.0

    def test_low_score_is_incorrect(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"is_correct": True, "score": 20},
        ):
            is_correct, score = evaluate_answer(question, "I don't know", "tr")

        assert is_correct is False
        assert score == 20.0

    def test_threshold_is_inclusive(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": PASS_THRESHOLD},
        ):
            is_correct, score = evaluate_answer(question, "answer", "tr")

        assert is_correct is True

    def test_score_above_100_is_clamped(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 150},
        ):
            _, score = evaluate_answer(question, "answer", "tr")

        assert score == 100.0

    def test_negative_score_is_clamped(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": -20},
        ):
            _, score = evaluate_answer(question, "answer", "tr")

        assert score == 0.0

    def test_non_dict_response_scores_zero(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value=["unexpected list"],
        ):
            assert evaluate_answer(question, "answer", "tr") == (False, 0.0)

    def test_missing_score_field_defaults_to_zero(self):
        question = make_question()

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"is_correct": True},
        ):
            is_correct, score = evaluate_answer(question, "answer", "tr")

        assert score == 0.0
        assert is_correct is False