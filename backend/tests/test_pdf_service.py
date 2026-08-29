import io

import pytest
from pypdf import PdfWriter

from app.services.pdf_service import MAX_PAGES, PdfExtractionError, extract_text


def make_pdf(page_count: int) -> bytes:
    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(width=200, height=200)

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class TestExtractText:
    def test_rejects_invalid_pdf(self):
        with pytest.raises(PdfExtractionError):
            extract_text(b"this is not a pdf")

    def test_rejects_empty_input(self):
        with pytest.raises(PdfExtractionError):
            extract_text(b"")

    def test_rejects_too_many_pages(self):
        content = make_pdf(MAX_PAGES + 1)

        with pytest.raises(PdfExtractionError):
            extract_text(content)

    def test_rejects_pdf_without_text(self):
        content = make_pdf(1)

        with pytest.raises(PdfExtractionError):
            extract_text(content)