"""
Answer extraction service for parsing OCR text and matching answers to questions.
"""
import re
from typing import List, Dict
from app.models import Question


def extract_student_answers(raw_text: str, assignment_questions: List[Question]) -> List[Dict[str, str]]:
    """
    Given OCR text and the assignment questions, return
    [{question_id, student_answer}]
    
    Uses regex to find patterns like:
    - 1. Answer text
    - 1) Answer text
    - Q1 Answer text
    - Question 1: Answer text
    """
    # Normalize text: lowercase for matching, but preserve original for answers
    normalized_text = raw_text.lower()
    answers = []
    
    # Create a mapping of question numbers to question objects
    question_map = {i + 1: q for i, q in enumerate(assignment_questions)}
    
    # Pattern 1: "1. Answer" or "1) Answer"
    pattern1 = re.compile(r'(\d+)[\.\)]\s*(.+?)(?=\d+[\.\)]|$)', re.DOTALL | re.MULTILINE)
    
    # Pattern 2: "Q1 Answer" or "Q 1 Answer"
    pattern2 = re.compile(r'q\s*(\d+)\s*[:\-]?\s*(.+?)(?=q\s*\d+|$)', re.DOTALL | re.MULTILINE | re.IGNORECASE)
    
    # Pattern 3: "Question 1: Answer"
    pattern3 = re.compile(r'question\s*(\d+)\s*[:\-]?\s*(.+?)(?=question\s*\d+|$)', re.DOTALL | re.MULTILINE | re.IGNORECASE)
    
    found_answers = {}
    
    # Try pattern 1 first (most common: "1. Answer")
    for match in pattern1.finditer(raw_text):
        q_num = int(match.group(1))
        answer_text = match.group(2).strip()
        if q_num in question_map and answer_text:
            found_answers[q_num] = answer_text
    
    # Try pattern 2 ("Q1 Answer")
    if len(found_answers) < len(assignment_questions):
        for match in pattern2.finditer(raw_text):
            q_num = int(match.group(1))
            answer_text = match.group(2).strip()
            if q_num in question_map and q_num not in found_answers and answer_text:
                found_answers[q_num] = answer_text
    
    # Try pattern 3 ("Question 1: Answer")
    if len(found_answers) < len(assignment_questions):
        for match in pattern3.finditer(raw_text):
            q_num = int(match.group(1))
            answer_text = match.group(2).strip()
            if q_num in question_map and q_num not in found_answers and answer_text:
                found_answers[q_num] = answer_text
    
    # Build answer list in question order
    for i, question in enumerate(assignment_questions):
        q_num = i + 1
        student_answer = found_answers.get(q_num, "").strip()
        
        # Clean up answer: remove excessive whitespace, newlines
        student_answer = re.sub(r'\s+', ' ', student_answer)
        student_answer = student_answer.strip()
        
        answers.append({
            "question_id": question.id,
            "student_answer": student_answer
        })
    
    return answers


def extract_answers_simple(raw_text: str, num_questions: int) -> List[str]:
    """
    Simpler extraction: split by lines and assume each line is an answer.
    Used as fallback if regex patterns don't work.
    """
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # If we have enough lines, use them directly
    if len(lines) >= num_questions:
        return lines[:num_questions]
    
    # Otherwise, pad with empty strings
    while len(lines) < num_questions:
        lines.append("")
    
    return lines

