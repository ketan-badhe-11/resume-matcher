from fastapi import APIRouter

from .resumes import router as resumes_router
from .jd import router as jd_router
from .match import router as match_router

api_router = APIRouter()
api_router.include_router(resumes_router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jd_router, prefix="/jd", tags=["job_descriptions"])
api_router.include_router(match_router, prefix="/match", tags=["matching"])
