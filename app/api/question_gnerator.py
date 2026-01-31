
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.services.resume_parser import extract_resume_text
from app.services.resume_ai import convert_resume_to_json
from app.services.question_generator import generate_interview_questions

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

        extracted_text = await run_in_threadpool(extract_resume_text, file.filename, file_bytes)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted")

        ats_json = await run_in_threadpool(convert_resume_to_json, extracted_text)
        clean_data = sanitize_json(ats_json)

        questions = await run_in_threadpool(generate_interview_questions, clean_data)

        return {
            "status": "success",
            "interview_questions": questions
        }

    except Exception as e:
        print(f"CRITICAL ERROR in generate_questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

