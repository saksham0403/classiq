from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class QuestionType(str, enum.Enum):
    NUMERIC = "numeric"
    ALGEBRA = "algebra"
    SHORT_ANSWER = "short_answer"
    MCQ = "mcq"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    topic_tag = Column(String, nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

