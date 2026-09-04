"""
Central configuration for DocuMind AI.
Holds constants, default settings and small helpers used across modules.
"""

APP_NAME = "DocuMind AI"
APP_TAGLINE = "Your private AI workspace for understanding documents."

# --------------------------------------------------------------------------
# Supported file types, grouped for the uploader + icon lookup
# --------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    # documents
    "pdf": "document",
    "doc": "document",
    "docx": "document",
    "txt": "text",
    "md": "text",
    "rtf": "document",
    # spreadsheets
    "xls": "spreadsheet",
    "xlsx": "spreadsheet",
    "csv": "spreadsheet",
    "tsv": "spreadsheet",
    # presentations
    "ppt": "presentation",
    "pptx": "presentation",
    # images
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "webp": "image",
    "tiff": "image",
    "bmp": "image",
    # web / data
    "html": "web",
    "htm": "web",
    "xml": "web",
    "json": "web",
}

FILE_ICONS = {
    "document": "📕",
    "text": "📄",
    "spreadsheet": "📊",
    "presentation": "📙",
    "image": "🖼",
    "web": "🌐",
}

# --------------------------------------------------------------------------
# Default settings (overridable from the Settings panel)
# --------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "chunk_size": 1000,
    "chunk_overlap": 150,
    "top_k": 4,
    "embedding_model": "text-embedding-3-small",
}

AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"]

SUGGESTED_QUESTIONS = [
    "Summarize the documents",
    "What are the key findings?",
    "Find the important numbers",
    "Compare these files",
    "Explain this simply",
]

SOURCE_PREVIEW_CHARS = 450
