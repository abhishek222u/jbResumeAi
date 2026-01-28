
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import extract_resume_text, extract_text_from_pdf
from app.services.resume_ai import convert_resume_to_json
router = APIRouter(prefix="/parse")
def sanitize_json(data: dict) -> dict:
    return {
        "skills": data.get("skills", []),
        "experience": data.get("experience", []),
        "education": data.get("education", [])
    }

@router.post("/parse-ats")
async def parse_ats(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        extracted_text = extract_resume_text(file.filename, file_bytes)

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from resume")
 
        ats_json = convert_resume_to_json(extracted_text)
        clean_data = sanitize_json(ats_json)

        return {
            "status": "success",
            "data": clean_data
        }

    except Exception as e:
        print(f"CRITICAL ERROR in parse_ats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
