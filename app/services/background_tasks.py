from app.services import text_to_speech, evaluator
from app.services.session_manager import session_manager
import asyncio

async def prefetch_tts(session_id: str, questions: list[str]):
    """
    Generates audio for all questions (skipping 0 since it's likely already done or doing it parallel).
    We start from index 1 because index 0 is needed immediately by the /start endpoint, 
    so it might be handled there or here depending on logic.
    Actual logic: The /start endpoint generates Q0. We generate Q1..QN here.
    """
    print(f"[Background] Starting TTS pre-fetch for session {session_id}")
    
    # Iterate from 1 to end
    for idx, question in enumerate(questions):
        if idx == 0: continue # Already generated in /start
        
        try:
            filename_prefix = f"q_{session_id}_{idx}"
            print(f"[Background] Generating audio for Q{idx+1}: {filename_prefix}")
            
            # We don't need run_in_threadpool here if we are already in a background task, 
            # but if speak_text is blocking (synchronous), we might want to wrap it.
            # Assuming speak_text is synchronous blocking IO, we should await it properly if it was async
            # or wrap it. The original code used run_in_threadpool(speak_text).
            # Here we will re-use that pattern if possible, or just call it if we are sure.
            # Since we are in a pure async function called by BackgroundTasks, we should ideally use threadpool for blocking IO.
            
            # For simplicity in this helper, let's assume valid async/sync. 
            # If `speak_text` is sync, we wrap it.
            from fastapi.concurrency import run_in_threadpool
            result = await run_in_threadpool(text_to_speech.speak_text, question, filename_prefix)
            
            if result["valid"]:
                session_manager.set_cached_audio(session_id, idx, result["relative_path"])
                print(f"[Background] Cached audio for Q{idx+1}")
            else:
                print(f"[Background] Failed audio for Q{idx+1}: {result.get('error')}")
                
        except Exception as e:
            print(f"[Background] Error pre-fetching Q{idx+1}: {e}")

async def process_answer_evaluation(session_id: str, index: int, question: str, answer_text: str):
    """
    Evaluates the answer and updates the session feedback asynchronously.
    """
    print(f"[Background] Evaluating answer for session {session_id} Q{index}")
    try:
        from fastapi.concurrency import run_in_threadpool
        feedback = await run_in_threadpool(evaluator.evaluate_answer, question, answer_text)
        
        session_manager.add_feedback(session_id, index, feedback)
        print(f"[Background] Feedback saved for session {session_id} Q{index}")
        
    except Exception as e:
        print(f"[Background] Error evaluating answer: {e}")
