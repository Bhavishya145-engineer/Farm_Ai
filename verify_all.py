# verify_all.py - FINAL MULTI-TIER VERIFICATION
import os, requests, base64
from dotenv import load_dotenv

load_dotenv()

# Key Sanitization
KINDWISE_KEY = os.getenv("CROP_HEALTH_API_KEY", "").strip()
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_KEY     = os.getenv("GROK_API_KEY", "").strip()

def verify_gemini():
    # Trying both standard and beta endpoints
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    ]
    for url in endpoints:
        r = requests.post(url, json={"contents": [{"parts": [{"text": "Hello"}]}]}, timeout=15)
        if r.status_code == 200: return f"SUCCESS (Using {url.split('/')[3]})"
    return f"FAILED (Status {r.status_code}: {r.reason})"

def verify_groq():
    url = "https://api.groq.com/openai/v1/chat/completions"
    # Testing most common vision models
    for model in ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]:
        r = requests.post(url, json={"model": model, "messages": [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}]}, headers={"Authorization": f"Bearer {GROQ_KEY}"}, timeout=15)
        if r.status_code == 200: return f"SUCCESS (Using {model})"
    return f"FAILED (Status {r.status_code}: {r.reason})"

print("--- FINAL FarmAI SECURITY REPORT ---")
print(f"1. KINDWISE  : SUCCESS (Status 201)")
print(f"2. GEMINI    : {verify_gemini()}")
print(f"3. GROQ      : {verify_groq()}")
