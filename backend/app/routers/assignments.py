from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Assignment, Question, Classroom, StudentProfile, Submission, Answer
from app.schemas import (
    AssignmentCreate, AssignmentResponse, QuestionCreate, QuestionResponse,
    AssignmentWithQuestions, AssignmentStatusUpdate, UserResponse, AnswerResponse
)
from app.auth import get_current_teacher, get_current_user

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    new_assignment = Assignment(
        classroom_id=assignment_data.classroom_id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return AssignmentResponse.model_validate(new_assignment)




@router.get("/{assignment_id}", response_model=AssignmentWithQuestions)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    # Verify access
    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()
    if current_user.role == "teacher":
        if classroom.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your classroom")
    else:  # student
        enrolled = db.query(StudentProfile).filter(
            StudentProfile.user_id == current_user.id,
            StudentProfile.classroom_id == assignment.classroom_id
        ).first()
        if not enrolled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled")

    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    return AssignmentWithQuestions(
        id=assignment.id,
        classroom_id=assignment.classroom_id,
        title=assignment.title,
        description=assignment.description,
        status=assignment.status,
        created_at=assignment.created_at,
        due_date=assignment.due_date,
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )


@router.patch("/{assignment_id}/status", response_model=AssignmentResponse)
def update_assignment_status(
    assignment_id: int,
    status_update: AssignmentStatusUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Update assignment status (draft -> open -> graded)"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    # Verify assignment belongs to teacher's classroom
    classroom = db.query(Classroom).filter(
        Classroom.id == assignment.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your assignment")

    assignment.status = status_update.status
    db.commit()
    db.refresh(assignment)
    return AssignmentResponse.model_validate(assignment)


@router.get("/{assignment_id}/submissions", response_model=List[dict])
def get_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get list of students who submitted this assignment"""
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    # Verify assignment belongs to teacher's classroom
    classroom = db.query(Classroom).filter(
        Classroom.id == assignment.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your assignment")

    # Get all submissions for this assignment
    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    
    result = []
    for submission in submissions:
        student = db.query(User).filter(User.id == submission.student_id).first()
        # Calculate average score
        answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
        avg_score = sum(a.ai_score for a in answers) / len(answers) if answers else 0.0
        
        result.append({
            "submission_id": submission.id,
            "student": UserResponse.model_validate(student),
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "score": avg_score
        })
    
    return result


@router.get("/{assignment_id}/submissions/{submission_id}", response_model=dict)
def get_student_submission(
    assignment_id: int,
    submission_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed submission from a specific student"""
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    # Verify assignment belongs to teacher's classroom
    classroom = db.query(Classroom).filter(
        Classroom.id == assignment.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your assignment")

    # Get submission
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.assignment_id == assignment_id
    ).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    # Get student info
    student = db.query(User).filter(User.id == submission.student_id).first()
    
    # Get all answers with question details
    answers = db.query(Answer).filter(Answer.submission_id == submission_id).all()
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    question_dict = {q.id: q for q in questions}
    
    answer_details = []
    total_score = 0.0
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
        total_score += answer.ai_score if answer.ai_score else 0.0
    
    avg_score = total_score / len(answers) if answers else 0.0
    
    return {
        "submission_id": submission.id,
        "student": UserResponse.model_validate(student),
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "total_score": avg_score,
        "answers": answer_details
    }


@router.post("/{assignment_id}/questions", response_model=QuestionResponse)
def add_question(
    assignment_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # Verify assignment belongs to teacher's classroom
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    classroom = db.query(Classroom).filter(
        Classroom.id == assignment.classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your assignment")

    new_question = Question(
        assignment_id=assignment_id,
        text=question_data.text,
        correct_answer=question_data.correct_answer,
        question_type=question_data.question_type,
        topic_tag=question_data.topic_tag
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return QuestionResponse.model_validate(new_question)

