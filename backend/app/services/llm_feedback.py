"""
LLM Feedback Service using Ollama (local, free).
Generates explanations for student answers.
"""
import httpx
from typing import Optional


async def generate_feedback_ollama(
    question_text: str,
    correct_answer: str,
    student_answer: str,
    is_correct: bool,
    model: str = "mistral"
) -> str:
    """
    Generate feedback using local Ollama instance.
    
    Args:
        question_text: The question text
        correct_answer: The correct answer
        student_answer: The student's answer
        is_correct: Whether the answer is correct
        model: Ollama model name (mistral, llama2, phi3, gemma, etc.)
    
    Returns:
        Feedback text explaining the answer
    """
    prompt = f"""You are a friendly, concise middle-school tutor.

Question: {question_text}
Correct answer: {correct_answer}
Student answer: {student_answer}
Is correct: {"Yes" if is_correct else "No"}

Provide a brief explanation:
1) Confirm if the student is correct or incorrect.
2) Explain why (briefly).
3) Show the correct approach if they were wrong, or reinforce if they were right.

Keep it short (2-3 sentences), simple, and encouraging. Use a friendly tone.
"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                feedback = data.get("response", "").strip()
                return feedback
            else:
                return f"Error: Ollama returned status {response.status_code}. Make sure Ollama is running on localhost:11434"
    
    except httpx.ConnectError:
        return "Error: Could not connect to Ollama. Please make sure Ollama is running on localhost:11434. Install from https://ollama.ai"
    
    except httpx.TimeoutException:
        return "Error: Ollama request timed out. The model may be loading or too slow."
    
    except Exception as e:
        return f"Error generating feedback: {str(e)}"


async def check_ollama_available(model: str = "mistral") -> bool:
    """
    Check if Ollama is running and the model is available.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return any(model in name for name in model_names)
            return False
    except:
        return False

