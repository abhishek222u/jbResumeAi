import requests
import io
import time

# Minimal valid PDF with "Hello World" (approximate)
# Use a simple function to generate a valid PDF or use a hardcoded minimal PDF
dummy_pdf_content = (
    b"%PDF-1.1\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n"
    b"4 0 obj\n<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Helvetica >>\nendobj\n"
    b"5 0 obj\n<< /Length 55 >>\nstream\nBT /F1 12 Tf 100 700 Td (Skills: Python, FastAPI. Experience: 5 years) Tj ET\nendstream\nendobj\n"
    b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000244 00000 n \n0000000334 00000 n \n"
    b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n440\n%%EOF\n"
)

def test_full_interview_flow():
    base_url = "http://127.0.0.1:8000"
    
    print("\n--- 1. Testing Start Interview (Upload Resume) ---")
    files = {
        'file': ('dummy_resume.pdf', dummy_pdf_content, 'application/pdf')
    }
    
    try:
        response = requests.post(f"{base_url}/interview/start", files=files)
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"✅ Success! Session ID: {session_id}")
            print(f"Parsed Question 1: {data['current_question']}")
            print(f"Audio Path: {data['audio_path']}")
            
            # Verify audio file exists or is valid path
            # (In a real test we might download it, here we just check the string)
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return
            
        print("\n--- 2. Testing Next Question (Submit Answer) ---")
        # Submit a dummy answer
        payload = {
            "session_id": session_id,
            "answer": "I have 5 years of experience in Python."
        }
        
        response = requests.post(f"{base_url}/interview/next", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Progress: {data['progress']}")
            print(f"Next Question: {data['next_question']}")
            print(f"Audio Path: {data['audio_path']}")
        else:
             print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_interview_flow()
