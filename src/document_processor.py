from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document_loader import load_file

def process_file(file_bytes, filename, chunk_size=1000, chunk_overlap=150):
    docs = load_file(file_bytes, filename)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    return chunks
