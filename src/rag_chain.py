from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from .prompts import RAG_PROMPT

def format_docs(docs):
    parts = []
    for d in docs:
        m = d.metadata
        source = m.get("source", "Unknown")
        location = []
        if "page" in m: location.append(f"Page {int(m['page']) + 1}")
        if "sheet" in m: location.append(f"Sheet {m['sheet']}")
        if "slide" in m: location.append(f"Slide {m['slide']}")
        if m.get("ocr"): location.append("OCR")
        label = f"{source} — " + ", ".join(location) if location else source
        parts.append(f"[SOURCE: {label}]\n{d.page_content}")
    return "\n\n".join(parts)

def answer_question(vectorstore, question, api_key, model, k=5):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    if not docs:
        return "I don't know based on the uploaded documents.", []

    context = format_docs(docs)
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)
    chain = RAG_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    return answer, docs
