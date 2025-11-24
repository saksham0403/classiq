from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.schemas.classroom import ClassroomCreate, ClassroomResponse, AddStudentRequest, StudentInClassroom, StudentProfileResponse
from app.schemas.assignment import AssignmentCreate, AssignmentResponse, QuestionCreate, QuestionResponse, AssignmentWithQuestions, AssignmentStatusUpdate
from app.schemas.submission import SubmissionCreate, SubmissionResponse, AnswerSubmission, AnswerResponse
# Alias for backward compatibility
AnswerResult = AnswerResponse
from app.schemas.analytics import ClassroomAnalytics, StudentSummary, AssignmentSummary, TopicPerformance, HardestQuestion, RecommendedPractice

# Rebuild models with forward references
StudentProfileResponse.model_rebuild()

# Alias for backward compatibility
UserSignup = UserCreate
UserLogin = LoginRequest
TokenResponse = Token

__all__ = [
    "UserCreate",
    "UserSignup",
    "UserResponse",
    "LoginRequest",
    "UserLogin",
    "Token",
    "TokenResponse",
    "ClassroomCreate",
    "ClassroomResponse",
    "AddStudentRequest",
    "StudentInClassroom",
    "AssignmentCreate",
    "AssignmentResponse",
    "QuestionCreate",
    "QuestionResponse",
    "AssignmentWithQuestions",
    "AssignmentStatusUpdate",
    "SubmissionCreate",
    "SubmissionResponse",
    "AnswerSubmission",
    "AnswerResponse",
    "AnswerResult",
    "ClassroomAnalytics",
    "StudentSummary",
    "AssignmentSummary",
    "TopicPerformance",
    "HardestQuestion",
    "RecommendedPractice",
]
