# disease_model.py - HIGH PRECISION AG-ENGINE
# Multi-Tier Strategy: 
# 1. Kindwise Crop Health API (Dedicated Plant-AI)
# 2. Google Gemini 1.5 Flash (General Vision AI)
# 3. Expert Knowledge Base (Color/Pattern Fallback)

import os, io, base64, requests, json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
CROP_HEALTH_API_KEY = os.getenv("CROP_HEALTH_API_KEY", "")
GEMINI_URL          = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
KINDWISE_URL        = "https://crop.kindwise.com/api/v1/health_assessment"

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
# Tier 1: Kindwise Crop Health (Dedicated Precision)
# ---------------------------------------------------------------
def _kindwise_predict(image_bytes: bytes) -> dict:
    if not CROP_HEALTH_API_KEY:
        raise ValueError("Kindwise Key Missing")
    
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [f"data:image/jpeg;base64,{b64}"],
        "latitude": 49.207, "longitude": 16.608, # Optional defaults
        "similar_images": True
    }
    headers = {"Content-Type": "application/json", "Api-Key": CROP_HEALTH_API_KEY}
    
    resp = requests.post(KINDWISE_URL, json=payload, headers=headers, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    
    res = data["health"]
    is_healthy = res.get("is_healthy", True)
    
    # Get top suggestion
    suggestions = res.get("diseases", [])
    if is_healthy or not suggestions:
        return {
            "disease":    "Plant Status: Healthy",
            "confidence": float(res.get("is_healthy_probability", 0.95)),
            "treatment":  "Maintain current irrigation. No chemical treatment needed.",
            "fertilizer": "Maintain balanced NPK schedule.",
            "method":     "Kindwise Industrial Plant-AI (Verified Healthy)"
        }
    
    top = suggestions[0]
    return {
        "disease":    top.get("name", "Unknown Issue"),
        "confidence": float(top.get("probability", 0.85)),
        "treatment":  "Apply recommended fungicide/pesticide. Quarantine infected crops.",
        "fertilizer": "Check macro-nutrient balance.",
        "method":     "Kindwise Industrial Plant-AI (Diagnostic)"
    }

# ---------------------------------------------------------------
# Tier 2: Google Gemini (Vision AI)
# ---------------------------------------------------------------
def _gemini_predict(image_bytes: bytes, crop: str = "Plant") -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("Gemini Key Missing")

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = f"""Identify the crop ({crop}) and state exactly if it is healthy or diseased.
If healthy, return status as Healthy. If diseased, specify the disease name.
Return JSON ONLY: {{"is_leaf":true,"crop":"name","disease":"Status","confidence":0.9,"treatment":"steps","fertilizer":"NPK"}}"""

    payload = {
        "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 300}
    }
    
    resp = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload, timeout=15)
    resp.raise_for_status()
    res_data = resp.json()
    text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    if "```" in text: text = text.split("```")[1].strip(); 
    if text.startswith("json"): text = text[4:].strip()
    
    result = json.loads(text)
    return {
        "disease":    result.get("disease", "Status: Healthy"),
        "confidence": float(result.get("confidence", 0.9)),
        "treatment":  result.get("treatment", "Standard Care."),
        "fertilizer": result.get("fertilizer", "Balanced NPK."),
        "method":     "Google Gemini Vision Engine"
    }

# ---------------------------------------------------------------
# Tier 3: Expert Fallback (Safe Logic)
# ---------------------------------------------------------------
def _expert_fallback(image_bytes: bytes, crop: str) -> dict:
    from PIL import Image
    import numpy as np
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((150, 150))
    arr = np.array(img, dtype=np.float32)
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    
    green = ((G > R * 1.0) & (G > B * 1.0)).sum() / R.size
    spots = ((R > 130) & (G < 150)).sum() / R.size # Simplified rust check
    
    crop_title = crop.title() if crop else "Plant"
    
    if green > 0.45 and spots < 0.08:
        return {
            "disease":    f"{crop_title}: Healthy",
            "confidence": 0.95,
            "treatment":  "Plant appears healthy.",
            "fertilizer": "Maintain regular feeding.",
            "method":     "Internal Color Intelligence"
        }
    return {
        "disease":    f"{crop_title}: Potential Fungal Sign",
        "confidence": 0.65,
        "treatment":  "Apply organic neem oil. Observe for 48h.",
        "fertilizer": "N/A",
        "method":     "Safety Fallback Algorithm"
    }

# ---------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------
def predict_disease_from_image(image_bytes: bytes, crop: str = None) -> dict:
    crop_name = (crop or "").strip() or "Plant"
    
    # Tier 1: Dedicated Crop Specialist
    if CROP_HEALTH_API_KEY:
        try:
            return _kindwise_predict(image_bytes)
        except Exception as e:
            print(f"Kindwise Error: {e}")
            
    # Tier 2: AI Vision Generalist
    if GEMINI_API_KEY:
        try:
            return _gemini_predict(image_bytes, crop_name)
        except Exception as e:
            print(f"Gemini Error: {e}")
            
    # Tier 3: Resilient Fallback
    return _expert_fallback(image_bytes, crop_name)
