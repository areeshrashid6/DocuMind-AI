from langchain_openai import OpenAIEmbeddings
from .config import EMBEDDING_MODEL

def get_embeddings(api_key: str):
    return OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)
