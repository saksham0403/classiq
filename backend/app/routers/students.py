from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Assignment, StudentProfile
from app.schemas import AssignmentResponse
from app.auth import get_current_student

router = APIRouter()


@router.get("/me/assignments", response_model=List[AssignmentResponse])
def get_my_assignments(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get all assignments from classrooms where the student is enrolled."""
    # Get all classrooms where student is enrolled
    profiles = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).all()
    
    classroom_ids = [p.classroom_id for p in profiles]
    
    if not classroom_ids:
        return []
    
    # Get all assignments from these classrooms
    assignments = db.query(Assignment).filter(
        Assignment.classroom_id.in_(classroom_ids)
    ).all()
    
    return [AssignmentResponse.model_validate(a) for a in assignments]

