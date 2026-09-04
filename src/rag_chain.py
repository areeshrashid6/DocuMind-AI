"""
Builds the retrieval-augmented generation chain: retriever -> prompt -> LLM.
Also exposes a helper to generate a short document summary on demand.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.prompts import RAG_PROMPT, SUMMARY_PROMPT


def format_docs(docs) -> str:
    blocks = []
    for d in docs:
        meta = d.metadata
        label_bits = [f"Source: {meta.get('source', 'unknown')}"]
        if meta.get("page") is not None:
            label_bits.append(f"Page: {meta['page']}")
        if meta.get("sheet"):
            label_bits.append(f"Sheet: {meta['sheet']}")
        if meta.get("rows"):
            label_bits.append(f"Rows: {meta['rows']}")
        if meta.get("slide") is not None:
            label_bits.append(f"Slide: {meta['slide']}")
        if meta.get("ocr"):
            label_bits.append("Extracted via OCR")
        blocks.append(f"[{' | '.join(label_bits)}]\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)


def history_to_messages(chat_history: list[dict]):
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages


def ask_question(
    vectorstore: FAISS,
    question: str,
    chat_history: list[dict],
    model: str,
    temperature: float,
    top_k: int,
) -> tuple[str, list]:
    """Run one RAG turn. Returns (answer_text, retrieved_docs)."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    retrieved_docs = retriever.invoke(question)

    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = RAG_PROMPT | llm

    response = chain.invoke(
        {
            "context": format_docs(retrieved_docs),
            "history": history_to_messages(chat_history[-6:]),
            "question": question,
        }
    )
    return response.content, retrieved_docs


def summarize_chunks(chunks: list, model: str = "gpt-4o-mini", max_chars: int = 6000) -> str:
    if not chunks:
        return "No content available to summarize."
    content = "\n\n".join(c.page_content for c in chunks)[:max_chars]
    llm = ChatOpenAI(model=model, temperature=0)
    chain = SUMMARY_PROMPT | llm
    response = chain.invoke({"content": content})
    return response.content
