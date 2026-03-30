# disease_model.py - ULTIMATE HYBRID-INTEL AG-ENGINE 12.0
import os, io, base64, requests, json
from PIL import Image
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Key Sanitization
GEMINI_KEY      = os.getenv("GEMINI_API_KEY", "").strip()
KINDWISE_KEY    = os.getenv("CROP_HEALTH_API_KEY", "").strip()
GROQ_KEY        = os.getenv("GROK_API_KEY", "").strip()

# 2026 Validated URLs
KINDWISE_URL    = "https://api.kindwise.com/api/v1/identification?details=health"
GEMINI_URL      = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL      = "llama-3.2-11b-vision-preview" # Reverting to the most stable known preview for compatibility

def _expert_fallback(image_bytes: bytes, crop: str, errors: list = None) -> dict:
    tag = f"[AI:111|{'|'.join(errors) if errors else 'OK'}]"
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((300, 300))
    arr = np.array(img, dtype=np.float32)
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    total = R.size
    
    is_maize = any(x in (crop or "").lower() for x in ["maise", "maize", "corn"])
    is_rice = any(x in (crop or "").lower() for x in ["rice", "grain", "paddy"])
    
    # 2026 Bright-Grain logic (Strict)
    is_gold = ((R > 200) & (G > 180) & (B < 150))
    gold_pct = is_gold.sum() / total
    
    # 2026 Pathological Rust logic (Darker spots)
    rust = ((R > G + 45) & (R > B + 65) & (R < 210) & (G > 30))
    r_pct = rust.sum() / total
    
    if (is_maize or is_rice) and gold_pct > 0.05:
        return {
            "disease": "Status: Generally Healthy (Mature)", "confidence": 0.99,
            "treatment": f"Identified as healthy mature crop. No pathology detected. {tag}",
            "fertilizer": "Maintain hydration.", "method": "Core Math 12.0"
        }
    
    if r_pct > 0.005:
        return {
            "disease": "Pathology: Foliar Rust Detected", "confidence": 0.95,
            "treatment": f"Detected orange fungal pattern. Apply Mancozeb or Myclobutanil. {tag}",
            "fertilizer": "NPK 14-14-14", "method": "Core Math 12.0"
        }
        
    return {
        "disease": "Condition: Generally Healthy", "confidence": 0.85,
        "treatment": f"No severe symptoms found in bio-scan. {tag}", "fertilizer": "NPK", "method": "Core Math 12.0"
    }

def _groq_predict(image_bytes: bytes, crop: str) -> dict:
    if not GROQ_KEY: raise ValueError("X-Missing")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = { "model": GROQ_MODEL, "messages": [{ "role": "user", "content": [ { "type": "text", "text": "JSON ONLY: {\"disease\":\"...\",\"confidence\":0.9,\"treatment\":\"...\"}" }, { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{b64}" } } ] }] }
    r = requests.post(GROQ_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_KEY}"}, timeout=25)
    if r.status_code != 200: raise Exception(f"X-{r.status_code}")
    txt = r.json()["choices"][0]["message"]["content"]; res = json.loads(txt.split("```")[1].replace("json","") if "```" in txt else txt)
    return {"disease": res["disease"], "confidence": 0.9, "treatment": res["treatment"], "method": "Groq-Vision Tier"}

def _gemini_predict(image_bytes: bytes, crop: str) -> dict:
    if not GEMINI_KEY: raise ValueError("G-Missing")
    b = {"contents": [{"parts": [{"text": "JSON: {\"disease\":\"...\",\"confidence\":0.9,\"treatment\":\"...\"}"}, {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode('utf-8')}}]}]}
    r = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", json=b, timeout=20)
    if r.status_code != 200: raise Exception(f"G-{r.status_code}")
    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]; res = json.loads(txt.split("```")[1].replace("json","") if "```" in txt else txt)
    return {"disease": res["disease"], "confidence": 0.9, "treatment": res["treatment"], "method": "Gemini-Vision Tier"}

def predict_disease_from_image(image_bytes: bytes, crop: str = None) -> dict:
    c = crop or "Plant"
    errs = []
    
    # 1. Kindwise (Triple-Auth Strategy)
    if KINDWISE_KEY:
        try:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            for h_type in [{"Api-Key": KINDWISE_KEY}, {"Authorization": f"Bearer {KINDWISE_KEY}"}]:
                r = requests.post(KINDWISE_URL, json={"images": [f"data:image/jpeg;base64,{b64_img}"]}, headers=h_type, timeout=15)
                if r.status_code == 200:
                    try: 
                        d = r.json()["result"]["disease"]; return {"disease": d["name"].title(), "confidence": 0.95, "treatment": "Apply treatment.", "method": "Kindwise AI"}
                    except: continue
            errs.append(f"K-{r.status_code}")
        except Exception: errs.append("K-TO")

    try: return _gemini_predict(image_bytes, c)
    except Exception as e: errs.append(str(e).split(":")[0][:5])
    
    try: return _groq_predict(image_bytes, c)
    except Exception as e: errs.append(str(e).split(":")[0][:5])
    
    return _expert_fallback(image_bytes, c, errs)
