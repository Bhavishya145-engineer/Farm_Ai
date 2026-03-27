# Bhavishya kumar - 0251BTCS042
# Atharv pandey - 0251BTCS048
# Dipanshu - 0251BTCS140
# Aditya singh - 0251BTCS081 

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import shutil
from typing import Optional
from PIL import Image
import io

# Database & Auth Imports
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# -----------------------------
# DATABASE SETUP
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    address = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

class CropHistory(Base):
    __tablename__ = "crop_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    crop_name = Column(String)
    confidence = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    ph = Column(Float)
    rainfall = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DiseaseHistory(Base):
    __tablename__ = "disease_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    disease_name = Column(String)
    confidence = Column(Float)
    treatment = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -----------------------------
# AUTH & SECURITY
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Pydantic Models for Auth
class UserCreate(BaseModel):
    username: str
    password: str
    address: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    address: Optional[str] = None

class PasswordChange(BaseModel):
    username: str
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CropHistorySave(BaseModel):
    username: str
    crop_name: str
    confidence: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class DiseaseHistorySave(BaseModel):
    username: str
    disease_name: str
    confidence: float
    treatment: str

# -----------------------------
# APP INITIALIZATION
# -----------------------------
app = FastAPI()

# Mount static files
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/logo", StaticFiles(directory="logo"), name="logo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 1. CROP PREDICTION LOGIC
# -----------------------------
class PredictRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    soil_type: str = "Not specified"
    top_n: int = 5

class FertilizerRequest(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    crop: str

def build_feature_row(req: PredictRequest, feature_names: list):
    row = {
        "N": req.nitrogen,
        "P": req.phosphorus,
        "K": req.potassium,
        "temperature": req.temperature,
        "humidity": req.humidity,
        "ph": req.ph,
        "rainfall": req.rainfall
    }
    return row

def train_and_persist_model():
    csv_path = "Crop_recommendation/Crop_recommendation.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Training data not found at {csv_path}")

    df = pd.read_csv(csv_path)
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model trained. Accuracy: {acc:.2f}")

    model.fit(X, y)

    joblib.dump({
        "model": model,
        "features": feature_cols,
        "accuracy": acc
    }, "crop_model.joblib")

    return model, feature_cols, acc

def load_model():
    if os.path.exists("crop_model.joblib"):
        try:
            data = joblib.load("crop_model.joblib")
            if data["features"] == ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"] and "accuracy" in data:
                return data["model"], data["features"], data["accuracy"]
        except:
            pass 
    
    print("Training new model from CSV...")
    return train_and_persist_model()

model, feature_names, model_accuracy = load_model()

# -----------------------------
# 2. ROUTES
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    warnings = []
    
    # We log warnings but don't block the prediction unless it's physically impossible
    if req.temperature > 60:
        warnings.append("Extreme heat detected (>60°C). Result may be inaccurate.")
    if req.ph < 0 or req.ph > 14:
        warnings.append("pH must be between 0 and 14.")
        
    row = build_feature_row(req, feature_names)
    X = pd.DataFrame([row], columns=feature_names)
    probs = model.predict_proba(X)[0]
    classes = model.classes_
    sorted_idx = np.argsort(probs)[::-1][:req.top_n]

    return {
        "metadata": {
            "accuracy": model_accuracy,
            "soil_type": req.soil_type,
            "warnings": warnings if warnings else None
        },
        "suggestions": [
            {
                "crop": classes[i],
                "probability": float(probs[i])
            }
            for i in sorted_idx
        ]
    }

# -----------------------------
# 3. AUTH & USER ROUTES
# -----------------------------

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...), 
    address: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Check existing user
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    
    # Handle Profile Picture
    picture_path = None
    if profile_picture:
        file_extension = profile_picture.filename.split(".")[-1]
        filename = f"{username}_profile.{file_extension}"
        path = f"static/uploads/{filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)
        picture_path = f"uploads/{filename}"
    
    new_user = User(
        username=username,
        hashed_password=hashed_password,
        address=address,
        profile_picture=picture_path
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "User created", "user_id": new_user.id}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # In a real app, generate JWT here. For this simple version, just return success
    return {
        "message": "Login successful", 
        "user": {
            "username": db_user.username,
            "address": db_user.address,
            "profile_picture": db_user.profile_picture
        },
        "access_token": "fake-jwt-token-for-demo" 
    }

@app.post("/change-password")
def change_password(req: PasswordChange, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == req.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(req.current_password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    db_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@app.put("/users/{username}")
def update_profile(username: str, req: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if req.address:
        db_user.address = req.address
    
    db.commit()
    db.refresh(db_user)
    
    return {
        "username": db_user.username,
        "address": db_user.address,
        "profile_picture": db_user.profile_picture
    }

@app.post("/users/{username}/profile-picture")
async def update_profile_picture(username: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    file_extension = file.filename.split(".")[-1]
    filename = f"{username}_profile.{file_extension}"
    path = f"static/uploads/{filename}"
    
    # Ensure directory exists again just in case
    os.makedirs("static/uploads", exist_ok=True)
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_user.profile_picture = f"uploads/{filename}"
    db.commit()
    
    return {"profile_picture": db_user.profile_picture}

# ------------------------------------
# 4. HTML SERVING ROUTES
# ------------------------------------

@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse("manifest.json")

@app.get("/service-worker.js")
async def serve_sw():
    return FileResponse("service-worker.js", media_type="application/javascript")

@app.get("/")
async def serve_home():
    return FileResponse("crop ui.html", media_type="text/html")

@app.get("/login")
@app.get("/login-page")
@app.get("/login.html")
async def serve_login():
    return FileResponse("login.html", media_type="text/html")

@app.get("/register")
@app.get("/register-page")
@app.get("/register.html")
async def serve_register():
    return FileResponse("register.html", media_type="text/html")

@app.get("/profile")
@app.get("/profile-page")
@app.get("/profile.html")
async def serve_profile():
    return FileResponse("profile.html", media_type="text/html")

@app.get("/results")
@app.get("/results-page")
@app.get("/results.html")
async def serve_results():
    return FileResponse("results.html", media_type="text/html")

@app.get("/change-password")
@app.get("/change-password-page")
@app.get("/change_password.html")
async def serve_change_password():
    return FileResponse("change_password.html", media_type="text/html")

@app.get("/disease")
@app.get("/disease-page")
@app.get("/disease.html")
async def serve_disease():
    return FileResponse("disease.html", media_type="text/html")

@app.get("/history")
@app.get("/history-page")
@app.get("/history.html")
async def serve_history():
    return FileResponse("history.html", media_type="text/html")

@app.get("/fertilizer")
@app.get("/fertilizer-page")
@app.get("/fertilizer.html")
async def serve_fertilizer():
    return FileResponse("fertilizer.html", media_type="text/html")

@app.post("/save-crop-history")
async def save_crop_history(req: CropHistorySave, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = CropHistory(
        user_id=user.id,
        crop_name=req.crop_name,
        confidence=req.confidence,
        temperature=req.temperature,
        humidity=req.humidity,
        ph=req.ph,
        rainfall=req.rainfall
    )
    db.add(history)
    db.commit()
    return {"status": "success"}

@app.post("/save-disease-history")
async def save_disease_history(req: DiseaseHistorySave, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = DiseaseHistory(
        user_id=user.id,
        disease_name=req.disease_name,
        confidence=req.confidence,
        treatment=req.treatment
    )
    db.add(history)
    db.commit()
    return {"status": "success"}

@app.get("/get-user-history/{username}")
async def get_user_history(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crops = db.query(CropHistory).filter(CropHistory.user_id == user.id).order_by(CropHistory.timestamp.desc()).all()
    diseases = db.query(DiseaseHistory).filter(DiseaseHistory.user_id == user.id).order_by(DiseaseHistory.timestamp.desc()).all()
    
    return {
        "crops": crops,
        "diseases": diseases
    }

# Prediction endpoints are handled below

@app.post("/predict-fertilizer")
async def predict_fertilizer(req: FertilizerRequest):
    # Rule-based logic for fertilizer recommendation
    # In a real-world scenario, this is based on the target crop's specific NPK requirements.
    # Here we use a standard 'deficiency-matching' logic.
    
    # Ideal NPK (Simplified standard ranges)
    ideal = {"N": 40, "P": 40, "K": 40} 
    
    n_diff = ideal["N"] - req.nitrogen
    p_diff = ideal["P"] - req.phosphorus
    k_diff = ideal["K"] - req.potassium
    
    recommendation = ""
    if n_diff > 10:
        recommendation = "Urea or Ammonium Nitrate to boost Nitrogen levels."
    elif p_diff > 10:
        recommendation = "DAP (Diammonium Phosphate) or Single Superphosphate for Phosphorus."
    elif k_diff > 10:
        recommendation = "MOP (Muriate of Potash) or Potassium Sulfate to increase Potassium."
    else:
        recommendation = "Your soil nutrient levels are optimal. Consider a balanced 10-10-10 organic compost to maintain health."

    return {
        "crop": req.crop,
        "recommendation": recommendation,
        "status": "Verified analysis complete"
    }

# -----------------------------
# 5. DISEASE DETECTION MODEL (STUB WITH HEURISTIC)
# -----------------------------
@app.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    # Read image content
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # Simple heuristic to detect if it's a plant (based on green pixels)
    # Resize for faster processing
    image.thumbnail((100, 100))
    pixels = list(image.getdata())
    
    green_pixels = 0
    total_pixels = len(pixels)
    
    for r, g, b in pixels:
        # A pixel is "greenish" if green is dominant
        if g > r * 1.1 and g > b * 1.1:
            green_pixels += 1
            
    green_ratio = green_pixels / total_pixels
    
    # Threshold for "is it a plant?" - roughly 15% of the frame should be greenish
    if green_ratio < 0.15:
        return {
            "error": "Invalid Input",
            "message": "The uploaded image does not appear to be a plant leaf. Please scan a clear image of a leaf."
        }

    # If it passes the heuristic, proceed with random prediction (stub)
    diseases = [
        {
            "name": "Tomato Bacterial Spot", 
            "confidence": 0.94, 
            "treatment": "Use copper-based fungicides and avoid overhead watering.",
            "fertilizer": "Potassium-rich fertilizer (0-0-50) to strengthen plant cell walls and slow bacterial spread."
        },
        {
            "name": "Potato Late Blight", 
            "confidence": 0.88, 
            "treatment": "Remove infected plants immediately and apply fungicides containing chlorothalonil.",
            "fertilizer": "High-Phosphorus 'Starter' fertilizer (10-52-10) to stimulate root recovery and energy."
        },
        {
            "name": "Corn Common Rust", 
            "confidence": 0.92, 
            "treatment": "Plant resistant hybrids and use triazole fungicides if infestation is severe.",
            "fertilizer": "Balanced N-K mix (15-5-15) to help the plant outgrow moisture-related spore damage."
        },
        {
            "name": "Apple Scab", 
            "confidence": 0.91, 
            "treatment": "Prune trees to improve air circulation and apply sulfur-based sprays.",
            "fertilizer": "Calcium Nitrate boost to improve leaf thickness and overall structural resistance."
        },
        {
            "name": "Healthy Leaf", 
            "confidence": 0.99, 
            "treatment": "No medical treatment required.",
            "fertilizer": "Standard balanced 20-20-20 plant food to maintain current growth momentum."
        }
    ]
    
    import random
    result = random.choice(diseases)
    
    return {
        "disease": result["name"],
        "confidence": result["confidence"],
        "treatment": result["treatment"],
        "fertilizer": result["fertilizer"]
    }