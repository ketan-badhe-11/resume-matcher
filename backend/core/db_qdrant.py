from typing import List, Dict, Any
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "resumes")

_client: QdrantClient = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def ensure_collection(vector_size: int):
    client = get_client()
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        )


def upsert_embedding(employee_id: str, vector: List[float]) -> int:
    client = get_client()
    point_id = hash(employee_id) & 0x7FFFFFFF
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[models.PointStruct(id=point_id, vector=vector, payload={"employee_id": employee_id})]
    )
    return point_id


def search(vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    client = get_client()
    results = client.search(collection_name=COLLECTION_NAME, query_vector=vector, limit=top_k)
    out = []
    for r in results:
        out.append({
            "employee_id": r.payload.get("employee_id"),
            "score": r.score
        })
    return out
