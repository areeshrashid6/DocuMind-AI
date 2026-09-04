"""
Cleans and splits loaded documents into embedding-ready chunks.
"""

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.document_loader import load_file


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def process_file(file_bytes: bytes, filename: str, chunk_size: int, chunk_overlap: int) -> dict:
    """
    Load + clean + split a single uploaded file.
    Returns a summary dict plus the list of chunk Documents, so the UI can
    show per-document stats without a second pass.
    """
    docs = load_file(file_bytes, filename)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    docs = [d for d in docs if d.page_content]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs) if docs else []

    pages = {d.metadata.get("page") for d in docs if d.metadata.get("page") is not None}

    return {
        "filename": filename,
        "chunks": chunks,
        "num_chunks": len(chunks),
        "num_pages": len(pages) if pages else None,
        "size_bytes": len(file_bytes),
    }
