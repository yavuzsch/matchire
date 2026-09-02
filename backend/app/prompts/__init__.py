from app.core.config import settings
from app.prompts import tr

LANGUAGES = {"tr": tr}


def get_prompts(language: str | None = None):
    return LANGUAGES.get(language or settings.DEFAULT_LANGUAGE, tr)