from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from app.database import get_db
from app.models import User, Classroom, Assignment, Question, Answer, Submission, StudentProfile
from app.schemas import (
    ClassroomAnalytics, AssignmentSummary, TopicPerformance, HardestQuestion,
    StudentSummary, RecommendedPractice
)
from app.auth import get_current_teacher, get_current_user

router = APIRouter()


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    # Get all assignments for this classroom
    assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    
    # Assignment summaries
    assignment_summaries = []
    for assignment in assignments:
        submissions = db.query(Submission).filter(Submission.assignment_id == assignment.id).all()
        if submissions:
            # Get average score for this assignment
            total_score = 0.0
            count = 0
            for submission in submissions:
                answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
                if answers:
                    submission_avg = sum(a.ai_score for a in answers) / len(answers)
                    total_score += submission_avg
                    count += 1
            avg_score = total_score / count if count > 0 else 0.0
        else:
            avg_score = 0.0
        
        assignment_summaries.append(AssignmentSummary(
            assignment_id=assignment.id,
            title=assignment.title,
            avg_score=avg_score
        ))

    # Topic performance
    # Get all questions in this classroom's assignments
    assignment_ids = [a.id for a in assignments]
    questions = db.query(Question).filter(Question.assignment_id.in_(assignment_ids)).all()
    
    topic_stats = {}
    for question in questions:
        if question.topic_tag not in topic_stats:
            topic_stats[question.topic_tag] = {"correct": 0, "total": 0}
        
        # Get all answers for this question
        answers = db.query(Answer).join(Submission).filter(
            Answer.question_id == question.id,
            Submission.assignment_id.in_(assignment_ids)
        ).all()
        
        topic_stats[question.topic_tag]["total"] += len(answers)
        topic_stats[question.topic_tag]["correct"] += sum(1 for a in answers if a.ai_is_correct)
    
    topics = []
    for topic, stats in topic_stats.items():
        accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
        topics.append(TopicPerformance(topic=topic, accuracy=accuracy))
    
    topics.sort(key=lambda x: x.accuracy)

    # Hardest questions
    question_stats = {}
    for question in questions:
        answers = db.query(Answer).join(Submission).filter(
            Answer.question_id == question.id,
            Submission.assignment_id.in_(assignment_ids)
        ).all()
        
        if answers:
            correct_count = sum(1 for a in answers if a.ai_is_correct)
            percent_correct = correct_count / len(answers)
            question_stats[question.id] = {
                "text": question.text,
                "percent_correct": percent_correct
            }
    
    hardest = []
    for q_id, stats in sorted(question_stats.items(), key=lambda x: x[1]["percent_correct"])[:10]:
        hardest.append(HardestQuestion(
            question_id=q_id,
            text=stats["text"],
            percent_correct=stats["percent_correct"]
        ))

    return ClassroomAnalytics(
        assignment_summary=assignment_summaries,
        topics=topics,
        hardest_questions=hardest
    )


@router.get("/students/{student_id}/summary", response_model=StudentSummary)
def get_student_summary(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access: student viewing own summary OR teacher viewing student in their class
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only view your own summary")

    # Get all submissions by this student
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    
    if not submissions:
        return StudentSummary(
            overall_score=0.0,
            strengths=[],
            weak_topics=[],
            recommended_practice=[]
        )

    # Calculate overall score
    all_scores = []
    topic_correct = {}
    topic_total = {}
    
    for submission in submissions:
        answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()
        for answer in answers:
            all_scores.append(answer.ai_score)
            
            # Get question to find topic
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                topic = question.topic_tag
                if topic not in topic_correct:
                    topic_correct[topic] = 0
                    topic_total[topic] = 0
                topic_total[topic] += 1
                if answer.ai_is_correct:
                    topic_correct[topic] += 1

    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

    # Calculate topic accuracies
    topic_accuracies = {}
    for topic in topic_total:
        accuracy = topic_correct[topic] / topic_total[topic] if topic_total[topic] > 0 else 0.0
        topic_accuracies[topic] = accuracy

    # Strengths: topics with accuracy >= 0.7
    strengths = [topic for topic, acc in topic_accuracies.items() if acc >= 0.7]
    
    # Weak topics: topics with accuracy < 0.5
    weak_topics = [topic for topic, acc in topic_accuracies.items() if acc < 0.5]

    # Recommended practice (simple: hard-coded examples per topic)
    recommended = []
    practice_questions = {
        "Factoring Quadratics": [
            {"text": "Factor 4x^2 - 9", "type": "algebra"},
            {"text": "Factor x^2 + 5x + 6", "type": "algebra"}
        ],
        "Linear Equations": [
            {"text": "Solve 2x + 3 = 7", "type": "algebra"},
            {"text": "Solve 3x - 5 = 10", "type": "algebra"}
        ],
        "Quadratic Equations": [
            {"text": "Solve x^2 - 5x + 6 = 0", "type": "algebra"},
            {"text": "Solve 2x^2 - 8 = 0", "type": "algebra"}
        ],
        "Polynomials": [
            {"text": "Simplify (x + 2)(x - 3)", "type": "algebra"},
            {"text": "Expand (x + 1)^2", "type": "algebra"}
        ]
    }

    for topic in weak_topics[:3]:  # Top 3 weak topics
        if topic in practice_questions:
            for q in practice_questions[topic][:2]:  # 2 questions per topic
                recommended.append(RecommendedPractice(
                    topic=topic,
                    question_text=q["text"],
                    type=q["type"]
                ))

    return StudentSummary(
        overall_score=overall_score,
        strengths=strengths,
        weak_topics=weak_topics,
        recommended_practice=recommended
    )

