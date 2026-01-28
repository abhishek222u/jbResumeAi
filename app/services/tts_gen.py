import os
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
from pathlib import Path
import uuid

# 🚫 HARD BLOCK HF INFERENCE FOR THIS FILE
os.environ["HF_HUB_DISABLE_HF_TRANSFER"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_NO_HF_INFERENCE"] = "1"

# 🚨 REMOVE TOKENS ONLY FOR THIS MODULE
os.environ.pop("HF_API_TOKEN", None)
os.environ.pop("HUGGINGFACEHUB_API_TOKEN", None)

# ===============================
# Helper: Path Setup
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = BASE_DIR / "app" / "storage" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


# ===============================
# Load TTS model ONCE
# ===============================
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Load speaker embeddings dataset
embeddings_dataset = load_dataset(
    "Matthijs/cmu-arctic-xvectors",
    split="validation"
)

# Pick a speaker voice (stable index)
speaker_embedding = torch.tensor(
    embeddings_dataset[7306]["xvector"]
).unsqueeze(0)


# ===============================
# TTS Function
# ===============================
def speak_question(text: str, idx: int, session_id: str = None):
    """
    Generates speech for a given text.
    
    Args:
        text (str): The text to convert to speech.
        idx (int): The index of the question (for ordering).
        session_id (str): A unique identifier for the session to avoid filename collisions.
        
    Returns:
        dict: Metadata about the generated audio file.
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    inputs = processor(text=text, return_tensors="pt")

    speech = model.generate_speech(
        inputs["input_ids"],
        speaker_embedding,
        vocoder=vocoder
    )

    filename = f"question_{session_id}_{idx}.wav"
    filepath = AUDIO_DIR / filename

    sf.write(str(filepath), speech.numpy(), samplerate=16000)

    return {
        "audio_url": f"/audio/{filename}",
        "file_path": str(filepath),
        "sample_rate": 16000,
        "duration": len(speech) / 16000
    }
