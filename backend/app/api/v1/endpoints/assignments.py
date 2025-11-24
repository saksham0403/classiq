from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.v1.dependencies import get_current_teacher, get_current_user
from app.models.user import User
from app.models.classroom import Classroom
from app.models.assignment import Assignment, AssignmentStatus
from app.models.question import Question
from app.models.student_profile import StudentProfile
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    QuestionCreate,
    QuestionResponse,
    AssignmentWithQuestions
)

router = APIRouter()

@router.post("/", response_model=AssignmentResponse)
def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # Verify classroom belongs to teacher
    classroom = db.query(Classroom).filter(
        Classroom.id == assignment_data.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    assignment = Assignment(
        classroom_id=assignment_data.classroom_id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date,
        status=AssignmentStatus.DRAFT
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

@router.get("/classrooms/{classroom_id}/assignments", response_model=List[AssignmentResponse])
def list_classroom_assignments(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access
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
    
    assignments = db.query(Assignment).filter(
        Assignment.classroom_id == classroom_id
    ).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentWithQuestions)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Verify access
    classroom = assignment.classroom
    if current_user.role == "teacher":
        if classroom.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    else:  # student
        profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == current_user.id,
            StudentProfile.classroom_id == classroom.id
        ).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enrolled in this classroom"
            )
    
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    return AssignmentWithQuestions(
        **assignment.__dict__,
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )

@router.post("/{assignment_id}/questions", response_model=QuestionResponse)
def add_question(
    assignment_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # Verify assignment belongs to teacher
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    classroom = assignment.classroom
    if classroom.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    question = Question(
        assignment_id=assignment_id,
        text=question_data.text,
        correct_answer=question_data.correct_answer,
        question_type=question_data.question_type,
        topic_tag=question_data.topic_tag
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

