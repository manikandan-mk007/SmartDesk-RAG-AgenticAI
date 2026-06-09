import os

from docx import Document
from pypdf import PdfReader


class DocumentProcessingError(Exception):
    pass


def get_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return "PDF"

    if ext == ".txt":
        return "TXT"

    if ext == ".docx":
        return "DOCX"

    return "OTHER"


def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages).strip()

    except Exception as exc:
        raise DocumentProcessingError(f"PDF text extraction failed: {exc}")


def extract_text_from_txt(file_path: str) -> str:
    encodings = ["utf-8", "utf-16", "latin-1"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read().strip()
        except UnicodeDecodeError:
            continue

    raise DocumentProcessingError("TXT text extraction failed due to encoding issue.")


def extract_text_from_docx(file_path: str) -> str:
    try:
        document = Document(file_path)
        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n\n".join(paragraphs).strip()

    except Exception as exc:
        raise DocumentProcessingError(f"DOCX text extraction failed: {exc}")


def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "PDF":
        text = extract_text_from_pdf(file_path)

    elif file_type == "TXT":
        text = extract_text_from_txt(file_path)

    elif file_type == "DOCX":
        text = extract_text_from_docx(file_path)

    else:
        raise DocumentProcessingError("Unsupported file type.")

    if not text or len(text.strip()) < 20:
        raise DocumentProcessingError("No readable text found in this document.")

    return text.strip()