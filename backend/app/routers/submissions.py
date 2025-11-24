from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Assignment, Submission, Answer, Question, StudentProfile
from app.schemas import SubmissionCreate, SubmissionResponse, AnswerResult
from app.auth import get_current_student, get_current_user
from app.grading import grade_answer

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

    # Get all questions for this assignment
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    question_dict = {q.id: q for q in questions}

    # Validate all questions are answered
    submitted_question_ids = {a.question_id for a in submission_data.answers}
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

    for answer_data in submission_data.answers:
        question = question_dict[answer_data.question_id]
        is_correct, score = grade_answer(
            question.question_type,
            question.correct_answer,
            answer_data.student_answer
        )

        answer = Answer(
            submission_id=submission.id,
            question_id=answer_data.question_id,
            student_answer=answer_data.student_answer,
            ai_score=score,
            ai_is_correct=is_correct
        )
        db.add(answer)
        total_score += score

        answer_results.append(AnswerResult(
            question_id=answer_data.question_id,
            student_answer=answer_data.student_answer,
            correct_answer=question.correct_answer,
            ai_is_correct=is_correct,
            ai_score=score
        ))

    db.commit()

    avg_score = total_score / num_questions if num_questions > 0 else 0.0

    return SubmissionResponse(
        submission_id=submission.id,
        total_score=avg_score,
        answers=answer_results
    )

