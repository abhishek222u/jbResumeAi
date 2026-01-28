import requests
from dotenv import load_dotenv
import os   
load_dotenv()

API_TOKEN = os.getenv("HF_API_KEY")  # set env variable
HF_URL = "https://router.huggingface.co/v1/chat/completions"


def generate_interview_questions(clean_data: dict,
    model: str = "meta-llama/Meta-Llama-3-8B-Instruct",
    num_questions: int = 10
):
    """
    Generates interview questions based on parsed resume data.
    Returns a list of questions.
    """

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
    
    Focus on:
    - Skills application - Generate exactly 2 questions
    - Real-World Experience - Generate exactly 2 questions
    - Educational Background - Generate exactly 1 question
    - Problem-Solving - Generate exactly 2 questions
    - Design or decision-making - Generate exactly 2 questions
    - Learning Background - Generate exactly 1 question

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
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You generate interview questions. Output only Plain text Questions"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(HF_URL, headers=headers, json=payload)
    response.raise_for_status()

    raw_text = response.json()["choices"][0]["message"]["content"].strip()

    # Safe parsing: one question per line
    questions = [
        line.strip()
        for line in raw_text.split("\n")
        if line.strip()
    ]

    # Hard guarantee
    return questions[:10]
    
    

