APP_NAME = "DocuMind AI"
EMBEDDING_MODEL = "text-embedding-3-small"
MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"]
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_TOP_K = 5
MAX_FILE_SIZE_MB = 50

SUPPORTED_EXTENSIONS = [
    "pdf", "doc", "docx", "txt", "md", "rtf",
    "csv", "tsv", "xls", "xlsx",
    "ppt", "pptx",
    "html", "htm", "xml", "json",
    "png", "jpg", "jpeg", "webp", "tiff", "bmp"
]
