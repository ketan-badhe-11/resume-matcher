"""Utility script to download and stage local models.
Run: python backend/scripts/download_models.py

Environment variables (optional):
  SENTENCE_MODEL_NAME  (default: sentence-transformers/all-MiniLM-L6-v2)
  EMBEDDINGS_DIR       (default: backend/local_models/embeddings)

This script:
  - Downloads SentenceTransformer model into embeddings dir if empty.
  - Creates OCR directory structure placeholders (does NOT auto-download PaddleOCR tar files).

For PaddleOCR manual download, see MODELS.md.
"""
import os
import sys
from pathlib import Path

DEFAULT_MODEL = os.getenv("SENTENCE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIR = Path(os.getenv("EMBEDDINGS_DIR", "backend/local_models/embeddings"))
OCR_BASE = Path("backend/local_models/ocr")


def ensure_embedding_model():
    if any(EMBED_DIR.iterdir()):
        print(f"[skip] Embeddings directory not empty: {EMBED_DIR}")
        return
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers not installed. Run: pip install sentence-transformers")
        return
    print(f"[download] Fetching model {DEFAULT_MODEL} ...")
    model = SentenceTransformer(DEFAULT_MODEL)
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    model.save(str(EMBED_DIR))
    print(f"[done] Saved model to {EMBED_DIR}")
    print(f"Dimension: {model.get_sentence_embedding_dimension()}")


def prepare_ocr_dirs():
    for sub in ["det", "rec", "cls"]:
        p = OCR_BASE / sub
        p.mkdir(parents=True, exist_ok=True)
    print(f"[info] Created OCR directory placeholders under {OCR_BASE}")
    print("[next] Download tar files (see MODELS.md) and extract into respective subfolders.")


def main():
    os.chdir(Path(__file__).resolve().parents[2])  # move to project root
    ensure_embedding_model()
    prepare_ocr_dirs()
    print("[summary] Model prep complete.")

if __name__ == "__main__":
    main()
