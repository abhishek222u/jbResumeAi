from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional

from app.services import resume_parser, resume_ai, question_generator, text_to_speech, speech_to_text
from app.services.session_manager import session_manager
from app.services.background_tasks import prefetch_tts, process_answer_evaluation
import os

router = APIRouter(prefix="/interview", tags=["Interview"])

class StartResponse(BaseModel):
    session_id: str
    message: str
    current_question: str
    audio_path: str
    total_questions: int

class NextQuestionRequest(BaseModel):
    session_id: str
    answer: str # User's answer to the *current* question

class NextQuestionResponse(BaseModel):
    is_finished: bool
    message: str
    next_question: Optional[str] = None
    audio_path: Optional[str] = None
    progress: str

@router.post("/start", response_model=StartResponse)
async def start_interview(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Read File
    try:
        file_bytes = await file.read()
        filename = file.filename
        
        # 2. Parse Text
        resume_text = await run_in_threadpool(resume_parser.extract_resume_text, filename, file_bytes)
        
        # 3. Extract Structured JSON
        # (This uses the LLM to get skills/exp/edu)
        parsed_data = await run_in_threadpool(resume_ai.convert_resume_to_json, resume_text)
        
        # 4. Generate Questions
        # (This uses LLM to generate 10 questions)
        questions = await run_in_threadpool(question_generator.generate_interview_questions, parsed_data)
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate questions")

        # 5. Create Session
        session_id = session_manager.create_session(questions)
        
        # 6. Speak First Question
        first_q = questions[0]
        # Use simple filenames as requested by user for now? 
        # Actually for multiple questions in a session, we need unique filenames to avoid collision or overwrite.
        # But user asked 'remove uuid' from TTS service. 
        # I will pass a filename_prefix that includes session_id + index so it's unique but deterministic.
        
        tts_result = await run_in_threadpool(text_to_speech.speak_text, first_q, filename_prefix=f"q_{session_id}_0")
        
        if not tts_result["valid"]:
             raise HTTPException(status_code=500, detail=f"TTS Error: {tts_result.get('error')}")

        # 7. Start Background Pre-fetch for Q1...QN
        background_tasks.add_task(prefetch_tts, session_id, questions)

        return StartResponse(
            session_id=session_id,
            message="Interview started successfully.",
            current_question=first_q,
            audio_path=tts_result["relative_path"],
            total_questions=len(questions)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next", response_model=NextQuestionResponse)
async def next_question(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Save Audio File
    audio_bytes = await file.read()
    
    # Generate Filename: answer_{session_id}_{q_index}.mp3
    # We need index, so let's get it first
    session = session_manager.get_session(session_id)
    if not session:
         raise HTTPException(status_code=404, detail="Session not found")
         
    current_idx = session.current_index
    file_ext = "mp3" 
    if file.filename.endswith(".wav"): file_ext = "wav"
    
    save_path = f"app/storage/answers/answer_{session_id}_{current_idx}.{file_ext}"
    
    with open(save_path, "wb") as f:
        f.write(audio_bytes)

    # 2. Transcribe Audio (STT)
    answer_text = await run_in_threadpool(speech_to_text.transcribe_audio, audio_bytes)
    
    if not answer_text:
        # Fallback if audio is silent or fails?
        answer_text = "[Audio Unintelligible]"

    # 2. Get Current Question for Context
    current_q = session_manager.get_current_question(session_id)
    if not current_q:
         raise HTTPException(status_code=404, detail="Session not found or finished")

    # Get index for background task
    session = session_manager.get_session(session_id)
    current_idx_for_eval = session.current_index

    # 3. Submit Answer (Without Feedback)
    # We submit the answer immediately. Evaluation happens in background.
    success = session_manager.submit_answer(session_id, answer_text, feedback=None)
    if not success:
         raise HTTPException(status_code=404, detail="Session invalid")

    # 4. Trigger Background Evaluation
    # Note: submit_answer incremented the index, so 'current_q' is effectively the 'previous' question now.
    # But we captured 'current_q' BEFORE submit_answer, so it is correct.
    background_tasks.add_task(process_answer_evaluation, session_id, current_idx_for_eval, current_q, answer_text)
         
    # 5. Check if finished
    if session_manager.is_finished(session_id):
        return NextQuestionResponse(
            is_finished=True,
            message="Interview completed. You can now request feedback.",
            progress="Done"
        )
        
    # 6. Get Next Question
    next_q = session_manager.get_current_question(session_id)
    session = session_manager.get_session(session_id)
    current_idx = session.current_index
    
    # 7. Get Audio (Cached or Generate)
    cached_audio_path = session_manager.get_cached_audio(session_id, current_idx)
    
    if cached_audio_path:
        print(f"DEBUG: Using cached audio for Q{current_idx}: {cached_audio_path}")
        audio_path_result = cached_audio_path
    else:
        print(f"DEBUG: Audio not cached for Q{current_idx}, generating now...")
        tts_result = await run_in_threadpool(text_to_speech.speak_text, next_q, filename_prefix=f"q_{session_id}_{current_idx}")
        audio_path_result = tts_result["relative_path"]
    
    return NextQuestionResponse(
        is_finished=False,
        message="Answer recorded.",
        next_question=next_q,
        audio_path=audio_path_result,
        progress=f"{current_idx + 1}"
    )

@router.get("/feedback")
async def get_feedback(session_id: str):
    feedbacks = session_manager.get_all_feedback(session_id)
    if feedbacks is None:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "session_id": session_id,
        "feedbacks": feedbacks
    }
    

    return NextQuestionResponse(
        is_finished=False,
        message="Next question ready",
        next_question=next_q,
        audio_path=tts_result["relative_path"],
        progress=f"{current_idx + 1}"
    )
