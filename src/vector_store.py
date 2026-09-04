"""
Manages a single FAISS index for the current session. Supports adding
newly-uploaded documents into an existing index and removing all chunks
belonging to a given filename (used by the sidebar's remove button).
"""

from langchain_community.vectorstores import FAISS

from src.embeddings import get_embeddings


def build_or_extend(existing_store: FAISS | None, chunks: list, embedding_model: str) -> FAISS:
    if not chunks:
        return existing_store

    embeddings = get_embeddings(embedding_model)
    if existing_store is None:
        return FAISS.from_documents(chunks, embeddings)

    existing_store.add_documents(chunks)
    return existing_store


def remove_document(store: FAISS, filename: str) -> FAISS | None:
    """
    Rebuild the index excluding chunks from `filename`, since FAISS doesn't
    support deleting by metadata directly in all versions.
    """
    remaining_docs = [
        doc
        for doc_id, doc in store.docstore._dict.items()
        if doc.metadata.get("source") != filename
    ]
    if not remaining_docs:
        return None
    embeddings = store.embeddings
    return FAISS.from_documents(remaining_docs, embeddings)
