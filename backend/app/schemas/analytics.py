from pydantic import BaseModel
from typing import List, Optional

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

