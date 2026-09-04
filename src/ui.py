"""
Custom visual layer for DocuMind AI. Streamlit's default chrome is muted
via CSS and replaced with an editorial "reading room" look: a serif display
face for headlines, hairline rules instead of heavy card shadows, and a
single indigo accent used sparingly.
"""

import streamlit as st

from src.config import SUGGESTED_QUESTIONS
from src.utils import file_icon, human_size, truncate

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
INK = "#14161F"
INK_MUTED = "#5B6072"
PAPER = "#F7F7FB"
SURFACE = "#FFFFFF"
BORDER = "#E4E4EF"
ACCENT = "#4338CA"
ACCENT_DARK = "#312E9C"
ACCENT_SOFT = "#EEF0FD"
GOOD = "#0F7A5C"
WARN = "#B45309"

BASE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif;
    color: {INK};
}}

.stApp {{
    background-color: {PAPER};
}}

#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.4rem; max-width: 900px; }}

h1, h2, h3 {{
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 500;
    color: {INK};
    letter-spacing: -0.01em;
}}

/* ---------- top header ---------- */
.dm-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0.9rem 0 1.1rem 0;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1.6rem;
}}
.dm-header .brand {{
    font-family: 'Fraunces', serif;
    font-size: 1.3rem;
    font-weight: 500;
    color: {INK};
}}
.dm-header .brand span {{ color: {ACCENT}; }}
.dm-header .nav-label {{
    font-size: 0.85rem;
    color: {INK_MUTED};
}}

/* ---------- onboarding screen ---------- */
.dm-onboard {{
    max-width: 480px;
    margin: 4vh auto 0 auto;
    text-align: left;
}}
.dm-onboard .mark {{ font-size: 2rem; margin-bottom: 0.6rem; }}
.dm-onboard h1 {{ font-size: 2.1rem; margin-bottom: 0.3rem; }}
.dm-onboard p.lede {{
    color: {INK_MUTED};
    font-size: 1.02rem;
    line-height: 1.55;
    margin-bottom: 1.8rem;
}}

/* ---------- hero ---------- */
.dm-hero {{ padding: 0.4rem 0 1.6rem 0; }}
.dm-hero .eyebrow {{
    font-size: 0.78rem;
    color: {ACCENT};
    font-weight: 600;
    letter-spacing: 0.02em;
    margin-bottom: 0.5rem;
}}
.dm-hero h1 {{ font-size: 2rem; line-height: 1.2; margin-bottom: 0.4rem; }}
.dm-hero p {{ color: {INK_MUTED}; font-size: 1rem; max-width: 46ch; }}

/* ---------- library / document list ---------- */
.dm-lib-title {{
    font-size: 0.78rem;
    text-transform: none;
    color: {INK_MUTED};
    margin: 0.2rem 0 0.7rem 0;
    font-weight: 600;
}}
.dm-doc-card {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.55rem;
    background: {SURFACE};
}}
.dm-doc-card .name {{
    font-size: 0.88rem;
    font-weight: 500;
    color: {INK};
    overflow-wrap: anywhere;
}}
.dm-doc-card .meta {{
    font-size: 0.76rem;
    color: {INK_MUTED};
    margin-top: 0.15rem;
}}
.dm-status-ok {{ color: {GOOD}; font-size: 0.76rem; font-weight: 500; }}

.dm-metric {{
    border-left: 2px solid {ACCENT};
    padding: 0.1rem 0 0.1rem 0.7rem;
}}
.dm-metric .num {{ font-family: 'Fraunces', serif; font-size: 1.5rem; color: {INK}; }}
.dm-metric .label {{ font-size: 0.76rem; color: {INK_MUTED}; }}

/* ---------- upload dropzone ---------- */
[data-testid="stFileUploaderDropzone"] {{
    background: {SURFACE};
    border: 1.5px dashed {BORDER};
    border-radius: 12px;
}}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color: {ACCENT}; }}

/* ---------- buttons ---------- */
.stButton>button, .stDownloadButton>button {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.45rem 1rem;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{ background-color: {ACCENT_DARK}; color: white; }}
button[kind="secondary"] {{ background: {SURFACE} !important; color: {INK} !important; border: 1px solid {BORDER} !important; }}

/* ---------- chat ---------- */
[data-testid="stChatMessage"] {{
    background: transparent;
}}
.dm-source {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0.5rem 0.7rem;
    margin-bottom: 0.5rem;
    background: {SURFACE};
}}
.dm-source .tag {{ font-size: 0.78rem; font-weight: 600; color: {ACCENT}; }}
.dm-source .preview {{ font-size: 0.82rem; color: {INK_MUTED}; margin-top: 0.2rem; }}

.dm-empty {{
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
    color: {INK_MUTED};
}}
.dm-empty .mark {{ font-size: 2.2rem; }}
.dm-empty h3 {{ margin: 0.4rem 0 0.2rem 0; }}

.dm-suggest {{ margin-top: 0.6rem; }}

/* sidebar */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

/* error / warning card */
.dm-warn {{
    border: 1px solid #F3D9B1;
    background: #FFF8EE;
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    color: {WARN};
    font-size: 0.86rem;
    margin-bottom: 0.6rem;
}}
</style>
"""


def inject_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def render_header(screen_label: str):
    st.markdown(
        f"""
        <div class="dm-header">
            <div class="brand">📚 DocuMind <span>AI</span></div>
            <div class="nav-label">{screen_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="dm-hero">
            <div class="eyebrow">AI DOCUMENT INTELLIGENCE</div>
            <h1>Talk to your documents.</h1>
            <p>Upload files and get accurate, source-backed answers &mdash;
            grounded only in what you've uploaded, never invented.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_doc_card(doc_meta: dict) -> None:
    icon = file_icon(doc_meta["filename"])
    size = human_size(doc_meta["size_bytes"])
    extra = f" • {doc_meta['num_pages']} pages" if doc_meta.get("num_pages") else ""
    st.markdown(
        f"""
        <div class="dm-doc-card">
            <div class="name">{icon} {doc_meta['filename']}</div>
            <div class="meta">{size}{extra} • {doc_meta['num_chunks']} chunks</div>
            <div class="dm-status-ok">&#10003; Indexed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(num_docs: int, num_pages: int, num_chunks: int, ready: bool):
    cols = st.columns(4)
    values = [
        ("Documents", num_docs),
        ("Pages", num_pages if num_pages else "—"),
        ("Chunks", num_chunks),
        ("Status", "Ready" if ready else "Empty"),
    ]
    for col, (label, val) in zip(cols, values):
        with col:
            st.markdown(
                f"""<div class="dm-metric"><div class="num">{val}</div>
                <div class="label">{label}</div></div>""",
                unsafe_allow_html=True,
            )


def render_empty_state():
    st.markdown(
        """
        <div class="dm-empty">
            <div class="mark">📚</div>
            <h3>Ask your documents anything.</h3>
            <div>Upload one or more files in the sidebar to start exploring your information.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_suggestions() -> str | None:
    st.markdown('<div class="dm-suggest"></div>', unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    clicked = None
    for col, q in zip(cols, SUGGESTED_QUESTIONS):
        with col:
            if st.button(q, key=f"suggest_{q}", use_container_width=True):
                clicked = q
    return clicked


def render_sources(retrieved_docs):
    with st.expander(f"Sources ({len(retrieved_docs)})"):
        for d in retrieved_docs:
            meta = d.metadata
            icon = file_icon(meta.get("source", ""))
            bits = [meta.get("source", "unknown")]
            if meta.get("page") is not None:
                bits.append(f"Page {meta['page']}")
            if meta.get("sheet"):
                bits.append(f"Sheet: {meta['sheet']}")
            if meta.get("rows"):
                bits.append(f"Rows {meta['rows']}")
            if meta.get("slide") is not None:
                bits.append(f"Slide {meta['slide']}")
            if meta.get("ocr"):
                bits.append("OCR")
            st.markdown(
                f"""
                <div class="dm-source">
                    <div class="tag">{icon} {" — ".join(bits)}</div>
                    <div class="preview">{truncate(d.page_content, 450)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_warning(message: str):
    st.markdown(f'<div class="dm-warn">⚠ {message}</div>', unsafe_allow_html=True)
