import io
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import magic
from docx import Document
import subprocess
import tempfile
import os
from typing import Tuple

try:
    from tika import parser as tika_parser  # type: ignore
except Exception:  # pragma: no cover
    tika_parser = None

_OCR = None

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
IMAGE_MIMES = {"image/jpeg", "image/png"}


def get_ocr():
    global _OCR
    if _OCR is None:
        # Assumes PaddleOCR models placed under backend/local_models/ocr if custom, else default download
        _OCR = PaddleOCR(use_angle_cls=True, lang='en')
    return _OCR


def detect_mime(data: bytes) -> str:
    return magic.from_buffer(data, mime=True)


def extract_pdf_text(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype='pdf')
    text_parts = []
    for page in doc:
        text = page.get_text("text")
        if text:
            text_parts.append(text)
    full_text = "\n".join(text_parts).strip()
    # Heuristic: if too little text, treat as scanned and OCR
    if len(full_text) < 100:
        images_text = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            ocr = get_ocr()
            result = ocr.ocr(io.BytesIO(img_bytes))
            page_text = " ".join([line[1][0] for line in result[0]]) if result else ""
            images_text.append(page_text)
        return "\n".join(images_text)
    return full_text


def extract_docx_text(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)


def extract_image_text(data: bytes) -> str:
    ocr = get_ocr()
    result = ocr.ocr(io.BytesIO(data))
    if not result:
        return ""
    return " ".join([line[1][0] for line in result[0]])


def extract_with_tika(data: bytes) -> str:
    if tika_parser is None:
        return ""
    parsed = tika_parser.from_buffer(data)
    return (parsed.get('content') or '').strip()


def extract(data: bytes) -> Tuple[str, str]:
    """Return (text, mime) given file bytes."""
    mime = detect_mime(data)
    text = ""
    try:
        if mime == PDF_MIME:
            text = extract_pdf_text(data)
        elif mime == DOCX_MIME:
            text = extract_docx_text(data)
        elif mime in IMAGE_MIMES:
            text = extract_image_text(data)
        else:
            # Fallback try PyMuPDF if pdf signature
            if data[:4] == b'%PDF':
                text = extract_pdf_text(data)
            else:
                text = extract_with_tika(data)
    except Exception as e:  # pragma: no cover
        # final fallback
        if not text:
            text = extract_with_tika(data)
    return text.strip(), mime
