from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, AssignmentStatus, QuestionType


# Auth schemas
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Classroom schemas
class ClassroomCreate(BaseModel):
    name: str


class ClassroomResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AddStudentRequest(BaseModel):
    student_email: EmailStr


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    classroom_id: int
    student: UserResponse

    class Config:
        from_attributes = True


# Assignment schemas
class AssignmentCreate(BaseModel):
    classroom_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    id: int
    classroom_id: int
    title: str
    description: Optional[str]
    status: AssignmentStatus
    created_at: datetime
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


# Question schemas
class QuestionCreate(BaseModel):
    text: str
    correct_answer: str
    question_type: QuestionType
    topic_tag: str


class QuestionResponse(BaseModel):
    id: int
    assignment_id: int
    text: str
    correct_answer: str
    question_type: QuestionType
    topic_tag: str

    class Config:
        from_attributes = True


class AssignmentWithQuestions(BaseModel):
    id: int
    classroom_id: int
    title: str
    description: Optional[str]
    status: AssignmentStatus
    created_at: datetime
    due_date: Optional[datetime]
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True


# Submission schemas
class AnswerSubmission(BaseModel):
    question_id: int
    student_answer: str


class SubmissionCreate(BaseModel):
    answers: List[AnswerSubmission]


class AnswerResult(BaseModel):
    question_id: int
    student_answer: str
    correct_answer: str
    ai_is_correct: bool
    ai_score: float
    feedback: Optional[str] = None


class SubmissionResponse(BaseModel):
    submission_id: int
    total_score: float
    answers: List[AnswerResult]


# Analytics schemas
class AssignmentSummary(BaseModel):
    assignment_id: int
    title: str
    avg_score: float


class TopicPerformance(BaseModel):
    topic: str
    accuracy: float


class HardestQuestion(BaseModel):
    question_id: int
    text: str
    percent_correct: float


class ClassroomAnalytics(BaseModel):
    assignment_summary: List[AssignmentSummary]
    topics: List[TopicPerformance]
    hardest_questions: List[HardestQuestion]


class RecommendedPractice(BaseModel):
    topic: str
    question_text: str
    type: str


class StudentSummary(BaseModel):
    overall_score: float
    strengths: List[str]
    weak_topics: List[str]
    recommended_practice: List[RecommendedPractice]

