# 🔐 Firebase Authentication Fix

## 🔴 Problem

Backend is returning 500 error: `Authentication verification failed`

**Error:** 
```
API Error: 500 {detail: 'Authentication verification failed'}
```

**Root Cause:** Firebase Admin SDK cannot verify tokens without service account credentials.

---

## ✅ Solution: Download Firebase Service Account Key

### Step 1: Go to Firebase Console

1. Open https://console.firebase.google.com/
2. Select your project: **accreditation-platform**
3. Click on **Project Settings** (gear icon)
4. Go to **Service Accounts** tab

### Step 2: Generate Service Account Key

1. Click **Generate New Private Key**
2. Click **Generate Key** in the dialog
3. A JSON file will be downloaded (e.g., `accreditation-platform-xxxxx.json`)

### Step 3: Save the Key File

1. Save the JSON file to your project root or `backend/` directory
2. Example name: `firebase-service-account.json`
3. **Important:** Add this file to `.gitignore` to prevent committing it to git

### Step 4: Update `.env` File

Add the path to the service account file in your `.env` file:

```env
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

Or if saved in backend directory:

```env
GOOGLE_APPLICATION_CREDENTIALS=./backend/firebase-service-account.json
```

### Step 5: Restart Backend

1. Stop the backend server
2. Start it again
3. The backend should now be able to verify Firebase tokens

---

## 🧪 Test the Fix

1. **Start backend:** Should see "Firebase Admin initialized with service account credentials"
2. **Try login:** Should work now without 500 error
3. **Check backend logs:** Should see "Firebase token verified for user: ..."

---

## 📋 What Changed

**Before:**
- Backend initialized with just project ID
- Token verification failed (no credentials)
- Error: 500 "Authentication verification failed"

**After:**
- Backend initialized with service account credentials
- Token verification works
- Login should succeed

---

## 🔒 Security Notes

1. **Never commit the service account JSON file to git**
2. Add `firebase-service-account.json` to `.gitignore`
3. Use environment variables for the path
4. For production, use secure secret management (e.g., AWS Secrets Manager, Google Secret Manager)

---

## ✅ Alternative: Application Default Credentials (Advanced)

If you have Google Cloud CLI installed, you can use Application Default Credentials:

```bash
gcloud auth application-default login
```

Then remove `GOOGLE_APPLICATION_CREDENTIALS` from `.env` and the backend will use ADC.

---

## 🎯 Next Steps

1. Download Firebase service account key
2. Save it to your project
3. Update `.env` with `GOOGLE_APPLICATION_CREDENTIALS`
4. Restart backend
5. Test login - should work!

---

## ✅ Summary

- ✅ Backend startup fixed
- ✅ Database connection fixed
- 🔐 Firebase authentication needs service account key
- 📥 Download service account key from Firebase Console
- 🔄 Update `.env` file with path
- 🚀 Restart backend

**Once you add the service account key, authentication will work! 🎉**

