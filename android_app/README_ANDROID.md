# FarmAI - Android Web Application (PWA)

This is a clone of the FarmAI web application optimized for Android devices as a Progressive Web App (PWA).

## Features
- **Installable**: Can be added to the Android home screen like a native app.
- **Standalone Mode**: Runs without the browser address bar for a native feel.
- **Offline Support**: Basic caching via Service Workers.
- **Mobile Optimized**: Responsive layout designed for touch interaction.

## How to Install on Android

1. **Start the Server**:
   - Run `start_android_app.bat` on your computer.
   - Note your computer's local IP address (e.g., `192.168.1.10`).

2. **Access from Android**:
   - Open Chrome on your Android phone.
   - Enter your computer's IP address and port 8000 (e.g., `http://192.168.1.10:8000`).

3. **Install the App**:
   - When the page loads, you should see an "Add FarmAI to Home screen" prompt.
   - If not, tap the **three dots (menu)** in the top right corner of Chrome.
   - Select **"Install app"** or **"Add to Home screen"**.

4. **Launch**:
   - You will now find the **FarmAI** icon on your phone's home screen. Launch it for a full-screen experience!

## Technical Details
- **Manifest**: `manifest.json` defines app identity.
- **Service Worker**: `service-worker.js` handles caching and background tasks.
- **Backend**: FastAPI (Python) serving mobile-ready HTML/JS.

---
*Created by FarmAI Team*
