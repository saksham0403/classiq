from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Classroom, StudentProfile, Assignment, Submission, Answer, Question
from app.schemas import (
    ClassroomCreate, ClassroomResponse, AddStudentRequest, 
    StudentProfileResponse, UserResponse, AssignmentResponse
)
from app.auth import get_current_teacher, get_current_user

router = APIRouter()


@router.post("/", response_model=ClassroomResponse)
def create_classroom(
    classroom_data: ClassroomCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    new_classroom = Classroom(
        name=classroom_data.name,
        teacher_id=current_user.id
    )
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)
    return ClassroomResponse.model_validate(new_classroom)


@router.get("/", response_model=List[ClassroomResponse])
def list_classrooms(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    classrooms = db.query(Classroom).filter(Classroom.teacher_id == current_user.id).all()
    return [ClassroomResponse.model_validate(c) for c in classrooms]


@router.post("/{classroom_id}/students", response_model=StudentProfileResponse)
def add_student(
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    # Find student user
    student_user = db.query(User).filter(
        User.email == student_data.student_email,
        User.role == "student"
    ).first()
    if not student_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found. Student must sign up first."
        )

    # Check if already enrolled
    existing = db.query(StudentProfile).filter(
        StudentProfile.user_id == student_user.id,
        StudentProfile.classroom_id == classroom_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already enrolled")

    # Create student profile
    profile = StudentProfile(
        user_id=student_user.id,
        classroom_id=classroom_id
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Return with student data
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        classroom_id=profile.classroom_id,
        student=UserResponse.model_validate(student_user)
    )


@router.get("/{classroom_id}/students", response_model=List[StudentProfileResponse])
def list_students(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access: teacher owns classroom OR student is enrolled
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    if current_user.role == "teacher":
        if classroom.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your classroom")
    else:  # student
        enrolled = db.query(StudentProfile).filter(
            StudentProfile.user_id == current_user.id,
            StudentProfile.classroom_id == classroom_id
        ).first()
        if not enrolled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this classroom")

    profiles = db.query(StudentProfile).filter(StudentProfile.classroom_id == classroom_id).all()
    result = []
    for profile in profiles:
        student_user = db.query(User).filter(User.id == profile.user_id).first()
        result.append(StudentProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            classroom_id=profile.classroom_id,
            student=UserResponse.model_validate(student_user)
        ))
    return result


@router.get("/{classroom_id}/assignments", response_model=List[AssignmentResponse])
def list_classroom_assignments(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    if current_user.role == "teacher":
        if classroom.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your classroom")
    else:  # student
        enrolled = db.query(StudentProfile).filter(
            StudentProfile.user_id == current_user.id,
            StudentProfile.classroom_id == classroom_id
        ).first()
        if not enrolled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled")

    assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    return [AssignmentResponse.model_validate(a) for a in assignments]


@router.get("/{classroom_id}/students/{student_id}/submissions")
def get_student_submissions_in_classroom(
    classroom_id: int,
    student_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all submissions from a student for all assignments in this classroom"""
    # Verify classroom belongs to teacher
    classroom = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    
    # Verify student is enrolled in this classroom
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student_id,
        StudentProfile.classroom_id == classroom_id
    ).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found in this classroom")
    
    # Get student info
    student = db.query(User).filter(User.id == student_id).first()
    
    # Get all assignments in this classroom
    assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    assignment_dict = {a.id: a for a in assignments}
    
    # Get all submissions from this student for assignments in this classroom
    assignment_ids = [a.id for a in assignments]
    submissions = db.query(Submission).filter(
        Submission.student_id == student_id,
        Submission.assignment_id.in_(assignment_ids)
    ).all()
    
    # Get all questions for these assignments
    questions = db.query(Question).filter(Question.assignment_id.in_(assignment_ids)).all()
    question_dict = {q.id: q for q in questions}
    
    # Build submission details
    submission_details = []
    for submission in submissions:
        assignment = assignment_dict.get(submission.assignment_id)
        if not assignment:
            continue
        
        # Get answers for this submission
        answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
        
        # Calculate score
        total_score = sum(a.ai_score for a in answers if a.ai_score) if answers else 0.0
        avg_score = total_score / len(answers) if answers else 0.0
        
        # Get answer details
        answer_details = []
        for answer in answers:
            question = question_dict.get(answer.question_id)
            answer_details.append({
                "question_id": answer.question_id,
                "question_text": question.text if question else "",
                "student_answer": answer.student_answer,
                "correct_answer": question.correct_answer if question else "",
                "ai_is_correct": answer.ai_is_correct,
                "ai_score": answer.ai_score,
                "question_type": question.question_type.value if question else "",
                "topic_tag": question.topic_tag if question else ""
            })
        
        submission_details.append({
            "submission_id": submission.id,
            "assignment_id": assignment.id,
            "assignment_title": assignment.title,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "score": avg_score,
            "answers": answer_details
        })
    
    return {
        "student": UserResponse.model_validate(student),
        "submissions": submission_details
    }

