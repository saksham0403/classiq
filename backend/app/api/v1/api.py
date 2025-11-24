from fastapi import APIRouter
from app.api.v1.endpoints import auth, classrooms, assignments, submissions, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(classrooms.router, prefix="/classrooms", tags=["classrooms"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(submissions.router, prefix="/assignments", tags=["submissions"])
api_router.include_router(analytics.router, prefix="", tags=["analytics"])

