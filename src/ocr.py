"""
OCR utilities. Falls back gracefully if Tesseract isn't installed on the
host — the app should never crash because OCR is unavailable, it should
just tell the user the text couldn't be extracted.
"""

import io

from langchain_core.documents import Document


def _tesseract_available() -> bool:
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401

        return True
    except Exception:
        return False


def image_bytes_to_text(file_bytes: bytes) -> str:
    if not _tesseract_available():
        return ""
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def pdf_is_scanned(pdf_path: str, sample_pages: int = 3) -> bool:
    """
    Heuristic: open the first few pages, if extractable text is near-empty
    across all of them, treat the PDF as scanned/image-only.
    """
    try:
        import fitz  # PyMuPDF
    except Exception:
        return False

    try:
        doc = fitz.open(pdf_path)
        pages_to_check = min(sample_pages, len(doc))
        total_chars = 0
        for i in range(pages_to_check):
            total_chars += len(doc[i].get_text().strip())
        doc.close()
        return total_chars < 20 * pages_to_check
    except Exception:
        return False


def ocr_pdf(pdf_path: str, filename: str) -> list[Document]:
    """Rasterize each page and OCR it. Requires PyMuPDF + pytesseract."""
    if not _tesseract_available():
        return [
            Document(
                page_content="[This PDF appears to be scanned and OCR is not "
                "available in this environment, so no text could be extracted.]",
                metadata={"source": filename, "file_type": "pdf", "page": 1, "ocr": True},
            )
        ]

    import fitz
    import pytesseract
    from PIL import Image

    docs = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        if text.strip():
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": filename, "file_type": "pdf", "page": i, "ocr": True},
                )
            )
    doc.close()
    return docs
