import requests
import os
import base64
import soundfile as sf
import io
from dotenv import load_dotenv
load_dotenv()
API_TOKEN = os.getenv("HF_API_KEY")  # set env variable
HF_URL = "https://router.huggingface.co/hf-inference/models/microsoft/speecht5_tts"

def speak_question(question: str, index: int) -> dict:
    """
    Converts a text question to speech and saves it as an audio file.
    Returns the path to the saved audio file.
    """
    payload = {
        
        "inputs": question,
        # Disable cache so the model generates a fresh response every time
        "options": {
            "use_cache": False
        }
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(HF_URL, headers=headers, json=payload)
    response.raise_for_status()

    ###audio_content = response.json()["audio"]
    ###audio_bytes = base64.b64decode(audio_content)
    
    ###path = f"app/storage/audio/question_{index}.wav"
    ###sf.write(path, audio_bytes, 22050)

    ###return audio_bytes
    
    ### NEW CODE LOGIC ONLY TO CHECK
    data = response.json()
    if "audio" not in data:
        raise RuntimeError("No audio returned from TTS")

    audio_bytes = base64.b64decode(data["audio"])
    """     
    os.makedirs("app/storage/audio", exist_ok=True)
    path = f"app/storage/audio/question_{index}.wav"

    # Write WAV file
    sf.write(path, audio_bytes, 22050)

    # ✅ VALIDATION CHECK
    info = sf.info(path)
    if info.duration < 0.3:
        raise RuntimeError("Generated audio too short")

    return {
        "audio_path": path,
        "duration": round(info.duration, 2),
        "sample_rate": info.samplerate
    }

    """
    audio_buffer = io.BytesIO(audio_bytes)
    audio_array, samplerate = sf.read(audio_buffer)

    # Ensure folder exists
    os.makedirs("app/storage/audio", exist_ok=True)
    path = f"app/storage/audio/question_{index}.wav"

    # Save properly to WAV
    sf.write(path, audio_array, samplerate)

    # ✅ validation
    info = sf.info(path)
    if info.duration < 0.3:
        raise RuntimeError("Generated audio too short")

    return {
        "audio_path": path,
        "duration": round(info.duration, 2),
        "sample_rate": info.samplerate
    }

  
    
    