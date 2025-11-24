"""
File upload endpoint for OCR-based submissions.
"""
import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Assignment, Submission, Answer, Question, StudentProfile
from app.schemas import SubmissionResponse, AnswerResult
from app.auth import get_current_student
from app.grading import grade_answer
from app.services.ocr import extract_text_from_file, clean_ocr_text
from app.services.answer_extraction import extract_student_answers

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
    submitted_question_ids = {a["question_id"] for a in answers_data}
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
        question = question_dict[answer_data["question_id"]]
        is_correct, score = grade_answer(
            question.question_type,
            question.correct_answer,
            answer_data["student_answer"]
        )
        
        answer = Answer(
            submission_id=submission.id,
            question_id=answer_data["question_id"],
            student_answer=answer_data["student_answer"],
            ai_score=score,
            ai_is_correct=is_correct
        )
        db.add(answer)
        total_score += score
        
        answer_results.append(AnswerResult(
            question_id=answer_data["question_id"],
            student_answer=answer_data["student_answer"],
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


@router.post("/{assignment_id}/upload", response_model=dict)
async def upload_and_grade(
    assignment_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Upload an image or PDF, extract text via OCR, extract answers, and grade.
    Returns submission results similar to typed submission.
    """
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
    
    # Validate file type
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.gif', '.bmp', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save file temporarily
    temp_file = None
    try:
        # Create temp file
        suffix = file_ext
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            # Read and write file content
            content = await file.read()
            tmp.write(content)
        
        # Extract text using OCR
        raw_text = await extract_text_from_file(temp_file)
        cleaned_text = clean_ocr_text(raw_text)
        
        # Get assignment questions
        questions = db.query(Question).filter(Question.assignment_id == assignment_id).order_by(Question.id).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignment has no questions"
            )
        
        # Extract answers from OCR text
        answers_data = extract_student_answers(cleaned_text, questions)
        
        # Process submission using existing logic
        submission_result = await _process_submission(
            assignment_id,
            answers_data,
            current_user,
            db
        )
        
        return {
            "source": "ocr",
            "submission_id": submission_result.submission_id,
            "total_score": submission_result.total_score,
            "answers": [
                {
                    "answer_id": a.answer_id,
                    "question_id": a.question_id,
                    "student_answer": a.student_answer,
                    "correct_answer": a.correct_answer,
                    "ai_is_correct": a.ai_is_correct,
                    "ai_score": a.ai_score
                }
                for a in submission_result.answers
            ],
            "ocr_text": cleaned_text  # Include for debugging
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OCR processing failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload processing failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

