# 🔥 Firebase Setup Guide - Step by Step

**What Firebase is used for:**
- ✅ **File Storage** - Store uploaded PDFs, Excel, CSV files
- ✅ **Authentication** - User login (Email + Google Sign-In)
- ✅ **Database** - Firestore (for production, currently using SQLite locally)

**Important:** Firebase is **OPTIONAL** for local development. The system works without it, but it's **recommended for production deployment**.

---

## 📋 Quick Summary

**Do you need Firebase?**
- **Local Development:** ❌ Not required (system uses SQLite + local storage)
- **Production Deployment:** ✅ Recommended (better scalability, security)

**If you're just testing locally, you can skip Firebase setup!**

---

## 🚀 Step-by-Step Setup (15 Minutes)

### Step 1: Go to Firebase Console

1. Open your web browser
2. Go to: **https://console.firebase.google.com/**
3. Sign in with your **Google account** (same account as Gemini API)

---

### Step 2: Create Firebase Project

1. Click **"Add project"** (or "Create a project")
2. Enter project name: `accreditation-platform` (or any name you like)
3. Click **"Continue"**
4. **Disable** Google Analytics (optional - you can enable later)
5. Click **"Create project"**
6. Wait for setup (30-60 seconds)
7. Click **"Continue"**

**✅ Project created!**

---

### Step 3: Enable Firebase Storage (For File Uploads)

1. In the left sidebar, click **"Storage"**
2. Click **"Get started"** button
3. Click **"Next"** (use default security rules)
4. Choose a location (closest to you, e.g., `us-central`, `asia-south1`)
5. Click **"Done"**
6. Wait for Storage to be created (10-20 seconds)

**✅ Storage enabled!**

**Note:** You'll see your bucket name like: `accreditation-platform.appspot.com` - **copy this name!**

---

### Step 4: Enable Firebase Authentication (Optional - for user login)

1. In the left sidebar, click **"Authentication"**
2. Click **"Get started"**
3. Click **"Sign-in method"** tab
4. Enable **"Email/Password"**:
   - Click on "Email/Password"
   - Toggle **"Enable"** to ON
   - Click **"Save"**
5. Enable **"Google"** (optional):
   - Click on "Google"
   - Toggle **"Enable"** to ON
   - Enter support email
   - Click **"Save"**

**✅ Authentication enabled!**

---

### Step 5: Get Service Account Key (IMPORTANT!)

This is what your backend needs to access Firebase.

1. Click the **gear icon ⚙️** (top left, next to "Project Overview")
2. Click **"Project settings"**
3. Go to **"Service accounts"** tab
4. Click **"Generate new private key"** button
5. A popup will appear - click **"Generate key"**
6. A JSON file will download automatically!
   - File name: `accreditation-platform-xxxxx-firebase-adminsdk-xxxxx.json`
   - **IMPORTANT:** Save this file somewhere safe (e.g., `C:\Users\datta\OneDrive\Desktop\gdg\backend\`)

**✅ Service account key downloaded!**

**⚠️ SECURITY WARNING:** This file contains sensitive credentials. Never commit it to Git!

---

### Step 6: Add to `.env` File

1. Open your `.env` file: `C:\Users\datta\OneDrive\Desktop\gdg\.env`
2. Add these lines:

```env
# ============================================
# FIREBASE (Optional - for production)
# ============================================

# Firebase Storage bucket name (from Step 3)
FIREBASE_STORAGE_BUCKET=accreditation-platform.appspot.com

# Path to service account JSON file (from Step 5)
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\datta\OneDrive\Desktop\gdg\backend\accreditation-platform-xxxxx-firebase-adminsdk-xxxxx.json
```

3. **Replace:**
   - `accreditation-platform.appspot.com` with your actual bucket name (from Step 3)
   - `C:\Users\datta\OneDrive\Desktop\gdg\backend\accreditation-platform-xxxxx-firebase-adminsdk-xxxxx.json` with your actual file path

4. Save the file

**✅ Firebase configured!**

---

## 🧪 Test Your Setup

### Test 1: Check if credentials file exists

```powershell
cd C:\Users\datta\OneDrive\Desktop\gdg
Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS
```

Should return: `True`

### Test 2: Verify bucket name

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Bucket:', os.getenv('FIREBASE_STORAGE_BUCKET'))"
```

Should print your bucket name.

### Test 3: Start backend and check logs

```powershell
cd backend
python main.py
```

Look for:
- ✅ `Firebase Storage initialized` (if Storage is configured)
- ✅ `Firebase Admin initialized` (if Auth is configured)
- ⚠️ `Firebase not configured. Using local storage.` (if not configured - this is OK for local dev)

---

## 📝 What Each Service Does

### Firebase Storage
- **What:** Stores uploaded documents (PDFs, Excel, CSV)
- **Fallback:** If not configured, uses local file storage
- **Required for:** Production deployment (better scalability)

### Firebase Authentication
- **What:** User login (Email + Google Sign-In)
- **Fallback:** If not configured, authentication is disabled
- **Required for:** Production deployment (secure user access)

### Firestore Database
- **What:** Cloud database (replaces SQLite)
- **Current:** System uses SQLite locally (Firestore not yet migrated)
- **Required for:** Future production deployment

---

## ⚠️ Common Issues

### Issue 1: "GOOGLE_APPLICATION_CREDENTIALS not found"
**Fix:**
- Check the file path in `.env` is correct
- Use full Windows path: `C:\Users\...\file.json`
- Make sure the JSON file exists at that location

### Issue 2: "FIREBASE_STORAGE_BUCKET not set"
**Fix:**
- Check bucket name in `.env` matches your Firebase project
- Bucket name format: `your-project-id.appspot.com`
- Find it in Firebase Console → Storage → Settings

### Issue 3: "Permission denied" errors
**Fix:**
- Make sure service account has proper permissions
- In Firebase Console → IAM & Admin → Service Accounts
- Check the service account has "Storage Admin" and "Firebase Admin" roles

---

## 🎯 Summary

**Minimum Setup (Local Development):**
- ❌ Firebase not required
- ✅ System works with SQLite + local storage

**Recommended Setup (Production):**
- ✅ Firebase Storage (for file uploads)
- ✅ Firebase Authentication (for user login)
- ⏳ Firestore (future - currently using SQLite)

**Your `.env` should have:**
```env
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
```

---

## ✅ Checklist

Before you're done, make sure:

- [ ] Firebase project created
- [ ] Firebase Storage enabled
- [ ] Service account key downloaded
- [ ] Service account JSON file saved to `backend/` folder
- [ ] `.env` file updated with:
  - [ ] `FIREBASE_STORAGE_BUCKET=...`
  - [ ] `GOOGLE_APPLICATION_CREDENTIALS=...`
- [ ] Backend starts without Firebase errors

---

## 🆘 Need Help?

If you get stuck:
1. Check Firebase Console → Project Settings → Service Accounts
2. Verify JSON file path in `.env` is correct
3. Make sure bucket name matches your project
4. Check backend logs for specific error messages

---

## 🎉 You're Done!

Once Firebase is configured:
- ✅ File uploads will go to Firebase Storage (instead of local)
- ✅ User authentication will work (if enabled)
- ✅ System is ready for production deployment

**Remember:** Firebase is optional for local development. The system works fine without it!

