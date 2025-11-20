from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import re

from ..core import skill_extractor, experience_extractor, embedder, db_mongo

router = APIRouter()

class JDRequest(BaseModel):
    text: str

class JDResponse(BaseModel):
    jd_id: str
    skills: List[str]
    min_experience: float
    embedding_dim: int

MIN_EXP_REGEX = re.compile(r"minimum\s+(\d+(?:\.\d+)?)\s+years", re.IGNORECASE)
SENIORITY_REGEX = re.compile(r"(junior|sr\.?|senior|lead|principal)", re.IGNORECASE)


def extract_min_experience(text: str) -> float:
    m = MIN_EXP_REGEX.search(text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    return 0.0


def extract_seniority(text: str) -> str:
    m = SENIORITY_REGEX.search(text)
    return m.group(1).lower() if m else ""

@router.post("/process-jd", response_model=JDResponse)
async def process_jd(req: JDRequest):
    jd_text = req.text
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Empty JD text")
    skills = skill_extractor.extract_skills(jd_text)
    min_exp = extract_min_experience(jd_text)
    seniority = extract_seniority(jd_text)
    vec = embedder.embed_text(jd_text)
    jd_id = str(uuid.uuid4())
    jd_doc = {
        "jd_id": jd_id,
        "raw_text": jd_text,
        "skills": skills,
        "min_experience": min_exp,
        "seniority": seniority,
        "embedding": vec,
    }
    db_mongo.insert_jd(jd_doc)
    return JDResponse(jd_id=jd_id, skills=skills, min_experience=min_exp, embedding_dim=len(vec))
