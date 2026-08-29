import io

from pypdf import PdfReader

MAX_PAGES = 10
MAX_CHARS = 20000


class PdfExtractionError(Exception):
    pass


def extract_text(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as error:
        raise PdfExtractionError(str(error))

    if len(reader.pages) > MAX_PAGES:
        raise PdfExtractionError("too many pages")

    parts = []

    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        if text.strip():
            parts.append(text.strip())

    combined = "\n\n".join(parts)

    if not combined.strip():
        raise PdfExtractionError("no text found")

    return combined[:MAX_CHARS]