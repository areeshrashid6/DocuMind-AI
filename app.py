"""
DocuMind AI — Intelligent Document Assistant
Entry point: run with `streamlit run app.py`
"""

import streamlit as st

from src.config import (
    APP_NAME,
    APP_TAGLINE,
    AVAILABLE_MODELS,
    DEFAULT_SETTINGS,
    SUPPORTED_EXTENSIONS,
)
from src.document_processor import process_file
from src.rag_chain import ask_question, summarize_chunks
from src.ui import (
    inject_css,
    render_doc_card,
    render_empty_state,
    render_header,
    render_hero,
    render_metrics,
    render_sources,
    render_suggestions,
    render_warning,
)
from src.utils import validate_api_key_format
from src.vector_store import build_or_extend, remove_document

st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
defaults = {
    "api_key": "",
    "unlocked": False,
    "vectorstore": None,
    "documents": [],  # list of dicts: filename, num_chunks, num_pages, size_bytes
    "messages": [],
    "settings": dict(DEFAULT_SETTINGS),
    "pending_question": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# SCREEN 1 — API key onboarding
# ---------------------------------------------------------------------------
def render_onboarding():
    render_header("Setup")
    st.markdown(
        f"""
        <div class="dm-onboard">
            <div class="mark">📚</div>
            <h1>{APP_NAME}</h1>
            <p class="lede">{APP_TAGLINE}<br/>
            Upload documents, spreadsheets, presentations and images, then ask
            questions using natural language.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        col = st.columns([1, 1.4, 1])[1]
        with col:
            key_input = st.text_input(
                "Enter your OpenAI API Key",
                type="password",
                placeholder="sk-...",
                value=st.session_state.api_key,
            )
            st.caption(
                "Your key stays in this browser session only — it is never "
                "written to disk, logged, or stored on a server."
            )
            if st.button("Continue to Workspace →", use_container_width=True):
                if not validate_api_key_format(key_input):
                    render_warning("That doesn't look like a valid OpenAI API key. It should start with 'sk-'.")
                else:
                    st.session_state.api_key = key_input
                    st.session_state.unlocked = True
                    st.rerun()


# ---------------------------------------------------------------------------
# Sidebar — document library + settings
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="dm-lib-title">DOCUMENT LIBRARY</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload files",
            type=list(SUPPORTED_EXTENSIONS.keys()),
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        st.caption("PDF • DOCX • XLSX • PPTX • CSV • TXT • Images")

        if uploaded_files:
            existing_names = {d["filename"] for d in st.session_state.documents}
            new_files = [f for f in uploaded_files if f.name not in existing_names]
            if new_files:
                progress = st.progress(0.0, text="Processing documents...")
                for i, f in enumerate(new_files):
                    try:
                        result = process_file(
                            f.getvalue(),
                            f.name,
                            st.session_state.settings["chunk_size"],
                            st.session_state.settings["chunk_overlap"],
                        )
                        st.session_state.vectorstore = build_or_extend(
                            st.session_state.vectorstore,
                            result["chunks"],
                            st.session_state.settings["embedding_model"],
                        )
                        st.session_state.documents.append(
                            {
                                "filename": result["filename"],
                                "num_chunks": result["num_chunks"],
                                "num_pages": result["num_pages"],
                                "size_bytes": result["size_bytes"],
                            }
                        )
                    except Exception as e:
                        render_warning(
                            f"Couldn't process '{f.name}'. It may be corrupted, "
                            f"password-protected, or an unsupported variant. ({type(e).__name__})"
                        )
                    progress.progress((i + 1) / len(new_files), text=f"Indexed {f.name}")
                progress.empty()
                st.rerun()

        if st.session_state.documents:
            for doc in list(st.session_state.documents):
                render_doc_card(doc)
                if st.button("Remove", key=f"remove_{doc['filename']}", use_container_width=True):
                    if st.session_state.vectorstore is not None:
                        st.session_state.vectorstore = remove_document(
                            st.session_state.vectorstore, doc["filename"]
                        )
                    st.session_state.documents = [
                        d for d in st.session_state.documents if d["filename"] != doc["filename"]
                    ]
                    st.rerun()

            if st.button("Clear all documents", use_container_width=True):
                st.session_state.vectorstore = None
                st.session_state.documents = []
                st.session_state.messages = []
                st.rerun()
        else:
            st.caption("No documents yet. Drop files above to get started.")

        with st.expander("⚙ Settings"):
            st.session_state.settings["model"] = st.selectbox(
                "AI model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(st.session_state.settings["model"])
            )
            st.session_state.settings["temperature"] = st.slider(
                "Temperature", 0.0, 1.0, st.session_state.settings["temperature"], 0.05
            )
            st.session_state.settings["chunk_size"] = st.slider(
                "Chunk size", 500, 2000, st.session_state.settings["chunk_size"], 100
            )
            st.session_state.settings["chunk_overlap"] = st.slider(
                "Chunk overlap", 0, 400, st.session_state.settings["chunk_overlap"], 50
            )
            st.session_state.settings["top_k"] = st.slider(
                "Retrieved chunks (k)", 2, 10, st.session_state.settings["top_k"]
            )
            st.caption("Chunk changes apply to newly uploaded documents.")

        if st.button("New session", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key] if key != "settings" else dict(DEFAULT_SETTINGS)
            st.rerun()


# ---------------------------------------------------------------------------
# Main workspace
# ---------------------------------------------------------------------------
def render_workspace():
    render_header("Workspace")
    render_sidebar()

    has_docs = bool(st.session_state.documents)

    if not st.session_state.messages:
        render_hero()

    if has_docs:
        total_chunks = sum(d["num_chunks"] for d in st.session_state.documents)
        pages = [d["num_pages"] for d in st.session_state.documents if d["num_pages"]]
        render_metrics(len(st.session_state.documents), sum(pages) if pages else 0, total_chunks, True)
        st.markdown("<br/>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                render_sources(msg["sources"])

    if not st.session_state.messages:
        if has_docs:
            st.markdown("**Try asking:**")
            clicked = render_suggestions()
            if clicked:
                st.session_state.pending_question = clicked
        else:
            render_empty_state()

    question = st.chat_input(
        "Ask anything about your documents..." if has_docs else "Upload a document to start chatting",
        disabled=not has_docs,
    )
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question and has_docs:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, retrieved_docs = ask_question(
                        st.session_state.vectorstore,
                        question,
                        st.session_state.messages[:-1],
                        st.session_state.settings["model"],
                        st.session_state.settings["temperature"],
                        st.session_state.settings["top_k"],
                    )
                except Exception as e:
                    answer = (
                        "Something went wrong while generating an answer. "
                        "Please check your API key and try again."
                    )
                    retrieved_docs = []
                    render_warning(f"{type(e).__name__}: request failed.")
                st.markdown(answer)
                if retrieved_docs:
                    render_sources(retrieved_docs)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": retrieved_docs}
        )
        st.rerun()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if not st.session_state.unlocked or not st.session_state.api_key:
    render_onboarding()
else:
    import os

    os.environ["OPENAI_API_KEY"] = st.session_state.api_key
    render_workspace()
