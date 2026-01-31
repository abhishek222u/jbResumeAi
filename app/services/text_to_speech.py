import os
import io
import soundfile as sf
import uuid
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Configuration
API_TOKEN = os.getenv("HF_API_KEY")
MODEL_ID = "facebook/mms-tts-eng"

# Helper: Path Setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = BASE_DIR / "app" / "storage" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

import traceback
from gtts import gTTS

def speak_text(text: str, filename_prefix: str = "output") -> dict:
    """
    Converts text to speech. 
    Directly uses gTTS for faster response and reliability, avoiding HF Inference cold starts/timeouts.
    """
    # Direct fallback to gTTS for speed
    return speak_text_gtts(text, filename_prefix)

    # Legacy HF Code (Commented out for performance)
    # if not API_TOKEN:
    #     print("DEBUG: HF_API_KEY not set. Using gTTS fallback.", flush=True)
    #     return speak_text_gtts(text, filename_prefix)
    # ...

def speak_text_gtts(text: str, filename_prefix: str) -> dict:
    try:
        print("DEBUG: Starting gTTS generation...", flush=True)
        tts = gTTS(text=text, lang='en')
        filename = f"{filename_prefix}_gtts.mp3" 
        filepath = AUDIO_DIR / filename
        
        print(f"DEBUG: Saving gTTS to {filepath}...", flush=True)
        tts.save(str(filepath))
        print("DEBUG: gTTS save complete.", flush=True)

        
        # Duration check with soundfile supports mp3 if libsndfile supports it, otherwise generic check or skip.
        # valid=True is enough.
        return {
            "valid": True,
            "file_path": str(filepath),
            "relative_path": f"/storage/audio/{filename}",
            "duration": 0.0 # Unknown without extra lib
        }
    except Exception as e:
         return {"valid": False, "error": f"gTTS Error: {str(e)}"}

def save_audio(audio_bytes: bytes, filename: str) -> dict:
    filepath = AUDIO_DIR / filename
    with io.BytesIO(audio_bytes) as bio:
        audio_data, samplerate = sf.read(bio)
        sf.write(str(filepath), audio_data, samplerate)
        info = sf.info(str(filepath))
        return {
            "valid": True,
            "file_path": str(filepath),
            "relative_path": f"/storage/audio/{filename}",
            "duration": float(info.duration)
        }


