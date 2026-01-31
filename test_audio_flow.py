import requests
import os

BASE_URL = "http://127.0.0.1:8000"
AUDIO_FILE = "app/storage/audio/resume_gen_test_gtts.mp3"
RESUME_FILE = "test_resume.pdf" # Dummy, we'll create one or assume one

def create_dummy_resume():
    with open("dummy_resume.pdf", "wb") as f:
        f.write(b"%PDF-1.4 dummy content")

def test_audio_loop():
    create_dummy_resume()
    
    # 1. Start Interview
    print("1. Starting Interview...")
    with open("dummy_resume.pdf", "rb") as f:
        files = {"file": ("resume.pdf", f, "application/pdf")}
        res = requests.post(f"{BASE_URL}/interview/start", files=files)
    
    if res.status_code != 200:
        print(f"Start Failed: {res.text}")
        return

    data = res.json()
    session_id = data["session_id"]
    print(f"Session Started: {session_id}")
    print(f"Question 1: {data['current_question']}")
    
    # 2. Submit Audio Answer
    print("\n2. Submitting Audio Answer...")
    
    # Ensure audio exists
    if not os.path.exists(AUDIO_FILE):
        # Create dummy if not exists
        with open("dummy_audio.mp3", "wb") as f:
            f.write(b"fake audio")
        audio_path = "dummy_audio.mp3"
    else:
        audio_path = AUDIO_FILE

    with open(audio_path, "rb") as f:
        # Note: 'file' is the key expected by UploadFile
        files = {"file": ("answer.mp3", f, "audio/mpeg")}
        data = {"session_id": session_id}
        res2 = requests.post(f"{BASE_URL}/interview/next", data=data, files=files)
        
    if res2.status_code != 200:
        print(f"Next Failed: {res2.text}")
    else:
        d2 = res2.json()
        print("✅ Answer Accepted!")
        print(f"Status: {d2['message']}")
        print(f"Next Question: {d2['next_question']}")
        print(f"Progress: {d2['progress']}")

    # 3. Check Feedback
    print("\n3. Checking Feedback...")
    res3 = requests.get(f"{BASE_URL}/interview/feedback?session_id={session_id}")
    print(res3.json())

if __name__ == "__main__":
    test_audio_loop()
