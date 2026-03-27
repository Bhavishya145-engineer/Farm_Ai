# FarmAI - Setup & Troubleshooting Guide

## **Quick Start**

### Method 1: Using the Batch File (Recommended - Windows)
1. Double-click **`start_farmai.bat`** in your project folder
2. The backend server and web interface will open automatically
3. Access the app at **http://127.0.0.1:8000**

### Method 2: Manual Start
1. Open PowerShell/Command Prompt in the project folder
2. Run: `python -m uvicorn crop:app --reload --host 127.0.0.1 --port 8000`
3. Open your browser and go to **http://127.0.0.1:8000**

---

## **Installation Requirements**

The following Python packages are required:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - Database ORM
- **passlib** & **bcrypt** - Password hashing
- **scikit-learn** - ML model for crop recommendation
- **pandas & numpy** - Data processing
- **joblib** - Model serialization
- **python-multipart** - File upload handling

All dependencies are listed in `requirements.txt`

### **Install Dependencies**
```bash
python -m pip install -r requirements.txt
```

Or install manually:
```bash
python -m pip install fastapi uvicorn sqlalchemy passlib bcrypt python-multipart scikit-learn pandas numpy joblib
```

---

## **Error: "An error occurred. Is the backend running?"**

### **Most Common Causes:**

#### **1. Backend Not Started**
- **Solution**: Make sure the backend is running on `http://127.0.0.1:8000`
- Run the batch file or manually start uvicorn (see Quick Start above)

#### **2. Missing Dependencies**
- **Solution**: Install required packages
```bash
python -m pip install -r requirements.txt
```

#### **3. HTML Files Opened as Files** (file:// protocol)
- **Issue**: If you directly open `.html` files from the file system, CORS will block API calls
- **Solution**: Always access through the web server at `http://127.0.0.1:8000`

#### **4. Port 8000 Already in Use**
- **Solution**: Kill the process using port 8000 or change the port
```bash
# Change port in start_farmai.bat or run:
python -m uvicorn crop:app --port 8001
```

#### **5. Firewall/Network Issues**
- **Solution**: Ensure `127.0.0.1:8000` is not blocked by your firewall

---

## **Project Structure**

```
- crop.py                  # Main FastAPI application
- crop ui.html            # Main crop recommendation interface
- login.html              # Login page
- register.html           # Registration page
- profile.html            # User profile page
- change_password.html    # Password change page
- results.html            # Results display page
- crop_model.joblib       # Trained ML model
- Crop_recommendation/    # Training data
- static/uploads/         # User profile pictures & uploads
- start_farmai.bat        # Startup script (Windows)
- requirements.txt        # Python dependencies
- sql_app.db             # SQLite database (auto-created)
```

---

## **API Endpoints**

### **Health & Status**
- `GET /health` - Check if backend is running

### **Crop Prediction**
- `POST /predict` - Get crop recommendations based on soil/weather data

### **User Management**
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /change-password` - Change password
- `PUT /users/{username}` - Update user profile
- `POST /users/{username}/profile-picture` - Upload profile picture

### **HTML Pages**
- `GET /` - Main crop recommendation interface
- `GET /login-page` - Login page
- `GET /register-page` - Registration page
- `GET /profile-page` - User profile page
- `GET /results-page` - Results page

---

## **Database**

- **Type**: SQLite (lightweight, file-based)
- **Location**: `sql_app.db` (auto-created in project root)
- **Tables**: 
  - `users` - Stores user accounts and profiles

### **Reset Database**
Delete `sql_app.db` and restart the server to create a fresh database.

---

## **Features**

✓ Crop recommendation based on soil conditions  
✓ User registration & login  
✓ User profiles with picture upload  
✓ Real-time predictions from ML model  
✓ Responsive UI with Tailwind CSS  
✓ CORS-enabled API for cross-origin requests  

---

## **Troubleshooting Checklist**

- [ ] Python 3.8+ is installed
- [ ] All dependencies installed: `python -m pip install -r requirements.txt`
- [ ] Backend running on http://127.0.0.1:8000 (not file://)
- [ ] Port 8000 is available
- [ ] No firewall blocking localhost:8000
- [ ] Browser console shows no CORS errors (F12 > Console)
- [ ] Check backend logs for any error messages

---

## **Support & Next Steps**

If you're still having issues:
1. Check the backend terminal for error messages
2. Open browser Developer Tools (F12) → Console tab
3. Verify the server is running with: `python -m uvicorn crop:app --reload`

**Happy farming! 🌾**
