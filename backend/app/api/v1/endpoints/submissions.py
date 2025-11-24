from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_student, get_current_user
from app.models.user import User
from app.models.assignment import Assignment
from app.models.question import Question
from app.models.submission import Submission
from app.models.answer import Answer
from app.models.student_profile import StudentProfile
from app.schemas.submission import SubmissionCreate, SubmissionResponse, AnswerResponse
from app.services.grading import grade_answer

router = APIRouter()

@router.post("/{assignment_id}/submissions", response_model=SubmissionResponse)
def submit_assignment(
    assignment_id: int,
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Verify assignment exists and student is enrolled
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    classroom = assignment.classroom
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id,
        StudentProfile.classroom_id == classroom.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this classroom"
        )
    
    # Check if already submitted
    existing_submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    ).first()
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already submitted"
        )
    
    # Get all questions for this assignment
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    question_dict = {q.id: q for q in questions}
    
    # Validate all question IDs
    for answer_data in submission_data.answers:
        if answer_data.question_id not in question_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {answer_data.question_id} not found in this assignment"
            )
    
    # Create submission
    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Grade and save answers
    answer_responses = []
    total_score = 0.0
    num_answers = 0
    
    for answer_data in submission_data.answers:
        question = question_dict[answer_data.question_id]
        is_correct, score = grade_answer(
            question.question_type,
            question.correct_answer,
            answer_data.student_answer
        )
        
        answer = Answer(
            submission_id=submission.id,
            question_id=question.id,
            student_answer=answer_data.student_answer,
            ai_score=score,
            ai_is_correct=is_correct
        )
        db.add(answer)
        
        answer_responses.append(AnswerResponse(
            question_id=question.id,
            student_answer=answer_data.student_answer,
            correct_answer=question.correct_answer,
            ai_is_correct=is_correct,
            ai_score=score,
            feedback=None
        ))
        
        total_score += score
        num_answers += 1
    
    db.commit()
    
    # Calculate average score
    avg_score = total_score / num_answers if num_answers > 0 else 0.0
    
    return SubmissionResponse(
        submission_id=submission.id,
        total_score=avg_score,
        answers=answer_responses
    )

