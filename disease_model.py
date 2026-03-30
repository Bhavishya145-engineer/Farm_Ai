# disease_model.py - HIGH PRECISION AG-ENGINE
# Multi-Tier Strategy: 
# 1. Kindwise Crop Health API (Dedicated Plant-AI)
# 2. Google Gemini 1.5 Flash (General Vision AI)
# 3. Expert Knowledge Base (Color/Pattern Fallback)

import os, io, base64, requests, json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "").strip()
CROP_HEALTH_API_KEY = os.getenv("CROP_HEALTH_API_KEY", "").strip()
GROK_API_KEY        = os.getenv("GROK_API_KEY", "").strip()

# REST Endpoints (Resilient Architecture)
GEMINI_V1BETA  = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_V1      = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
KINDWISE_URL   = "https://crop.kindwise.com/api/v1/health_assessment"
KINDWISE_ALT   = "https://crop.kindwise.com/api/v1/identification?details=health"
GROK_URL       = "https://api.xai.com/v1/chat/completions"

# ---------------------------------------------------------------
# Expert knowledge base
# ---------------------------------------------------------------
EXPERT_KB = {
    "rice":        [("Rice: Blast Disease",              "Apply tricyclazole or isoprothiolane fungicide immediately. Drain field.",        "Reduce Nitrogen. Apply Silica-rich fertilizer."),
                    ("Rice: Brown Spot",                  "Apply propiconazole or mancozeb fungicide. Drain field periodically.",            "Potassium Chloride (MOP 0-0-60)."),
                    ("Rice: Bacterial Leaf Blight",       "Apply copper bactericide. Drain field and avoid excess Nitrogen.",               "Balanced NPK (16-20-0)."),
                    ("Rice: Sheath Blight",               "Apply hexaconazole or propiconazole fungicide.",                                 "Potassium-rich fertilizer (MOP).")],
    "banana":      [("Banana: Sigatoka Leaf Spot",        "Apply mancozeb or propiconazole. Remove infected leaves.",                       "Balanced NPK (15-15-15)."),
                    ("Banana: Black Sigatoka",            "Apply triazole fungicide. Improve drainage.",                                    "Potassium Sulfate (0-0-50)."),
                    ("Banana: Panama Wilt",               "No chemical cure. Remove infected plants. Use resistant varieties.",             "Calcium + Magnesium foliar spray.")],
    "maize":       [("Maize: Gray Leaf Spot",             "Apply triazole or strobilurin fungicide. Rotate crops.",                         "Urea (Nitrogen-rich)."),
                    ("Maize: Common Rust",                "Apply triazole fungicide early. Use resistant varieties.",                       "Balanced N-K (15-5-15)."),
                    ("Maize: Northern Leaf Blight",       "Apply fungicide at tasseling. Rotate crops annually.",                          "High-Nitrogen Urea (46-0-0).")],
    "corn":        [("Maize: Gray Leaf Spot",             "Apply triazole or strobilurin.",                                                 "Balanced NPK (15-15-15).")],
}

# ---------------------------------------------------------------
# Tier 1: Kindwise Crop Health (Scientific Precision Specialist)
# ---------------------------------------------------------------
def _kindwise_predict(image_bytes: bytes) -> dict:
    if not CROP_HEALTH_API_KEY: raise ValueError("AI_EMPTY")
    
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{b64}"],
        "latitude": 20.5, "longitude": 78.5
    }
    headers = {"Content-Type": "application/json", "Api-Key": CROP_HEALTH_API_KEY}
    
    # Try primary endpoint
    resp = requests.post(KINDWISE_URL, json=payload, headers=headers, timeout=20)
    
    # Try fallback endpoint if primary 404s
    if resp.status_code == 404:
        resp = requests.post(KINDWISE_ALT, json=payload, headers=headers, timeout=20)
        
    if resp.status_code != 200:
        raise Exception(f"K-Err:{resp.status_code}")
        
    data = resp.json()
    health = data.get("health") or data.get("result", {}).get("is_healthy_probability")
    if health is None: raise Exception("K-BadSchema")
    
    # Handle different Kindwise JSON structures
    is_healthy = health.get("is_healthy", True) if isinstance(health, dict) else (health > 0.5)
    conf = float(health.get("is_healthy_probability", 0.95)) if isinstance(health, dict) else float(health)
    
    if is_healthy:
        return {
            "disease": "Plant: Generally Healthy", "confidence": conf,
            "treatment": "Plant biometrics appear optimal. [Scientific AI]",
            "fertilizer": "NPK 15-15-15 Maintenance.", "method": "Kindwise Ag-AI"
        }
    
    diseases = health.get("diseases", []) if isinstance(health, dict) else []
    top = diseases[0] if diseases else {"name": "Detected Pathogen", "probability": 0.8}
    name = top.get("name", "Unknown Issue").title()
    
    return {
        "disease": name, "confidence": float(top.get("probability", 0.82)),
        "treatment": f"Diagnosis: {name}. Apply targeted treatment. [Scientific AI]",
        "fertilizer": "Recovery nutrient boost.", "method": "Kindwise Ag-AI"
    }

# ---------------------------------------------------------------
# Tier 2: Google Gemini (High-Level Vision)
# ---------------------------------------------------------------
def _gemini_predict(image_bytes: bytes, crop: str = "Plant") -> dict:
    if not GEMINI_API_KEY: raise ValueError("G-Missing")
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = f"IMAGE DIAGNOSIS: {crop}. If 100% fine, 'Healthy'. If spots/blight/rot, specific name. RETURN JSON: {{\"disease\":\"Name\",\"confidence\":0.9,\"treatment\":\"Advice\",\"fertilizer\":\"Advice\"}}"
    body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    
    # Try endpoints
    resp = requests.post(f"{GEMINI_V1BETA}?key={GEMINI_API_KEY}", json=body, timeout=20)
    if resp.status_code == 404: resp = requests.post(f"{GEMINI_V1}?key={GEMINI_API_KEY}", json=body, timeout=20)
    if resp.status_code != 200: raise Exception(f"G-Err:{resp.status_code}")
    
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if "```" in text: text = text.split("```")[1].replace("json","").strip()
    res = json.loads(text)
    return {
        "disease": res.get("disease", "Healthy").title(),
        "confidence": float(res.get("confidence", 0.90)),
        "treatment": f"{res.get('treatment')} [Gemini-Tier]",
        "fertilizer": res.get("fertilizer", "NPK Balanced"), "method": "Google Vision AI"
    }

# ---------------------------------------------------------------
# Tier 3: xAI Grok Vision (Expert Reasoning Fallback)
# ---------------------------------------------------------------
def _grok_predict(image_bytes: bytes, crop: str = "Plant") -> dict:
    if not GROK_API_KEY: raise ValueError("X-Missing")
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    # xAI uses OpenAI-Style Vision Format
    payload = {
        "model": "grok-1.5-vision-latest",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Expert Ag-Analysis: Identify disease in {crop}. JSON ONLY: {{\"disease\":\"...\",\"confidence\":0.95,\"treatment\":\"...\",\"fertilizer\":\"...\"}}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }]
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GROK_API_KEY}"}
    
    resp = requests.post(GROK_URL, json=payload, headers=headers, timeout=25)
    if resp.status_code != 200: raise Exception(f"X-Err:{resp.status_code}")
    
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if "```" in raw: raw = raw.split("```")[1].replace("json","").strip()
    res = json.loads(raw)
    return {
        "disease": res.get("disease", "Healthy").title(),
        "confidence": float(res.get("confidence", 0.95)),
        "treatment": f"{res.get('treatment')} [Grok-Tier]",
        "fertilizer": res.get("fertilizer", "Organic Boost"), "method": "xAI Grok Vision"
    }

def predict_disease_from_image(image_bytes: bytes, crop: str = None) -> dict:
    crop_name = (crop or "").strip() or "Plant"
    err_logs = []
    
    # Tier 1: Kindwise (Ag-Specialist)
    if CROP_HEALTH_API_KEY:
        try: return _kindwise_predict(image_bytes)
        except Exception as e: err_logs.append(str(e))
            
    # Tier 2: Gemini (Vision Specialist)
    if GEMINI_API_KEY:
        try: return _gemini_predict(image_bytes, crop_name)
        except Exception as e: err_logs.append(str(e))
            
    # Tier 3: Grok (Expert Reasoning Fallback)
    if GROK_API_KEY:
        try: return _grok_predict(image_bytes, crop_name)
        except Exception as e: err_logs.append(str(e))
            
    # Tier 4: Resilient Semantic Fallback
    return _expert_fallback(image_bytes, crop_name, err_logs)
