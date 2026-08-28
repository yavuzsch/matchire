from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors as genai_errors

from app.services.llm_client import (
    MAX_ATTEMPTS,
    LLMUnavailableError,
    generate_json,
    generate_text,
)


def make_response(text: str) -> MagicMock:
    response = MagicMock()
    response.text = text
    return response


def make_server_error() -> genai_errors.ServerError:
    return genai_errors.ServerError(503, {"error": {"message": "overloaded"}})


class TestGenerateText:
    def test_returns_stripped_text(self):
        with patch(
            "app.services.llm_client.client.models.generate_content",
            return_value=make_response("  answer  "),
        ):
            assert generate_text("prompt") == "answer"

    def test_handles_none_text(self):
        with patch(
            "app.services.llm_client.client.models.generate_content",
            return_value=make_response(None),
        ):
            assert generate_text("prompt") == ""

    def test_retries_then_succeeds(self):
        calls = [make_server_error(), make_response("answer")]

        with patch(
            "app.services.llm_client.client.models.generate_content",
            side_effect=calls,
        ) as mock_call:
            with patch("app.services.llm_client.time.sleep"):
                assert generate_text("prompt") == "answer"

        assert mock_call.call_count == 2

    def test_raises_after_max_attempts(self):
        with patch(
            "app.services.llm_client.client.models.generate_content",
            side_effect=make_server_error(),
        ) as mock_call:
            with patch("app.services.llm_client.time.sleep"):
                with pytest.raises(LLMUnavailableError):
                    generate_text("prompt")

        assert mock_call.call_count == MAX_ATTEMPTS

    def test_retries_on_rate_limit(self):
        rate_limit = genai_errors.ClientError(
            429, {"error": {"message": "quota exceeded"}}
        )

        with patch(
            "app.services.llm_client.client.models.generate_content",
            side_effect=[rate_limit, make_response("answer")],
        ) as mock_call:
            with patch("app.services.llm_client.time.sleep"):
                assert generate_text("prompt") == "answer"

        assert mock_call.call_count == 2

    def test_does_not_retry_on_not_found(self):
        not_found = genai_errors.ClientError(
            404, {"error": {"message": "model not found"}}
        )

        with patch(
            "app.services.llm_client.client.models.generate_content",
            side_effect=not_found,
        ) as mock_call:
            with pytest.raises(genai_errors.ClientError):
                generate_text("prompt")

        assert mock_call.call_count == 1


class TestGenerateJson:
    def test_parses_plain_json(self):
        with patch(
            "app.services.llm_client.generate_text",
            return_value='{"score": 90}',
        ):
            assert generate_json("prompt") == {"score": 90}

    def test_strips_json_code_fence(self):
        fenced = '```json\n{"score": 90}\n```'

        with patch("app.services.llm_client.generate_text", return_value=fenced):
            assert generate_json("prompt") == {"score": 90}

    def test_strips_plain_code_fence(self):
        fenced = '```\n["question 1", "question 2"]\n```'

        with patch("app.services.llm_client.generate_text", return_value=fenced):
            assert generate_json("prompt") == ["question 1", "question 2"]

    def test_raises_on_invalid_json(self):
        with patch(
            "app.services.llm_client.generate_text",
            return_value="this is not JSON",
        ):
            with pytest.raises(LLMUnavailableError):
                generate_json("prompt")