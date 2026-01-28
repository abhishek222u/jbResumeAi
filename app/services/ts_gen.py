import os
import requests
import base64
import io
import soundfile as sf
from pathlib import Path
import uuid
from dotenv import load_dotenv

load_dotenv()

# ===============================
# Configuration
# ===============================
API_TOKEN = os.getenv("HF_API_KEY")
HF_URL = "https://router.huggingface.co/hf-inference/models/microsoft/speecht5_tts"

# Helper: Path Setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = BASE_DIR / "app" / "storage" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def speak_question(text: str, idx: int, session_id: str = None) -> dict:
    """
    Converts text to speech using Hugging Face API.
    
    Args:
        text (str): The text to convert.
        idx (int): Question index.
        session_id (str): Session identifier for unique filenames.
        
    Returns:
        dict: Metadata about the generated audio.
    """
    if not API_TOKEN:
        raise ValueError("HF_API_KEY not found in environment variables")

    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    # Payload for HF API
    payload = {
        "inputs": text,
        "options": {
            "use_cache": False,
            "wait_for_model": True
        }
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(HF_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if audio is in response (HF Inference API usually returns 'audio' key for TTS)
        # Note: Some HF endpoints return raw bytes, but the standard Inference API for SpeechT5 
        # normally wraps it in JSON with a base64 string if using the new serverless inference,
        # or sometimes raw bytes. The reference manual and tts_generator.py suggest JSON+base64.
        
        # Handle cases where response might be raw bytes vs json
        if response.headers.get("content-type") == "application/json":
            if "audio" not in data:
                raise RuntimeError(f"Unexpected API response: {data}")
            audio_bytes = base64.b64decode(data["audio"])
        else:
             # Fallback if the API returns raw bytes directly
            audio_bytes = response.content

        # Convert to audio array using SoundFile to ensure validity and get properties
        audio_buffer = io.BytesIO(audio_bytes)
        audio_array, samplerate = sf.read(audio_buffer)

        # Generate specific filename
        filename = f"question_{session_id}_{idx}.wav"
        filepath = AUDIO_DIR / filename

        # Write to file
        sf.write(str(filepath), audio_array, samplerate)
        
        # Get duration
        info = sf.info(str(filepath))

        return {
            "audio_url": f"/audio/{filename}",
            "file_path": str(filepath),
            "sample_rate": samplerate,
            "duration": info.duration
        }

    except Exception as e:
        print(f"Error in speak_question (API): {e}")
        raise e
