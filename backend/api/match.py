from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..core import db_mongo, db_qdrant, embedder

router = APIRouter()

class MatchRequest(BaseModel):
    jd_text: str
    top_k: int = 5
    skill_weight: float = 0.4
    exp_weight: float = 0.2
    embed_weight: float = 0.4

class CandidateMatch(BaseModel):
    employee_id: str
    final_score: float
    embedding_score: float
    skill_score: float
    experience_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_years: float
    summary: str

class MatchResponse(BaseModel):
    results: List[CandidateMatch]


def compute_skill_score(required: List[str], candidate: List[str]) -> (float, List[str], List[str]):
    req_set = set(s.lower() for s in required)
    cand_set = set(s.lower() for s in candidate)
    matched = req_set & cand_set
    score = len(matched) / len(req_set) if req_set else 0.0
    return score, [m.capitalize() for m in matched], [r.capitalize() for r in req_set - matched]

@router.post("/run", response_model=MatchResponse)
async def run_match(req: MatchRequest):
    jd_vec = embedder.embed_text(req.jd_text)
    # naive required skills extraction (reuse skill extractor logic via Mongo skill dict if stored) - placeholder
    from ..core.skill_extractor import extract_skills
    required_skills = extract_skills(req.jd_text)

    # search similar embeddings
    results = db_qdrant.search(jd_vec, top_k=req.top_k * 2)  # get extra for filtering
    candidates: List[CandidateMatch] = []
    for r in results:
        prof = db_mongo.get_resume_by_employee(r['employee_id'])
        if not prof:
            continue
        cand_skills = prof.get('skills', [])
        skill_score, matched, missing = compute_skill_score(required_skills, cand_skills)
        exp_years = prof.get('experience_years', 0.0)
        # attempt to parse JD min experience from text (simple pattern)
        import re
        m = re.search(r"(\d+)\s+years", req.jd_text, re.IGNORECASE)
        jd_min_exp = float(m.group(1)) if m else 0.0
        experience_score = min(exp_years / jd_min_exp, 1.0) if jd_min_exp > 0 else 0.0
        embedding_score = r['score']  # already cosine similarity
        final = (skill_score * req.skill_weight) + (experience_score * req.exp_weight) + (embedding_score * req.embed_weight)
        candidates.append(CandidateMatch(
            employee_id=r['employee_id'],
            final_score=round(final, 4),
            embedding_score=round(embedding_score, 4),
            skill_score=round(skill_score, 4),
            experience_score=round(experience_score, 4),
            matched_skills=matched,
            missing_skills=missing,
            experience_years=exp_years,
            summary=prof.get('sections', {}).get('summary', '')[:500]
        ))
    # rank and cut top_k
    candidates.sort(key=lambda c: c.final_score, reverse=True)
    return MatchResponse(results=candidates[:req.top_k])
