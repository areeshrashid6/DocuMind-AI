"""Thin wrapper around the embeddings model so it's configured in one place."""

from langchain_openai import OpenAIEmbeddings


def get_embeddings(model: str = "text-embedding-3-small") -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=model)
