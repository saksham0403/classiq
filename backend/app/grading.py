import re
from typing import Tuple
from sympy import sympify, simplify, Symbol, Eq, solve
from app.models import QuestionType


def grade_answer(question_type: QuestionType, correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """
    Returns (is_correct, score_float_0_to_1).
    """
    try:
        if question_type == QuestionType.NUMERIC:
            return grade_numeric(correct_answer, student_answer)
        elif question_type == QuestionType.ALGEBRA:
            return grade_algebra(correct_answer, student_answer)
        elif question_type == QuestionType.SHORT_ANSWER:
            return grade_short_answer(correct_answer, student_answer)
        elif question_type == QuestionType.MCQ:
            return grade_mcq(correct_answer, student_answer)
        else:
            return False, 0.0
    except Exception:
        return False, 0.0


def grade_numeric(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade numeric answers with tolerance."""
    try:
        correct_val = float(correct_answer.strip())
        student_val = float(student_answer.strip())
        diff = abs(correct_val - student_val)
        if diff < 1e-5:  # More precise tolerance: 0.00001
            return True, 1.0
        else:
            return False, 0.0
    except (ValueError, AttributeError):
        return False, 0.0


def grade_algebra(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade algebraic expressions/equations using SymPy."""
    try:
        # Normalize whitespace
        correct = correct_answer.strip()
        student = student_answer.strip()

        # Try to parse as equations first
        if "=" in correct and "=" in student:
            # Parse equations
            correct_parts = [p.strip() for p in correct.split("=", 1)]
            student_parts = [p.strip() for p in student.split("=", 1)]
            
            if len(correct_parts) == 2 and len(student_parts) == 2:
                try:
                    correct_left = sympify(correct_parts[0])
                    correct_right = sympify(correct_parts[1])
                    student_left = sympify(student_parts[0])
                    student_right = sympify(student_parts[1])
                    
                    correct_eq = simplify(correct_left - correct_right)
                    student_eq = simplify(student_left - student_right)
                    
                    if simplify(correct_eq - student_eq) == 0:
                        return True, 1.0
                except:
                    pass

        # Try as expressions
        try:
            correct_expr = simplify(sympify(correct))
            student_expr = simplify(sympify(student))
            if simplify(correct_expr - student_expr) == 0:
                return True, 1.0
        except:
            pass

        # Try solving both sides and comparing
        try:
            # Extract variable (assume 'x' for now)
            x = Symbol('x')
            correct_solved = solve(sympify(correct), x)
            student_solved = solve(sympify(student), x)
            
            if correct_solved and student_solved:
                if abs(float(correct_solved[0]) - float(student_solved[0])) < 1e-3:
                    return True, 1.0
        except:
            pass

        return False, 0.0
    except Exception:
        return False, 0.0


def grade_short_answer(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade short answers using text similarity."""
    def normalize(text: str) -> str:
        # Lowercase, remove punctuation, strip
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def tokenize(text: str) -> set:
        return set(text.split())

    correct_norm = normalize(correct_answer)
    student_norm = normalize(student_answer)

    if correct_norm == student_norm:
        return True, 1.0

    correct_tokens = tokenize(correct_norm)
    student_tokens = tokenize(student_norm)

    if not correct_tokens:
        return False, 0.0

    intersection = correct_tokens & student_tokens
    union = correct_tokens | student_tokens

    similarity = len(intersection) / len(union) if union else 0.0

    threshold = 0.7
    if similarity >= threshold:
        return True, similarity
    else:
        return False, similarity


def grade_mcq(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade multiple choice questions by exact match."""
    correct = correct_answer.strip().lower()
    student = student_answer.strip().lower()
    
    if correct == student:
        return True, 1.0
    else:
        return False, 0.0

