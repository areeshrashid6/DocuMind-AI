from langchain_community.vectorstores import FAISS
from .embeddings import get_embeddings

def build_vectorstore(chunks, api_key):
    if not chunks:
        raise ValueError("No readable text was found in the uploaded files.")
    return FAISS.from_documents(chunks, get_embeddings(api_key))
