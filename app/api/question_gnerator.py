
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import extract_resume_text
from app.services.resume_ai import convert_resume_to_json
from app.services.questions_genrator import generate_interview_questions

router = APIRouter(prefix="/question")
def sanitize_json(data: dict) -> dict:
    return {
        "skills": data.get("skills", []),
        "experience": data.get("experience", []),
        "education": data.get("education", [])
    }

@router.post("/generate-questions")
async def generate_questions_only(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        extracted_text = extract_resume_text(file.filename, file_bytes)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted")

        ats_json = convert_resume_to_json(extracted_text)
        clean_data = sanitize_json(ats_json)

        questions = generate_interview_questions(clean_data)

        return {
            "status": "success",
            "interview_questions": questions
        }

    except Exception as e:
        print(f"CRITICAL ERROR in generate_questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

