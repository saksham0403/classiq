from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from app.core.database import get_db
from app.api.v1.dependencies import get_current_teacher, get_current_user
from app.models.user import User
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.models.question import Question
from app.models.submission import Submission
from app.models.answer import Answer
from app.models.student_profile import StudentProfile
from app.schemas.analytics import (
    ClassroomAnalytics,
    AssignmentSummary,
    TopicPerformance,
    HardestQuestion,
    StudentSummary,
    RecommendedPractice
)

router = APIRouter()

# Sample practice questions for recommendations
PRACTICE_QUESTIONS = {
    "Factoring Quadratics": [
        {"text": "Factor 4x^2 - 9", "type": "algebra"},
        {"text": "Factor x^2 + 5x + 6", "type": "algebra"},
        {"text": "Factor 2x^2 - 7x + 3", "type": "algebra"},
    ],
    "Linear Equations": [
        {"text": "Solve 2x + 3 = 11", "type": "algebra"},
        {"text": "Solve 5x - 7 = 18", "type": "algebra"},
    ],
    "Quadratic Equations": [
        {"text": "Solve x^2 - 5x + 6 = 0", "type": "algebra"},
        {"text": "Solve 2x^2 - 8x = 0", "type": "algebra"},
    ],
    "Polynomials": [
        {"text": "Simplify (x + 2)(x - 3)", "type": "algebra"},
        {"text": "Expand (x + 1)^2", "type": "algebra"},
    ],
}

@router.get("/classrooms/{classroom_id}/analytics", response_model=ClassroomAnalytics)
def get_classroom_analytics(
    classroom_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # Verify classroom belongs to teacher
    classroom = db.query(Classroom).filter(
        Classroom.id == classroom_id,
        Classroom.teacher_id == current_user.id
    ).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Get all assignments for this classroom
    assignments = db.query(Assignment).filter(
        Assignment.classroom_id == classroom_id
    ).all()
    
    assignment_summaries = []
    topic_scores: Dict[str, List[float]] = {}
    question_scores: Dict[int, List[bool]] = {}
    question_texts: Dict[int, str] = {}
    
    for assignment in assignments:
        # Get all submissions for this assignment
        submissions = db.query(Submission).filter(
            Submission.assignment_id == assignment.id
        ).all()
        
        if not submissions:
            continue
        
        # Calculate average score for this assignment
        total_score = 0.0
        num_submissions = 0
        
        for submission in submissions:
            answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
            if answers:
                submission_score = sum(a.ai_score for a in answers) / len(answers)
                total_score += submission_score
                num_submissions += 1
                
                # Track topic performance
                for answer in answers:
                    question = db.query(Question).filter(Question.id == answer.question_id).first()
                    if question:
                        topic = question.topic_tag
                        if topic not in topic_scores:
                            topic_scores[topic] = []
                        topic_scores[topic].append(answer.ai_score)
                        
                        # Track question performance
                        if question.id not in question_scores:
                            question_scores[question.id] = []
                            question_texts[question.id] = question.text
                        question_scores[question.id].append(answer.ai_is_correct)
        
        if num_submissions > 0:
            avg_score = total_score / num_submissions
            assignment_summaries.append(AssignmentSummary(
                assignment_id=assignment.id,
                title=assignment.title,
                avg_score=avg_score
            ))
    
    # Calculate topic accuracies
    topics = []
    for topic, scores in topic_scores.items():
        accuracy = sum(scores) / len(scores) if scores else 0.0
        topics.append(TopicPerformance(topic=topic, accuracy=accuracy))
    
    # Find hardest questions (lowest percent correct)
    hardest_questions = []
    for question_id, correct_list in question_scores.items():
        percent_correct = sum(correct_list) / len(correct_list) if correct_list else 0.0
        hardest_questions.append(HardestQuestion(
            question_id=question_id,
            text=question_texts.get(question_id, ""),
            percent_correct=percent_correct
        ))
    
    # Sort by percent_correct (ascending - hardest first)
    hardest_questions.sort(key=lambda x: x.percent_correct)
    
    return ClassroomAnalytics(
        assignment_summary=assignment_summaries,
        topics=topics,
        hardest_questions=hardest_questions[:10]  # Top 10 hardest
    )

@router.get("/students/{student_id}/summary", response_model=StudentSummary)
def get_student_summary(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access: student can see own summary, teacher can see any student in their classes
    student = db.query(User).filter(User.id == student_id).first()
    if not student or student.role != "student":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if current_user.role == "student":
        if current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    else:  # teacher
        # Check if student is in any of teacher's classrooms
        teacher_classrooms = db.query(Classroom).filter(
            Classroom.teacher_id == current_user.id
        ).all()
        classroom_ids = [c.id for c in teacher_classrooms]
        
        student_profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == student_id,
            StudentProfile.classroom_id.in_(classroom_ids)
        ).first()
        if not student_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student not in your classrooms"
            )
    
    # Get all submissions for this student
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    
    if not submissions:
        return StudentSummary(
            overall_score=0.0,
            strengths=[],
            weak_topics=[],
            recommended_practice=[]
        )
    
    # Calculate overall score and topic performance
    all_scores = []
    topic_scores: Dict[str, List[float]] = {}
    
    for submission in submissions:
        answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
        for answer in answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                all_scores.append(answer.ai_score)
                topic = question.topic_tag
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(answer.ai_score)
    
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    # Determine strengths and weak topics
    topic_accuracies = {}
    for topic, scores in topic_scores.items():
        accuracy = sum(scores) / len(scores) if scores else 0.0
        topic_accuracies[topic] = accuracy
    
    # Strengths: topics with accuracy > 0.7
    strengths = [topic for topic, acc in topic_accuracies.items() if acc >= 0.7]
    
    # Weak topics: topics with accuracy < 0.6
    weak_topics = [topic for topic, acc in topic_accuracies.items() if acc < 0.6]
    
    # Recommended practice
    recommended_practice = []
    for topic in weak_topics:
        if topic in PRACTICE_QUESTIONS:
            for practice_q in PRACTICE_QUESTIONS[topic][:2]:  # Top 2 per topic
                recommended_practice.append(RecommendedPractice(
                    topic=topic,
                    question_text=practice_q["text"],
                    type=practice_q["type"]
                ))
    
    return StudentSummary(
        overall_score=overall_score,
        strengths=strengths,
        weak_topics=weak_topics,
        recommended_practice=recommended_practice
    )

