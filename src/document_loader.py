import io, json, os, tempfile
from pathlib import Path
from langchain_core.documents import Document
from .ocr import image_to_text

def _tmp_file(file_bytes, suffix):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(file_bytes); f.close()
    return f.name

def load_file(file_bytes: bytes, filename: str):
    ext = Path(filename).suffix.lower()
    meta = {"source": filename, "file_type": ext.lstrip(".")}

    if ext == ".pdf":
        from langchain_community.document_loaders import PyMuPDFLoader
        path = _tmp_file(file_bytes, ext)
        try:
            docs = PyMuPDFLoader(path).load()
        finally:
            os.unlink(path)
        for d in docs: d.metadata.update(meta)
        return docs

    if ext in {".docx", ".doc"}:
        try:
            from langchain_community.document_loaders import UnstructuredWordDocumentLoader
            path = _tmp_file(file_bytes, ext)
            try: docs = UnstructuredWordDocumentLoader(path).load()
            finally: os.unlink(path)
        except Exception:
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(file_bytes))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            docs = [Document(page_content=text, metadata=meta)]
        for d in docs: d.metadata.update(meta)
        return docs

    if ext in {".xlsx", ".xls"}:
        import pandas as pd
        try:
            sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        except Exception:
            # pandas/openpyxl handles xlsx; xlrd handles legacy xls when installed.
            sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None, engine=None)
        docs = []
        for sheet, df in sheets.items():
            df = df.fillna("")
            text = f"Workbook: {filename}\nSheet: {sheet}\n\n"
            text += df.to_csv(index=False)
            docs.append(Document(page_content=text, metadata={**meta, "sheet": str(sheet)}))
        return docs

    if ext in {".csv", ".tsv"}:
        import pandas as pd
        sep = "\t" if ext == ".tsv" else ","
        df = pd.read_csv(io.BytesIO(file_bytes), sep=sep).fillna("")
        text = f"File: {filename}\n\n{df.to_csv(index=False)}"
        return [Document(page_content=text, metadata=meta)]

    if ext in {".pptx", ".ppt"}:
        try:
            from langchain_community.document_loaders import UnstructuredPowerPointLoader
            path = _tmp_file(file_bytes, ext)
            try: docs = UnstructuredPowerPointLoader(path).load()
            finally: os.unlink(path)
        except Exception:
            from pptx import Presentation
            prs = Presentation(io.BytesIO(file_bytes))
            docs = []
            for i, slide in enumerate(prs.slides, 1):
                texts = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        texts.append(shape.text)
                docs.append(Document(
                    page_content="\n".join(texts),
                    metadata={**meta, "slide": i}
                ))
        for i, d in enumerate(docs, 1):
            d.metadata.update(meta)
            d.metadata.setdefault("slide", i)
        return docs

    if ext in {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}:
        text = image_to_text(file_bytes)
        return [Document(
            page_content=text or "No readable text was extracted from this image.",
            metadata={**meta, "ocr": True}
        )]

    if ext in {".html", ".htm"}:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(file_bytes.decode("utf-8", errors="ignore"), "html.parser")
        return [Document(page_content=soup.get_text("\n", strip=True), metadata=meta)]

    if ext in {".json", ".xml"}:
        text = file_bytes.decode("utf-8", errors="ignore")
        if ext == ".json":
            try: text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
            except Exception: pass
        return [Document(page_content=text, metadata=meta)]

    text = file_bytes.decode("utf-8", errors="ignore")
    return [Document(page_content=text, metadata=meta)]
