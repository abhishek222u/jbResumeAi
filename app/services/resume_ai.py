import requests
import json
import os
import re
from dotenv import load_dotenv
###from app.json_utils import parse_kv_to_json,safe_json_parse  
load_dotenv()

API_TOKEN = os.getenv("HF_API_KEY")  # set env variable

HF_URL = "https://router.huggingface.co/v1/chat/completions"

def fix_json_with_llm(broken_json: str):
    repair_prompt = f"""
You are a JSON repair engine.

Fix the following JSON so that it becomes:
- STRICTLY valid JSON
- Parsable by json.loads()
- Escape quotes correctly
- Remove trailing commas
- No markdown, no explanation

Broken JSON:
{broken_json}
"""

    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {"role": "system", "content": "You fix invalid JSON."},
            {"role": "user", "content": repair_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 1200
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(HF_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

def convert_resume_to_json(text: str):
    prompt = f"""
You are an ATS resume parser.

Extract ONLY the following sections from the resume:
- Skills
- Experience
- Education

Return STRICTLY valid JSON.
The JSON MUST be parsable by json.loads().
Do NOT include markdown, comments, or explanations.

Output format MUST be exactly:

{{
  "skills": ["skill1", "skill2", "..."],
  "experience": [
    {{
      "title": "NA",
      "company": "NA",
      "description": "NA"
    }}
  ],
  "education": [
    {{
      "degree": "NA",
      "institution": "NA"
    }}
  ]
}}

Rules:
- Extract ALL experience entries (do NOT merge them)
- Extract ALL education entries
- Skills must be deduplicated
- Preserve original wording
- If a value is missing, use "NA"
- Do NOT add extra fields
- Do NOT return text outside JSON

Resume:
{text}
"""

    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are an ATS resume parser. Return ONLY valid JSON. No markdown. No explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1200
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(HF_URL, headers=headers, json=payload)
    response.raise_for_status()

    raw_text = response.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        fixed = fix_json_with_llm(raw_text)
        return json.loads(fixed)
    
