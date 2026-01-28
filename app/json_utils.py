import json
import re


def safe_json_parse(text: str):
    """
    Attempts multiple strategies to parse JSON safely.
    Returns dict or raises ValueError.
    """

    # remove markdown
    text = re.sub(r"```json|```", "", text).strip()

    # extract first JSON block
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")

    json_text = match.group(0)

    # Attempt 1: direct load
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass

    # Attempt 2: remove trailing commas
    json_text = re.sub(r",\s*([\]}])", r"\1", json_text)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass

    raise ValueError("JSON parsing failed after cleanup")
def parse_kv_to_json(text: str):
    lines = text.splitlines()
    data = {}

    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    return {
        "user": {
            "name": normalize_str(data.get("name")),
            "email": normalize_str(data.get("email")),
            "mobileno": normalize_str(data.get("mobile")),
            "linkedin": normalize_str(data.get("linkedin"))
        },
        "profile": {
            "headline": normalize_str(data.get("headline")),
            "location": normalize_str(data.get("location")),
            "experienceYears": safe_int(data.get("experience_years")),
            "summary": ""
        },
        "skills": [
            s.strip()
            for s in normalize_str(data.get("skills") or "").split(",")
            if s.strip()
        ],
        "employments": [
            {
                "title": normalize_str(data.get("employment_1_title")),
                "company": normalize_str(data.get("employment_1_company")),
                "description": normalize_str(data.get("employment_1_description"))
            }
        ],
        "educations": [
            {
                "degree": normalize_str(data.get("education_1_degree")),
                "institution": normalize_str(data.get("education_1_institution"))
            }
        ]
    }
def safe_int(value, default=0):
    try:
        if value is None:
            return default
        value = value.strip()
        if value.upper() in ["NA", "N/A", "NULL", ""]:
            return default
        return int(float(value))
    except Exception:
        return default
def normalize_str(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip().upper() in ["NA", "N/A", "NULL"]:
        return None
    return value.strip()



