import os
import streamlit as st
from .config import APP_NAME, MODELS, SUPPORTED_EXTENSIONS, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_TOP_K, MAX_FILE_SIZE_MB
from .utils import validate_openai_key, human_size
from .document_processor import process_file
from .vector_store import build_vectorstore
from .rag_chain import answer_question

def inject_css():
    st.markdown("""
    <style>
    #MainMenu, footer {visibility:hidden;}
    .stApp {background:#f7f8fc;}
    [data-testid="stSidebar"] {background:#ffffff; border-right:1px solid #e8eaf0;}
    .block-container {max-width:1180px; padding-top:1.2rem; padding-bottom:5rem;}
    .brand {font-size:20px;font-weight:800;color:#171a2b;letter-spacing:-.4px;}
    .muted {color:#6b7280;font-size:14px;}
    .hero {padding:58px 0 35px;text-align:center;}
    .hero-badge {display:inline-block;padding:7px 12px;border-radius:999px;background:#eef0ff;color:#5146d8;font-size:11px;font-weight:800;letter-spacing:1px;}
    .hero h1 {font-size:46px;line-height:1.05;letter-spacing:-2px;color:#151827;margin:17px 0 12px;}
    .hero p {font-size:17px;color:#667085;max-width:650px;margin:auto;}
    .card {background:white;border:1px solid #e7e9ef;border-radius:18px;padding:24px;box-shadow:0 8px 30px rgba(20,25,45,.04);}
    .upload-card {text-align:center;padding:32px;border:1.5px dashed #cfd3df;border-radius:18px;background:#fff;}
    .stat {background:white;border:1px solid #e7e9ef;border-radius:15px;padding:17px;}
    .stat .num {font-size:25px;font-weight:800;color:#161925;}
    .stat .label {font-size:12px;color:#777f91;margin-top:3px;}
    .file-card {border:1px solid #e8eaf0;border-radius:12px;padding:12px;margin:8px 0;background:#fff;}
    .source-card {background:#f8f9fc;border:1px solid #e7e9ef;border-radius:12px;padding:12px;margin-top:8px;}
    .connect-wrap {max-width:650px;margin:50px auto;}
    div.stButton > button {border-radius:10px;border:0;padding:.6rem 1rem;font-weight:700;}
    div.stButton > button[kind="primary"] {background:#5b4ee8;color:white;}
    textarea, input {border-radius:10px !important;}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown(f'<div class="brand">📚 {APP_NAME}</div>', unsafe_allow_html=True)
    st.divider()

def render_api_page():
    st.markdown("""
    <div class="connect-wrap">
      <div class="hero">
        <div class="hero-badge">AI DOCUMENT INTELLIGENCE</div>
        <h1>Your documents.<br>Now searchable with AI.</h1>
        <p>Connect your OpenAI account, upload your files, and ask grounded questions from your own documents.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Connect to OpenAI")
        st.caption("Your API key is kept only in this Streamlit session and is not written to disk.")
        key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        model = st.selectbox("AI model", MODELS)
        if st.button("Connect to Workspace →", type="primary", use_container_width=True):
            ok, error = validate_openai_key(key)
            if not ok:
                st.error(error)
            else:
                st.session_state.api_key = key.strip()
                st.session_state.model = model
                st.session_state.page = "workspace"
                st.success("Connected successfully.")
                st.rerun()

def _reset():
    st.session_state.vectorstore = None
    st.session_state.documents = []
    st.session_state.messages = []

def render_workspace():
    with st.sidebar:
        st.markdown("### Document Library")
        st.caption("Upload files to create your private search index.")
        if st.button("← Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            _reset()
            st.session_state.page = "connect"
            st.rerun()

        st.divider()
        uploaded = st.file_uploader(
            "Upload files",
            type=SUPPORTED_EXTENSIONS,
            accept_multiple_files=True,
            help="PDF, Word, Excel, PowerPoint, CSV, text, HTML, JSON, XML and common images are supported."
        )

        st.divider()
        st.markdown("### Settings")
        chunk_size = st.slider("Chunk size", 500, 2000, DEFAULT_CHUNK_SIZE, 100)
        overlap = st.slider("Chunk overlap", 0, 400, DEFAULT_CHUNK_OVERLAP, 50)
        top_k = st.slider("Retrieved chunks", 2, 10, DEFAULT_TOP_K)

        if st.button("Clear documents", use_container_width=True):
            _reset()
            st.rerun()

    st.markdown("""
    <div class="hero" style="padding-top:20px">
      <div class="hero-badge">PRIVATE DOCUMENT WORKSPACE</div>
      <h1>Talk to your documents.</h1>
      <p>Upload files and get source-backed answers without leaving your workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    if uploaded:
        sig = [(f.name, f.size) for f in uploaded]
        if st.session_state.get("file_sig") != sig or st.session_state.vectorstore is None:
            all_chunks = []
            metadata_cards = []
            progress = st.progress(0, text="Starting document processing...")
            for i, f in enumerate(uploaded):
                progress.progress(int(i / len(uploaded) * 85), text=f"Reading {f.name}...")
                try:
                    chunks = process_file(f.getvalue(), f.name, chunk_size, overlap)
                    all_chunks.extend(chunks)
                    metadata_cards.append((f.name, f.size, len(chunks), None))
                except Exception as exc:
                    metadata_cards.append((f.name, f.size, 0, str(exc)))
            progress.progress(90, text="Creating vector index...")
            try:
                st.session_state.vectorstore = build_vectorstore(all_chunks, st.session_state.api_key)
                st.session_state.documents = metadata_cards
                st.session_state.file_sig = sig
                st.session_state.messages = []
                progress.progress(100, text="Ready ✓")
            except Exception as exc:
                progress.empty()
                st.error(f"Could not build the document index: {exc}")
                return

        st.success(f"{len(uploaded)} file(s) indexed and ready.")
    else:
        st.markdown('<div class="upload-card"><h3>📄 Drop your documents here</h3><p>Upload PDF, Word, Excel, PowerPoint, images, CSV, text and more.</p></div>', unsafe_allow_html=True)
        return

    cols = st.columns(4)
    docs_count = len(st.session_state.documents)
    chunks_count = sum(x[2] for x in st.session_state.documents)
    cols[0].markdown(f'<div class="stat"><div class="num">{docs_count}</div><div class="label">Documents</div></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="stat"><div class="num">{chunks_count}</div><div class="label">Chunks</div></div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div class="stat"><div class="num">✓</div><div class="label">Index status</div></div>', unsafe_allow_html=True)
    cols[3].markdown(f'<div class="stat"><div class="num">{st.session_state.model}</div><div class="label">AI model</div></div>', unsafe_allow_html=True)

    st.write("")
    for name, size, chunks, error in st.session_state.documents:
        icon = "📄"
        ext = os.path.splitext(name)[1].lower()
        if ext in [".xlsx",".xls",".csv",".tsv"]: icon = "📊"
        elif ext in [".pptx",".ppt"]: icon = "📙"
        elif ext in [".jpg",".jpeg",".png",".webp",".tiff",".bmp"]: icon = "🖼️"
        st.markdown(f'<div class="file-card">{icon} <b>{name}</b> · {human_size(size)} · {chunks} chunks {"· ⚠️ " + error if error else "· ✓ Indexed"}</div>', unsafe_allow_html=True)

    st.write("")
    if not st.session_state.messages:
        st.markdown('<div class="card" style="text-align:center"><h3>Ask anything about your files</h3><p class="muted">Answers are limited to the indexed document content.</p></div>', unsafe_allow_html=True)
        suggestions = ["Summarize the documents", "What are the key findings?", "Find the important numbers", "Compare the uploaded files"]
        s_cols = st.columns(4)
        for i, s in enumerate(suggestions):
            if s_cols[i].button(s, use_container_width=True):
                st.session_state.pending_question = s
                st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for d in msg["sources"]:
                        m = d.metadata
                        loc = []
                        if "page" in m: loc.append(f"Page {int(m['page'])+1}")
                        if "sheet" in m: loc.append(f"Sheet {m['sheet']}")
                        if "slide" in m: loc.append(f"Slide {m['slide']}")
                        st.markdown(f"**{m.get('source','Unknown')}** · {', '.join(loc) if loc else 'Document'}")
                        st.caption(d.page_content[:500])

    question = st.chat_input("Ask a question about your documents...")
    question = question or st.session_state.pop("pending_question", None)

    if question:
        st.session_state.messages.append({"role":"user","content":question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching your documents..."):
                try:
                    answer, sources = answer_question(
                        st.session_state.vectorstore,
                        question,
                        st.session_state.api_key,
                        st.session_state.model,
                        top_k
                    )
                    st.markdown(answer)
                    with st.expander("Sources"):
                        for d in sources:
                            m = d.metadata
                            loc = []
                            if "page" in m: loc.append(f"Page {int(m['page'])+1}")
                            if "sheet" in m: loc.append(f"Sheet {m['sheet']}")
                            if "slide" in m: loc.append(f"Slide {m['slide']}")
                            st.markdown(f"**{m.get('source','Unknown')}** · {', '.join(loc) if loc else 'Document'}")
                            st.caption(d.page_content[:500])
                    st.session_state.messages.append({"role":"assistant","content":answer,"sources":sources})
                except Exception as exc:
                    st.error("I couldn't process that question. Please check your API access and try again.")
