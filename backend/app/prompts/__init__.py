from app.prompts import tr

LANGUAGES = {"tr": tr}
DEFAULT_LANGUAGE = "tr"


def get_prompts(language: str | None = None):
    return LANGUAGES.get(language or DEFAULT_LANGUAGE, tr)