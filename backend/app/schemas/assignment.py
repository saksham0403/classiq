from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.assignment import AssignmentStatus
from app.models.question import QuestionType

class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    classroom_id: int

class AssignmentResponse(AssignmentBase):
    id: int
    classroom_id: int
    status: AssignmentStatus
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    text: str
    correct_answer: str
    question_type: QuestionType
    topic_tag: str

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    assignment_id: int

    class Config:
        from_attributes = True

class AssignmentStatusUpdate(BaseModel):
    status: AssignmentStatus

class AssignmentWithQuestions(AssignmentResponse):
    questions: List[QuestionResponse] = []

