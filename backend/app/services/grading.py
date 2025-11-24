from typing import Tuple
import re
import sympy
from sympy import sympify, simplify, Symbol, solve, Eq

def grade_answer(question_type: str, correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """
    Returns (is_correct, score_float_0_to_1).
    """
    try:
        if question_type == "numeric":
            return grade_numeric(correct_answer, student_answer)
        elif question_type == "algebra":
            return grade_algebra(correct_answer, student_answer)
        elif question_type == "short_answer":
            return grade_short_answer(correct_answer, student_answer)
        elif question_type == "mcq":
            return grade_mcq(correct_answer, student_answer)
        else:
            return (False, 0.0)
    except Exception:
        return (False, 0.0)

def grade_numeric(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade numeric answers with tolerance."""
    try:
        correct_val = float(correct_answer.strip())
        student_val = float(student_answer.strip())
        tolerance = 1e-3
        diff = abs(correct_val - student_val)
        is_correct = diff < tolerance
        return (is_correct, 1.0 if is_correct else 0.0)
    except (ValueError, TypeError):
        return (False, 0.0)

def grade_algebra(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade algebraic expressions/equations using SymPy."""
    try:
        # Normalize whitespace
        correct = correct_answer.strip()
        student = student_answer.strip()
        
        # Try to parse as equations (e.g., "x = 1" or "x+1=2")
        # Check if it contains "="
        if "=" in correct and "=" in student:
            # Parse both sides
            correct_parts = [p.strip() for p in correct.split("=", 1)]
            student_parts = [p.strip() for p in student.split("=", 1)]
            
            if len(correct_parts) == 2 and len(student_parts) == 2:
                try:
                    # Try to solve both and compare solutions
                    correct_lhs = sympify(correct_parts[0])
                    correct_rhs = sympify(correct_parts[1])
                    student_lhs = sympify(student_parts[0])
                    student_rhs = sympify(student_parts[1])
                    
                    # Check if equations are equivalent
                    correct_eq = Eq(correct_lhs, correct_rhs)
                    student_eq = Eq(student_lhs, student_rhs)
                    
                    # Simplify both sides and compare
                    correct_simplified = simplify(correct_lhs - correct_rhs)
                    student_simplified = simplify(student_lhs - student_rhs)
                    
                    # Check if they're equivalent
                    diff = simplify(correct_simplified - student_simplified)
                    if diff == 0:
                        return (True, 1.0)
                    
                    # Alternative: try to extract variable and compare solutions
                    # Find common variables
                    correct_vars = correct_lhs.free_symbols.union(correct_rhs.free_symbols)
                    student_vars = student_lhs.free_symbols.union(student_rhs.free_symbols)
                    
                    if correct_vars and student_vars:
                        common_var = list(correct_vars.intersection(student_vars))
                        if common_var:
                            var = common_var[0]
                            try:
                                correct_sol = solve(correct_eq, var)
                                student_sol = solve(student_eq, var)
                                if correct_sol and student_sol:
                                    # Compare solutions
                                    if set(correct_sol) == set(student_sol):
                                        return (True, 1.0)
                            except:
                                pass
                except:
                    pass
        
        # Fallback: try to parse as expressions and compare
        try:
            correct_expr = sympify(correct)
            student_expr = sympify(student)
            
            # Simplify and compare
            diff = simplify(correct_expr - student_expr)
            if diff == 0:
                return (True, 1.0)
            
            # Try numeric evaluation if both are numeric
            try:
                correct_val = float(correct_expr.evalf())
                student_val = float(student_expr.evalf())
                if abs(correct_val - student_val) < 1e-3:
                    return (True, 1.0)
            except:
                pass
        except:
            pass
        
        # Last resort: string normalization and comparison
        correct_normalized = normalize_text(correct)
        student_normalized = normalize_text(student)
        if correct_normalized == student_normalized:
            return (True, 1.0)
        
        return (False, 0.0)
    except Exception:
        return (False, 0.0)

def grade_short_answer(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade short answers using text similarity."""
    correct_norm = normalize_text(correct_answer)
    student_norm = normalize_text(student_answer)
    
    if correct_norm == student_norm:
        return (True, 1.0)
    
    # Compute Jaccard similarity (word overlap)
    correct_words = set(correct_norm.split())
    student_words = set(student_norm.split())
    
    if not correct_words:
        return (False, 0.0)
    
    intersection = correct_words.intersection(student_words)
    union = correct_words.union(student_words)
    
    similarity = len(intersection) / len(union) if union else 0.0
    threshold = 0.7
    
    is_correct = similarity >= threshold
    return (is_correct, similarity)

def grade_mcq(correct_answer: str, student_answer: str) -> Tuple[bool, float]:
    """Grade multiple choice questions."""
    correct_norm = normalize_text(correct_answer)
    student_norm = normalize_text(student_answer)
    
    is_correct = correct_norm == student_norm
    return (is_correct, 1.0 if is_correct else 0.0)

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    # Lowercase, strip, remove extra whitespace
    text = text.lower().strip()
    # Remove punctuation (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text

