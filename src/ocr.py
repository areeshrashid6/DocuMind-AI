import io
from PIL import Image

def image_to_text(file_bytes: bytes) -> str:
    """OCR images with pytesseract if installed. Returns a useful error-free fallback."""
    try:
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""
