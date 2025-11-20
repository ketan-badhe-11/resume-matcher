from typing import List
import os
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "local_models", "embeddings")


def get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        # Assumes local model directory contains necessary files
        _MODEL = SentenceTransformer(MODEL_PATH)
    return _MODEL


def embed_text(text: str) -> List[float]:
    model = get_model()
    vec = model.encode(text, show_progress_bar=False, normalize_embeddings=True)
    return vec.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_model()
    vecs = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [v.tolist() for v in vecs]


def embedding_dimension() -> int:
    model = get_model()
    return model.get_sentence_embedding_dimension()
