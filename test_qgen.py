from app.services import question_generator
import json

dummy_data = {
    "skills": ["Python", "FastAPI"],
    "experience": [{"title": "Dev", "company": "A"}],
    "education": [{"degree": "B.Tech", "institution": "B"}]
}

try:
    print("Testing Question Generator...")
    questions = question_generator.generate_interview_questions(dummy_data)
    print("Success!")
    print(json.dumps(questions, indent=2))
except Exception as e:
    print(f"Error: {e}")
