# 📚 DocuMind AI — Intelligent Document Assistant

Upload PDFs, Word docs, spreadsheets, presentations, images and more, then
ask natural-language questions. Answers are grounded strictly in your
uploaded documents, with citations to the exact page, sheet, or slide.

## Features

- **Broad format support** — PDF, DOC/DOCX, TXT, MD, RTF, XLS/XLSX, CSV/TSV,
  PPT/PPTX, PNG/JPG/WEBP/TIFF/BMP, HTML, XML, JSON
- **OCR fallback** for scanned PDFs and images (via Tesseract)
- **Structure-aware spreadsheets** — sheet, row and column context preserved
  so numeric questions ("which region had the highest revenue?") stay accurate
- **Multi-document RAG** — ask questions across everything you've uploaded,
  compare documents, ask follow-ups with conversational memory
- **Source citations** on every answer — filename + page/sheet/slide
- **Bring-your-own API key** — kept in session memory only, never written to disk
- **Configurable retrieval** — model, temperature, chunk size/overlap, top-k

## Architecture

```
app.py                     Streamlit entry point / screen router
src/
  config.py                Constants and default settings
  document_loader.py       Per-format loaders → LangChain Documents
  document_processor.py    Cleaning + chunking pipeline
  ocr.py                   Image and scanned-PDF OCR helpers
  embeddings.py            OpenAI embeddings wrapper
  vector_store.py          FAISS index build/extend/remove
  rag_chain.py             Retrieval + grounded-answer chain
  prompts.py                System / summary prompts
  ui.py                    Custom CSS + reusable render helpers
  utils.py                 Small shared helpers
```

## Installation

```bash
git clone <your-repo-url>
cd documind-ai

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**OCR (optional, for scanned PDFs/images):** install the Tesseract binary
separately — it's not a Python package.

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows: https://github.com/UB-Mannheim/tesseract/wiki
```

If Tesseract isn't installed, the app still runs — it just tells the user
it couldn't extract text from scanned content instead of crashing.

## Run locally

```bash
streamlit run app.py
```

Open the local URL Streamlit prints, enter your OpenAI API key on the
welcome screen, and start uploading documents.

## Using your OpenAI API key

- Enter it once on the onboarding screen.
- It is stored only in `st.session_state` for the current browser session.
- It is never written to disk, committed, or logged.
- Click **New session** in the sidebar to clear everything, including the key.

## Deployment

### Streamlit Community Cloud
1. Push this repo to GitHub (the `.gitignore` already excludes secrets/caches).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Point it at `app.py` on your repo's main branch.
4. Add `tesseract-ocr` as an `apt` dependency via a `packages.txt` file if you
   want OCR support on Cloud (add a file with that single line at the repo root).
5. Deploy. Users supply their own API key in the app itself — no secrets needed.

### Other hosts (Render, Railway, Fly.io, a VM, etc.)
Any host that can run `pip install -r requirements.txt && streamlit run app.py
--server.port $PORT --server.address 0.0.0.0` will work.

## Troubleshooting

| Issue | Fix |
|---|---|
| "Invalid API key" style errors from OpenAI | Re-check the key on the onboarding screen; regenerate it if needed |
| Scanned PDF returns no text | Make sure Tesseract is installed on the host (see above) |
| Excel numbers look wrong | Re-upload after confirming the sheet has a proper header row |
| App feels slow on large files | Lower chunk size / raise overlap cautiously, or split very large files before upload |
| "Unsupported file type" | Check the extension against the supported list above |

## Security notes

- No API key is ever written to disk, `st.cache`, logs, or vector metadata.
- Each browser session gets its own document set and vector index — nothing
  is shared between users.
- Raw Python tracebacks are never shown to end users; failures render as a
  plain-language warning card instead.
