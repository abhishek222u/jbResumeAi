import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

API_TOKEN = os.getenv("HF_API_KEY")
# Using a widely available open model
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

def generate_interview_questions(clean_data: dict, model: str = MODEL_ID, num_questions: int = 10):
    """
    Generates interview questions based on parsed resume data.
    Returns a list of questions.
    """
    if not API_TOKEN:
        print("DEBUG: HF_API_KEY is missing!")
        return []

    skills = ", ".join(clean_data.get("skills", [])) or "NA"

    experience_text = "; ".join(
        f"{e.get('title', 'NA')} at {e.get('company', 'NA')}"
        for e in clean_data.get("experience", [])
    ) or "NA"

    education_text = "; ".join(
        f"{e.get('degree', 'NA')} from {e.get('institution', 'NA')}"
        for e in clean_data.get("education", [])
    ) or "NA"

    prompt = f"""
    You are an expert technical interviewer.
    Based on the candidate's resume information below,
    generate Exactly {num_questions} clear, professional interview questions.
    IMPORTANT:
    - You Must output {num_questions} questions.
    - The questions should be relevant to the candidate's skills, experience, and education.
    - Do Not output fewer than {num_questions}.
    - Each questions must be on its own Line.
    
    Resume Information:
    Skills: {skills}
    Experience: {experience_text}
    Education: {education_text}

    Rules:
    - Output ONLY the questions
    - One question per line
    - No numbering
    - No extra text
    """
    
    client = InferenceClient(token=API_TOKEN)
    
    try:
        messages = [
            {"role": "system", "content": "You generate interview questions. Output only Plain text Questions."},
            {"role": "user", "content": prompt}
        ]
        
        # Use simple text generation if chat completion is tricky, but chat is better for instruct models.
        # client.chat_completion is the way.
        response = client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=500,
            temperature=0.2
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Safe parsing
        questions = [
            line.strip()
            for line in raw_text.split("\n")
            if line.strip() and "?" in line # basic validation
        ]
        
        # Fallback if parsing failed (e.g. numbered list)
        if not questions:
            # simple split by newline
             questions = [l.strip() for l in raw_text.split("\n") if l.strip()]

        return questions[:num_questions]

    except Exception as e:
        print(f"DEBUG: Question Generation Error: {e}")
        # Return empty list so the caller (API) can raise 500
        return []