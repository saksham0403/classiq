from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, classrooms, assignments, submissions, analytics, students
from app.models import *  # Import all models so they're registered with Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ClassIQ API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(classrooms.router, prefix="/classrooms", tags=["classrooms"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(submissions.router, prefix="/assignments", tags=["submissions"])
app.include_router(analytics.router, prefix="", tags=["analytics"])
app.include_router(students.router, prefix="/students", tags=["students"])


@app.get("/")
def root():
    return {"message": "ClassIQ API"}
