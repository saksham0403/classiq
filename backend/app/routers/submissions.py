from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Assignment, Submission, Answer, Question, StudentProfile
from app.schemas import SubmissionCreate, SubmissionResponse, AnswerResult
from app.auth import get_current_student, get_current_user
from app.grading import grade_answer

router = APIRouter()


async def _process_submission(
    assignment_id: int,
    answers_data: list,
    current_user: User,
    db: Session
) -> SubmissionResponse:
    """
    Helper function to process submission (shared between typed and OCR submissions).
    """
    # Get all questions for this assignment
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    question_dict = {q.id: q for q in questions}
    
    # Validate all questions are answered
    submitted_question_ids = {a.get("question_id") if isinstance(a, dict) else a.question_id for a in answers_data}
    required_question_ids = {q.id for q in questions}
    if submitted_question_ids != required_question_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must answer all questions"
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
    answer_results = []
    total_score = 0.0
    num_questions = len(questions)
    
    for answer_data in answers_data:
        # Handle both dict and AnswerSubmission objects
        if isinstance(answer_data, dict):
            question_id = answer_data["question_id"]
            student_answer = answer_data["student_answer"]
        else:
            question_id = answer_data.question_id
            student_answer = answer_data.student_answer
        
        question = question_dict[question_id]
        is_correct, score = grade_answer(
            question.question_type,
            question.correct_answer,
            student_answer
        )
        
        answer = Answer(
            submission_id=submission.id,
            question_id=question_id,
            student_answer=student_answer,
            ai_score=score,
            ai_is_correct=is_correct
        )
        db.add(answer)
        total_score += score
        
        # Create AnswerResult with answer_id
        answer_result = AnswerResult(
            answer_id=answer.id,  # Include answer ID for feedback requests
            question_id=question_id,
            student_answer=student_answer,
            correct_answer=question.correct_answer,
            ai_is_correct=is_correct,
            ai_score=score
        )
        answer_results.append(answer_result)
    
    db.commit()
    
    avg_score = total_score / num_questions if num_questions > 0 else 0.0
    
    return SubmissionResponse(
        submission_id=submission.id,
        total_score=avg_score,
        answers=answer_results
    )


@router.post("/{assignment_id}/submissions", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Verify assignment exists and student is enrolled
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    enrolled = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id,
        StudentProfile.classroom_id == assignment.classroom_id
    ).first()
    if not enrolled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this classroom")

    # Check if already submitted
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already submitted")

    # Convert AnswerSubmission objects to dict format for shared function
    answers_data = [
        {"question_id": a.question_id, "student_answer": a.student_answer}
        for a in submission_data.answers
    ]
    
    # Use shared submission processing function
    return await _process_submission(assignment_id, answers_data, current_user, db)

