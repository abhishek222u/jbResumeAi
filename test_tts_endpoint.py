import requests

def test_tts():
    url = "http://127.0.0.1:8000/tts/speak"
    payload = {
        "text": "Hello, this is a verify check from the agent.",
        "filename_prefix": "agent_verify"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tts()
