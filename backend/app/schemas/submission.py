from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerSubmission(BaseModel):
    question_id: int
    student_answer: str

class SubmissionCreate(BaseModel):
    answers: List[AnswerSubmission]

class AnswerResponse(BaseModel):
    question_id: int
    student_answer: str
    correct_answer: str
    ai_is_correct: bool
    ai_score: float
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionResponse(BaseModel):
    submission_id: int
    total_score: float
    answers: List[AnswerResponse]

