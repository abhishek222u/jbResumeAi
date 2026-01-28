from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    token=os.getenv("HF_API_KEY")
)

def run_llm(prompt: str, max_tokens=512):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a resume parser. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9
    )

    return response.choices[0].message.content
