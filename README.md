# DocuMind AI — Streamlit RAG Agent

A polished Streamlit document assistant using OpenAI + LangChain + FAISS.

## Features

- API key connection screen before workspace
- OpenAI model selection
- Invalid-key error handling
- Multi-file upload
- PDF, DOC/DOCX, XLS/XLSX, CSV/TSV, PPT/PPTX, TXT, Markdown, HTML, JSON, XML and common images
- OCR for images when Tesseract is available
- PDF page metadata
- Excel sheet metadata
- PowerPoint slide metadata
- FAISS vector search
- Grounded RAG answers
- Source previews
- "I don't know based on the uploaded documents." fallback for unsupported/out-of-scope questions
- Session-only API key handling
- Premium light UI

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload the complete project.
3. In Streamlit Community Cloud choose **New app**.
4. Select your repository.
5. Set the main file to `app.py`.
6. Deploy.

The user enters their own OpenAI API key in the app. You do not need to put a personal OpenAI key in Streamlit secrets.

## Local run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Important OCR note

Image OCR requires the Tesseract executable to be installed on the server. The Python package alone does not install the Tesseract binary. If deploying to a Linux environment where you control system packages, install Tesseract. If not, the app will gracefully return no OCR text for images.

Scanned PDFs are handled by PyMuPDF for extractable PDF text. A production OCR deployment should add a PDF OCR service or system Tesseract/PyMuPDF preprocessing for image-only PDFs.

## Security

- API keys are kept in Streamlit session state.
- API keys are not written to disk or included in FAISS metadata.
- Do not commit `.env` or `secrets.toml`.
- Each user's uploaded documents are processed in their Streamlit session.

## File-size note

The included config allows uploads up to 50 MB per file. Increase this only if your deployment resources and OpenAI usage budget support it.
