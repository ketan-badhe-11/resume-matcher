from fastapi import FastAPI
from .api import api_router
from .core import embedder, db_qdrant
import spacy
import os

app = FastAPI(title="Resume Matcher", version="0.1.0")
app.include_router(api_router)

_NLP = None

@app.on_event("startup")
def startup_event():
    # Load spaCy model if available (optional for NER enhancements)
    global _NLP
    model_name = os.getenv("SPACY_MODEL", "en_core_web_sm")
    try:
        _NLP = spacy.load(model_name)
    except Exception:
        _NLP = None
    # Ensure Qdrant collection exists with model dimension
    dim = embedder.embedding_dimension()
    db_qdrant.ensure_collection(dim)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Resume Matcher API"}
