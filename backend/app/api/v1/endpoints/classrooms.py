from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.v1.dependencies import get_current_teacher, get_current_user
from app.models.user import User
from app.models.classroom import Classroom
from app.models.student_profile import StudentProfile
from app.schemas.classroom import (
    ClassroomCreate, 
    ClassroomResponse, 
    AddStudentRequest,
    StudentInClassroom
)

router = APIRouter()

@router.post("/", response_model=ClassroomResponse)
def create_classroom(
    classroom_data: ClassroomCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    classroom = Classroom(
        name=classroom_data.name,
        teacher_id=current_user.id
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom

@router.get("/", response_model=List[ClassroomResponse])
def list_classrooms(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    classrooms = db.query(Classroom).filter(Classroom.teacher_id == current_user.id).all()
    return classrooms

@router.post("/{classroom_id}/students")
def add_student_to_classroom(
    classroom_id: int,
    student_data: AddStudentRequest,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # Verify classroom belongs to teacher
    classroom = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Find student by email
    student = db.query(User).filter(
        User.email == student_data.student_email,
        User.role == "student"
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if already enrolled
    existing_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student.id,
        StudentProfile.classroom_id == classroom_id
    ).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled in this classroom"
        )
    
    # Create student profile
    profile = StudentProfile(
        user_id=student.id,
        classroom_id=classroom_id
    )
    db.add(profile)
    db.commit()
    return {"message": "Student added successfully"}

@router.get("/{classroom_id}/students", response_model=List[StudentInClassroom])
def list_classroom_students(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access: teacher owns classroom or student is enrolled
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    if current_user.role == "teacher":
        if classroom.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    else:  # student
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == current_user.id,
            StudentProfile.classroom_id == classroom_id
        ).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enrolled in this classroom"
            )
    
    # Get students
    profiles = db.query(StudentProfile).filter(
        StudentProfile.classroom_id == classroom_id
    ).all()
    
    students = [profile.student for profile in profiles]
    return [StudentInClassroom.model_validate(s) for s in students]

