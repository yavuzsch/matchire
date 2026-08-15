import json

from google import genai

from app.core.config import settings

client = genai.Client(api_key=settings.LLM_API_KEY)


def generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()


def generate_json(prompt: str) -> dict | list:
    text = generate_text(prompt)

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())