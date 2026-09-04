import streamlit as st
from src.config import APP_NAME, MODELS
from src.ui import inject_css, render_header, render_api_page, render_workspace
from src.utils import validate_openai_key

st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="wide", initial_sidebar_state="expanded")
inject_css()

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = MODELS[0]
if "page" not in st.session_state:
    st.session_state.page = "connect"
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "documents" not in st.session_state:
    st.session_state.documents = []
if "messages" not in st.session_state:
    st.session_state.messages = []

render_header()

if st.session_state.page == "connect":
    render_api_page()
else:
    render_workspace()
