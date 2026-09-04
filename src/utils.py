import os

from src.config import FILE_ICONS, SUPPORTED_EXTENSIONS


def file_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    category = SUPPORTED_EXTENSIONS.get(ext, "text")
    return FILE_ICONS.get(category, "📄")


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def validate_api_key_format(key: str) -> bool:
    return bool(key) and key.startswith("sk-") and len(key) > 20
