# How to generate your FarmAI.apk

I have generated the native Android source code for your app. An `.apk` is a compiled file, so you need the Android SDK to "build" it.

### Option 1: Using Android Studio (Professional)
1.  **Download & Install** [Android Studio](https://developer.android.com/studio).
2.  Open Android Studio and select **"Open"**.
3.  Navigate to the `android_native` folder in your project.
4.  **Important**: Open `app/src/main/java/com/farmai/app/MainActivity.java` and change the line:
    `myWebView.loadUrl("http://192.168.1.10:8000");`
    to your computer's actual IP address.
5.  Go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
6.  Android Studio will generate an `app-debug.apk`. Transfer this to your phone and install it!

### Option 2: Using Website to APK (Simplest)
If you don't want to code in Java, you can use a tool like [Web2App](https://www.web2app.com/) or similar:
1.  Enter your server URL: `http://[YOUR_IP]:8000`
2.  Upload the `logo/logo.png` as the icon.
3.  Click "Build".

### Why a Native App?
-   **No Browser UI**: It looks like a real app from the Play Store.
-   **Permissions**: It remembers your Camera and Location permissions permanently.
-   **Performance**: Better memory management for image scanning.

---
*Note: Your Python server must be running on your PC for the app to function.*
