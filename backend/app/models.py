from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class AssignmentStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    GRADED = "graded"


class QuestionType(str, enum.Enum):
    NUMERIC = "numeric"
    ALGEBRA = "algebra"
    SHORT_ANSWER = "short_answer"
    MCQ = "mcq"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    classrooms = relationship("Classroom", back_populates="teacher")
    student_profiles = relationship("StudentProfile", back_populates="student")
    submissions = relationship("Submission", back_populates="student")


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("User", back_populates="classrooms")
    student_profiles = relationship("StudentProfile", back_populates="classroom")
    assignments = relationship("Assignment", back_populates="classroom")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)

    # Relationships
    student = relationship("User", back_populates="student_profiles")
    classroom = relationship("Classroom", back_populates="student_profiles")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    classroom = relationship("Classroom", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    topic_tag = Column(String, nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_answer = Column(Text, nullable=False)
    ai_score = Column(Float, nullable=True)
    ai_is_correct = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)

    # Relationships
    submission = relationship("Submission", back_populates="answers")
    question = relationship("Question", back_populates="answers")

