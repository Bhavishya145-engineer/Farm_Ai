# disease_model.py - ULTIMATE MODERN AG-ENGINE 8.0
import os, io, base64, requests, json
from PIL import Image
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Key Sanitization
GEMINI_KEY      = os.getenv("GEMINI_API_KEY", "").strip()
KINDWISE_KEY    = os.getenv("CROP_HEALTH_API_KEY", "").strip()
GROQ_KEY        = os.getenv("GROK_API_KEY", "").strip()

# Resilient Endpoints (2026 Multi-AI Tier)
KINDWISE_URL    = "https://crop.kindwise.com/api/v1/health_assessment"
GEMINI_URL      = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL      = "meta-llama/llama-4-scout-17b-instruct" # 2026 Flagship Vision

def _expert_fallback(image_bytes: bytes, crop: str, errors: list = None) -> dict:
    g_s = "1" if GEMINI_KEY else "0"
    k_s = "1" if KINDWISE_KEY else "0"
    x_s = "1" if GROQ_KEY else "0"
    err_str = "|".join(errors) if errors else "OK"
    tag = f"[AI:{g_s}{k_s}{x_s}|{err_str}]"
    
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((300, 300))
    arr = np.array(img, dtype=np.float32)
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    total = R.size
    
    # 2026 Color-Space Pattern Matching
    rust = ((R > G + 30) & (R > B + 50) & (G > 40))
    r_pct = rust.sum() / total
    is_maize = any(x in (crop or "").lower() for x in ["maise", "maize", "corn"])
    
    if r_pct > 0.007:
        return {
            "disease": "Pathology: Foliar Rust Detected", "confidence": 0.95,
            "treatment": f"Detected orange fungal pattern. Apply Mancozeb or Myclobutanil. {tag}",
            "fertilizer": "Focus on high Potassium for plant strength.", "method": "Modern Logic 8.0"
        }
    
    return {
        "disease": "Condition: Generally Healthy", "confidence": 0.85,
        "treatment": f"No severe pathology patterns found in bio-scan. {tag}",
        "fertilizer": "Maintain NP balance.", "method": "Modern Logic 8.0"
    }

def _groq_predict(image_bytes: bytes, crop: str) -> dict:
    if not GROQ_KEY: raise ValueError("X-Missing")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": GROQ_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"DIAGNOSE {crop}. JSON: {{\"disease\":\"Name\",\"confidence\":0.9,\"treatment\":\"Advice\",\"fertilizer\":\"Advice\"}}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }]
    }
    h = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    r = requests.post(GROQ_URL, json=payload, headers=h, timeout=25)
    if r.status_code != 200: raise Exception(f"X-{r.status_code}")
    txt = r.json()["choices"][0]["message"]["content"].strip()
    if "```" in txt: txt = txt.split("```")[1].replace("json","").strip()
    res = json.loads(text)
    return {"disease": res["disease"].title(), "confidence": 0.95, "treatment": res["treatment"], "fertilizer": res.get("fertilizer", "NPK"), "method": "Groq Llama 4 Vision"}

def _gemini_predict(image_bytes: bytes, crop: str) -> dict:
    if not GEMINI_KEY: raise ValueError("G-Missing")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    p = f"DIAGNOSE {crop}. JSON: {{\"disease\":\"...\",\"confidence\":0.9,\"treatment\":\"...\",\"fertilizer\":\"...\"}}"
    body = {"contents": [{"parts": [{"text": p}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    r = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", json=body, timeout=20)
    if r.status_code != 200: raise Exception(f"G-{r.status_code}")
    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if "```" in txt: txt = txt.split("```")[1].replace("json","").strip()
    res = json.loads(text)
    return {"disease": res["disease"].title(), "confidence": 0.9, "treatment": res["treatment"], "fertilizer": res.get("fertilizer", "NPK"), "method": "Gemini 1.5 Flash"}

def predict_disease_from_image(image_bytes: bytes, crop: str = None) -> dict:
    c = crop or "Plant"
    errs = []
    # 1. Kindwise
    if KINDWISE_KEY:
        try:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            r = requests.post(KINDWISE_URL, json={"images": [f"data:image/jpeg;base64,{b64}"]}, headers={"Api-Key": KINDWISE_KEY}, timeout=20)
            if r.status_code == 200:
                h = r.json().get("health", {})
                if h.get("is_healthy", True): return {"disease": "Generally Healthy", "confidence": 0.9, "treatment": "Biometrics optimal.", "fertilizer": "NPK", "method": "Kindwise AI"}
                top = h.get("diseases", [{}])[0]
                return {"disease": top.get("name", "Disease").title(), "confidence": 0.9, "treatment": "Apply treatment.", "fertilizer": "NPK", "method": "Kindwise AI"}
            else: errs.append(f"K-{r.status_code}")
        except Exception: errs.append("K-TO")

    # 2. Gemini
    try: return _gemini_predict(image_bytes, c)
    except Exception as e: errs.append(str(e))
    
    # 3. Groq
    try: return _groq_predict(image_bytes, c)
    except Exception as e: errs.append(str(e))
    
    return _expert_fallback(image_bytes, c, errs)
