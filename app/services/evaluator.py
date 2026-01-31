import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import json

load_dotenv()

API_TOKEN = os.getenv("HF_API_KEY")
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

def evaluate_answer(question: str, answer: str) -> dict:
    """
    Evaluates the candidate's answer to the interview question.
    Returns a dict: {"feedback": str, "rating": str, "is_satisfactory": bool}
    """
    if not API_TOKEN:
        return {"feedback": "Error: API Key missing", "rating": "N/A", "is_satisfactory": False}

    prompt = f"""
    You are an expert technical interviewer.
    
    Question: "{question}"
    Candidate's Answer: "{answer}"
    
    Evaluate the answer. 
    1. Is it correct?
    2. specific feedback on what was good or missing.
    3. Rating (1-10).
    
    Output strictly in this JSON format:
    {{
      "feedback": "Your feedback here...",
      "rating": "X/10",
      "is_satisfactory": true/false
    }}
    """
    
    client = InferenceClient(token=API_TOKEN)
    
    try:
        messages = [
            {"role": "system", "content": "You are a strict technical evaluator. Output only JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat_completion(
            messages=messages,
            model=MODEL_ID,
            max_tokens=300,
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up markdown if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        return json.loads(content)
        
    except Exception as e:
        print(f"DEBUG: Evaluation Error: {e}")
        return {
            "feedback": "Could not evaluate answer due to system error.", 
            "rating": "N/A", 
            "is_satisfactory": False
        }
