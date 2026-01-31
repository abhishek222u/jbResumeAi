from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from app.services import text_to_speech, question_generator
import traceback

router = APIRouter(prefix="/tts", tags=["Text to Speech"])

class TTSRequest(BaseModel):
    text: str
    filename_prefix: Optional[str] = "test_audio"

class TTSResponse(BaseModel):
    audio_path: str
    relative_path: str
    duration: float
    message: str

class MockGenResponse(BaseModel):
    question: str
    audio_path: str
    message: str

class ResumeData(BaseModel):
    skills: list[str]
    experience: list[dict]
    education: list[dict]

@router.post("/generate-and-speak", response_model=MockGenResponse)
async def generate_and_speak(resume_data: ResumeData):
    """
    [TEST ENDPOINT] Manual Trigger
    ------------------------------
    This endpoint does NOT parse a resume. It expects YOU to provide the
    parsed data (Skills, Exp, Edu) in the JSON Body.
    
    Use this to test the "Generator -> TTS" flow without uploading a file.
    
    For the REAL flow (File -> Parse -> Generate -> Speak), use:
    POST /interview/start
    """
    try:
        # 1. Use Provided Data
        clean_data = resume_data.dict()

        # 2. Generate Questions
        questions = await run_in_threadpool(question_generator.generate_interview_questions, clean_data)
        if not questions:
            print("DEBUG: No questions generated.")
            raise HTTPException(status_code=500, detail="No questions generated")

        # 3. Speak First Question
        first_q = questions[0]
        print(f"DEBUG: Generating audio for: {first_q}")
        result = await run_in_threadpool(text_to_speech.speak_text, first_q, filename_prefix="resume_gen_test")

        if not result["valid"]:
            print(f"DEBUG: TTS Invalid result: {result}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown TTS error"))

        return MockGenResponse(
            question=first_q,
            audio_path=result["relative_path"],
            message="Generated from provided resume data and Spoken successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        # Capture full traceback
        error_trace = traceback.format_exc()
        print(error_trace) # Keep checking terminal
        # Return it in the response so user sees it in Postman
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)} | Trace: {error_trace}")

@router.post("/speak", response_model=TTSResponse)
async def generate_speech(payload: TTSRequest):
    """
    Test endpoint to generate speech from text.
    """
    if not payload.text:
        raise HTTPException(status_code=400, detail="Text is required")

    result = await run_in_threadpool(
        text_to_speech.speak_text,
        text=payload.text,
        filename_prefix=payload.filename_prefix
    )

    if not result["valid"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown TTS error"))

    return TTSResponse(
        audio_path=result["file_path"],
        relative_path=result["relative_path"],
        duration=result["duration"],
        message="Audio generated successfully"
    )
