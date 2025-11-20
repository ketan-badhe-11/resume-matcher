from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid

from ..core import extractor, cleaner, classifier, skill_extractor, experience_extractor, embedder, db_mongo, db_qdrant

router = APIRouter()

class UploadResponse(BaseModel):
    employee_id: str
    embedding_id: int


@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    text, mime = extractor.extract(data)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text")
    cleaned = cleaner.clean_text(text)
    sections = classifier.classify_sections(cleaned)
    skills = skill_extractor.extract_skills(cleaned)
    experience_years = experience_extractor.compute_years(cleaned)

    employee_id = str(uuid.uuid4())
    vec = embedder.embed_text(cleaned)
    embed_dim = len(vec)
    db_qdrant.ensure_collection(embed_dim)
    embedding_id = db_qdrant.upsert_embedding(employee_id, vec)

    profile = {
        "employee_id": employee_id,
        "raw_text": text,
        "cleaned_text": cleaned,
        "sections": sections,
        "skills": skills,
        "experience_years": experience_years,
        "embedding_id": embedding_id,
        "mime": mime,
        "filename": file.filename,
    }
    db_mongo.insert_resume(profile)
    return UploadResponse(employee_id=employee_id, embedding_id=embedding_id)


@router.get("/profile/{employee_id}")
async def get_profile(employee_id: str):
    prof = db_mongo.get_resume_by_employee(employee_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Not found")
    prof.pop('_id', None)
    return prof


@router.get("/export/{employee_id}")
async def export_resume(employee_id: str):
    """Simplified export: returns structured data. (Docx/PDF generation handled separately)."""
    prof = db_mongo.get_resume_by_employee(employee_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Not found")
    prof.pop('_id', None)
    return prof
