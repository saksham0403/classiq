"""
Feedback endpoint for generating LLM explanations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Answer, Question
from app.auth import get_current_user
from app.services.llm_feedback import generate_feedback_ollama

router = APIRouter()


@router.post("/{answer_id}/feedback", response_model=dict)
async def generate_feedback(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate LLM feedback for a specific answer.
    Student can only request feedback for their own answers.
    Teacher can request feedback for any answer.
    """
    # Get answer with submission relationship
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    
    # Get submission to check student_id
    from app.models import Submission
    submission = db.query(Submission).filter(Submission.id == answer.submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    # Get question
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    # Check permissions
    if current_user.role == "student":
        # Student can only view their own answers
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only request feedback for your own answers"
            )
    # Teachers can view any answer (no additional check needed)
    
    # If feedback already exists, return it
    if answer.ai_feedback:
        return {
            "answer_id": answer_id,
            "feedback": answer.ai_feedback,
            "cached": True
        }
    
    # Generate new feedback
    try:
        feedback_text = await generate_feedback_ollama(
            question_text=question.text,
            correct_answer=question.correct_answer,
            student_answer=answer.student_answer,
            is_correct=answer.ai_is_correct or False
        )
        
        # Save feedback to database
        answer.ai_feedback = feedback_text
        db.commit()
        db.refresh(answer)
        
        return {
            "answer_id": answer_id,
            "feedback": feedback_text,
            "cached": False
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )

