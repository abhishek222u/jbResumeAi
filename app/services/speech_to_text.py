import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

API_TOKEN = os.getenv("HF_API_KEY")
model_id = "openai/whisper-large-v3-turbo"

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribes audio bytes to text using Hugging Face Inference API.
    """
    if not API_TOKEN:
        print("DEBUG: HF_API_KEY missing for STT")
        return "Error: API Key missing"

    client = InferenceClient(token=API_TOKEN)

    try:
        # automatic-speech-recognition
        response = client.automatic_speech_recognition(audio_bytes, model=model_id)
        return response.text
    except Exception as e:
        print(f"DEBUG: STT Error: {e}")
        return ""
