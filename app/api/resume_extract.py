from fastapi import APIRouter, UploadFile, File
from app.services.resume_parser import extract_resume_text, extract_text_from_pdf
router = APIRouter(prefix="/resume")
import os
import tempfile
from fastapi import HTTPException
@router.post("/extract-text")


async def extract_text(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()
            text = extract_text_from_pdf(file_bytes)
    finally:
        os.remove(tmp_path)

    return {"resume_text": text}
