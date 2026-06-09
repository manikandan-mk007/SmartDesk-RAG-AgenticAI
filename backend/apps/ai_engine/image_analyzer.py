from PIL import Image, ImageEnhance, ImageFilter
from django.conf import settings

from apps.ai_engine.multimodal_rules import (
    build_analysis_summary,
    clean_ocr_text,
    detect_issue_type,
)

try:
    import pytesseract
except ImportError:
    pytesseract = None


def setup_tesseract():
    if pytesseract and settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def preprocess_image(image_path: str) -> Image.Image:
    image = Image.open(image_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(1.8)
    image = image.filter(ImageFilter.SHARPEN)

    return image


def extract_text_from_image(image_path: str) -> str:
    if not pytesseract:
        return ""

    setup_tesseract()

    try:
        image = preprocess_image(image_path)
        text = pytesseract.image_to_string(image)
        return clean_ocr_text(text)

    except Exception:
        return ""


def analyze_image_attachment(image_path: str) -> dict:
    if not settings.IMAGE_ANALYSIS_ENABLED:
        return {
            "success": False,
            "issue_type": "Image Analysis Disabled",
            "extracted_text": "",
            "summary": "Image analysis is disabled in settings.",
        }

    extracted_text = extract_text_from_image(image_path)

    issue_type = detect_issue_type(
        extracted_text,
        file_type="IMAGE",
    )

    summary = build_analysis_summary(
        file_type="IMAGE",
        issue_type=issue_type,
        extracted_text=extracted_text,
    )

    if not extracted_text:
        summary += (
            "\nNote: OCR could not read text clearly from this image. "
            "Please check the image manually or ask the user for a clearer screenshot."
        )

    return {
        "success": True,
        "issue_type": issue_type,
        "extracted_text": extracted_text,
        "summary": summary,
    }