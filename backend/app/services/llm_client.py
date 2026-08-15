import json
import time

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings

client = genai.Client(api_key=settings.LLM_API_KEY)

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 3


class LLMUnavailableError(Exception):
    pass


def generate_text(prompt: str) -> str:
    last_error = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=settings.LLM_MODEL,
                contents=prompt,
            )
            return (response.text or "").strip()
        except genai_errors.ServerError as error:
            last_error = error
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))

    raise LLMUnavailableError(str(last_error))


def generate_json(prompt: str) -> dict | list:
    text = generate_text(prompt)

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as error:
        raise LLMUnavailableError(str(error))