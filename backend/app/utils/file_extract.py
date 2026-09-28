"""
Extract raw text from uploaded PDF or DOCX files.

Constraint from the brief: "Handle broken/messy PDFs gracefully — show
a clear error, don't fail silently or crash." So every extractor here
raises a ValueError with a human-readable message on failure, instead
of letting a low-level library exception bubble up.
"""
import io
import pdfplumber
import docx  # python-docx


class ExtractionError(ValueError):
    """Raised when a file can't be read — message is safe to show the user."""
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise ExtractionError("This PDF has no pages.")
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except ExtractionError:
        raise
    except Exception as e:
        # Covers corrupted files, password-protected PDFs, etc.
        raise ExtractionError(
            f"Could not read this PDF — it may be corrupted, scanned as an image, "
            f"or password-protected. ({type(e).__name__})"
        )

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise ExtractionError(
            "No extractable text found in this PDF. It might be a scanned "
            "image rather than real text — OCR support is planned for a "
            "future version, not this MVP."
        )
    return full_text


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        document = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExtractionError(
            f"Could not read this DOCX file — it may be corrupted or not a "
            f"valid Word document. ({type(e).__name__})"
        )

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

    # Tables often hold skills/experience in resume templates — include them.
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    paragraphs.append(cell.text.strip())

    full_text = "\n".join(paragraphs).strip()
    if not full_text:
        raise ExtractionError("No extractable text found in this DOCX file.")
    return full_text


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Dispatch by extension. Raises ExtractionError for unsupported types."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ExtractionError(
            "Unsupported file type. Please upload a .pdf or .docx resume."
        )
