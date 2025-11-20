from typing import Dict, Any, Optional, List
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "resume_matcher")

_client: Optional[MongoClient] = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[DB_NAME]
    return _db


def insert_resume(profile: Dict[str, Any]) -> str:
    db = get_db()
    res = db.resumes.insert_one(profile)
    return str(res.inserted_id)


def update_resume(query: Dict[str, Any], update: Dict[str, Any]):
    db = get_db()
    db.resumes.update_one(query, {"$set": update})


def insert_jd(jd: Dict[str, Any]) -> str:
    db = get_db()
    res = db.job_descriptions.insert_one(jd)
    return str(res.inserted_id)


def list_resumes() -> List[Dict[str, Any]]:
    db = get_db()
    return list(db.resumes.find())


def get_resume_by_employee(employee_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    return db.resumes.find_one({"employee_id": employee_id})
