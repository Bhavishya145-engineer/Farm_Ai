# check_keys.py - PROFESSIONAL API KEY VERIFICATION
import os, requests, base64
from dotenv import load_dotenv

load_dotenv()

# Key Sanitization
KINDWISE_KEY = os.getenv("CROP_HEALTH_API_KEY", "").strip()
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_KEY     = os.getenv("GROK_API_KEY", "").strip()

# Dummy Image (small red dot)
DUMMY_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def test_kindwise():
    url = "https://crop.kindwise.com/api/v1/identification?details=health"
    payload = {"images": [f"data:image/jpeg;base64,{DUMMY_B64}"]}
    r = requests.post(url, json=payload, headers={"Api-Key": KINDWISE_KEY}, timeout=15)
    return r.status_code, r.reason

def test_gemini():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": "Is this plant healthy?"}]}]}
    r = requests.post(url, json=payload, timeout=15)
    return r.status_code, r.reason

def test_groq():
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {"model": "llama-3.2-11b-vision-preview", "messages": [{"role": "user", "content": [{"type": "text", "text": "Is this plant healthy?"}]}]}
    r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {GROQ_KEY}"}, timeout=15)
    return r.status_code, r.reason

print("--- FARM AI KEY REPORT ---")
print(f"1. KINDWISE : Status {test_kindwise()}")
print(f"2. GEMINI   : Status {test_gemini()}")
print(f"3. GROQ     : Status {test_groq()}")
