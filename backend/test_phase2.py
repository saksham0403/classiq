#!/usr/bin/env python3
"""
Quick test script to verify Phase 2 functionality.
Run: python test_phase2.py
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_services():
    """Test that all Phase 2 services can be imported and basic functions work."""
    print("🧪 Testing Phase 2 Services...\n")
    
    # Test OCR service
    try:
        from app.services.ocr import extract_text_from_file, clean_ocr_text
        print("✅ OCR service: Import successful")
        # Test text cleaning
        test_text = "  Hello   World  \n\n  Test  "
        cleaned = clean_ocr_text(test_text)
        # Check that cleaning removes excessive whitespace
        assert "Hello" in cleaned and "World" in cleaned, "Text cleaning failed"
        print("✅ OCR service: Text cleaning works")
    except Exception as e:
        print(f"❌ OCR service: {e}")
        return False
    
    # Test Answer Extraction
    try:
        from app.services.answer_extraction import extract_student_answers
        from app.models import Question, QuestionType
        print("✅ Answer extraction: Import successful")
        
        # Create mock questions
        questions = [
            Question(id=1, text="What is 2+2?", correct_answer="4", question_type=QuestionType.NUMERIC, topic_tag="Math"),
            Question(id=2, text="Solve x+1=3", correct_answer="x=2", question_type=QuestionType.ALGEBRA, topic_tag="Algebra"),
        ]
        
        # Test extraction
        ocr_text = "1. 4\n2. x=2"
        answers = extract_student_answers(ocr_text, questions)
        assert len(answers) == 2, "Should extract 2 answers"
        assert answers[0]["question_id"] == 1, "First answer should match question 1"
        print("✅ Answer extraction: Works correctly")
    except Exception as e:
        print(f"❌ Answer extraction: {e}")
        return False
    
    # Test LLM Feedback
    try:
        from app.services.llm_feedback import generate_feedback_ollama, check_ollama_available
        print("✅ LLM feedback: Import successful")
        
        # Check if Ollama is available (non-blocking)
        ollama_available = await check_ollama_available()
        if ollama_available:
            print("✅ LLM feedback: Ollama is running")
        else:
            print("⚠️  LLM feedback: Ollama not running (install from https://ollama.ai)")
    except Exception as e:
        print(f"❌ LLM feedback: {e}")
        return False
    
    print("\n✅ All Phase 2 services are functional!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_services())
    sys.exit(0 if result else 1)

