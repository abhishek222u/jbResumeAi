import requests
import json

def test_generate_and_speak():
    url = "http://127.0.0.1:8000/tts/generate-and-speak"
    
    # This is the JSON body you need to send in Postman
    payload = {
        "skills": ["Python", "Docker", "FastAPI"],
        "experience": [
            {
                "title": "Senior Developer",
                "company": "Tech Solutions Inc",
                "description": "Built API services."
            }
        ],
        "education": [
            {
                "degree": "B.Sc Computer Science",
                "institution": "State University"
            }
        ]
    }
    
    try:
        print(f"Sending POST request with payload: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success!")
            print(f"🔹 GENERATED QUESTION: \"{data['question']}\"")
            print(f"🔹 AUDIO PATH: {data['audio_path']}")
            print(f"🔹 MESSAGE: {data['message']}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate_and_speak()
