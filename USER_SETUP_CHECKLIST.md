# ✅ User Setup Checklist

**Quick Reference:** What YOU need to do to get the platform running

---

## 🎯 Minimum Setup (5 Minutes) - REQUIRED

### 1. Google Gemini API Key (FREE) 🆓
**Required for:** Chatbot feature

**Steps:**
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSyAbc123...`)

**Add to `.env` file:**
```env
GEMINI_API_KEY=AIzaSyAbc123...your_key_here
```

**✅ Status:** [ ] Done

---

## 🔧 Recommended Setup (15 Minutes) - OPTIONAL BUT RECOMMENDED

### 2. Google Cloud Vision API (FREE) 🆓
**Required for:** Better OCR (text extraction from PDFs)

**Free Tier:** 1,000 images per month

**Steps:**
1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "Cloud Vision API"
4. Create Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Grant role: "Cloud Vision API User"
   - Create JSON key and download it
5. Save JSON file to: `backend/accreditation-platform-abc123.json` (or any name)

**Add to `.env` file:**
```env
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\datta\OneDrive\Desktop\gdg\backend\accreditation-platform-abc123.json
```
*(Use your actual file path)*

**✅ Status:** [ ] Done

---

### 3. OpenAI API (Optional) 💰
**Required for:** Chatbot fallback (if Gemini fails)

**Cost:** Pay-as-you-go (set a budget limit!)

**Steps:**
1. Go to: https://platform.openai.com/
2. Sign up / Log in
3. Add payment method (set usage limit!)
4. Go to: https://platform.openai.com/api-keys
5. Click "Create new secret key"
6. Copy the key (looks like: `sk-abc123...`)

**Add to `.env` file:**
```env
OPENAI_API_KEY=sk-abc123...your_key_here
OPENAI_MODEL_PRIMARY=gpt-4o-mini
OPENAI_MODEL_FALLBACK=gpt-4o-mini
```

**✅ Status:** [ ] Done (Optional)

---

## 🏗️ Production Setup (Optional - for deployment)

### 4. Firebase (Optional) 🔥
**Required for:** Production deployment (Authentication, Storage)

**Free Tier:** Available

**Steps:**
1. Go to: https://console.firebase.google.com/
2. Create a new project
3. Enable:
   - Authentication (Email/Google Sign-In)
   - Firestore Database
   - Cloud Storage
4. Download service account JSON

**Add to `.env` file:**
```env
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\firebase-service-account.json
```

**✅ Status:** [ ] Done (Optional - only for production)

---

## 📝 Create `.env` File

**Location:** `C:\Users\datta\OneDrive\Desktop\gdg\.env` (project root)

**Template:**
```env
# ============================================
# REQUIRED (Minimum Setup)
# ============================================

# Google Gemini API (FREE - Required for Chatbot)
GEMINI_API_KEY=AIzaSyAbc123...your_actual_key_here

# ============================================
# RECOMMENDED (Better OCR)
# ============================================

# Google Cloud Vision API (FREE - Better OCR)
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\datta\OneDrive\Desktop\gdg\backend\accreditation-platform-abc123.json

# ============================================
# OPTIONAL (Chatbot Fallback)
# ============================================

# OpenAI API (Optional - Chatbot Fallback)
OPENAI_API_KEY=sk-abc123...your_actual_key_here
OPENAI_MODEL_PRIMARY=gpt-4o-mini
OPENAI_MODEL_FALLBACK=gpt-4o-mini

# ============================================
# OPTIONAL (Production - Firebase)
# ============================================

# Firebase Storage (Optional - for production)
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

**✅ Status:** [ ] Created

---

## ✅ Verification Steps

### 1. Check `.env` File Location
- [ ] File exists at: `C:\Users\datta\OneDrive\Desktop\gdg\.env`
- [ ] Contains at least `GEMINI_API_KEY=...`

### 2. Test Backend
```bash
cd backend
python -m uvicorn main:app --reload
```
- [ ] Server starts without errors
- [ ] No "API key not found" errors

### 3. Test Frontend
```bash
cd frontend
npm install
npm run dev
```
- [ ] Frontend starts on http://localhost:3000
- [ ] Can access dashboard

---

## 🚨 Common Issues

### Issue 1: "GEMINI_API_KEY not found"
**Fix:** 
- Check `.env` file is in project root (not `backend/.env`)
- Restart backend server

### Issue 2: "Google Cloud Vision API not working"
**Fix:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Verify JSON file exists
- Check service account has "Cloud Vision API User" role

### Issue 3: "Firebase not configured"
**Fix:**
- This is OK for local development
- System will use local storage instead
- Only needed for production deployment

---

## 📚 Full Documentation

- **Quick Start:** See `QUICK_START.md` (5 minutes)
- **Detailed Setup:** See `SETUP_GUIDE.md` (step-by-step with screenshots)
- **Google OCR Setup:** See `GOOGLE_OCR_SETUP.md`
- **Deployment:** See `DEPLOYMENT_GUIDE.md`

---

## 🎯 Summary

**Minimum (Required):**
1. ✅ Get Gemini API key
2. ✅ Create `.env` file with `GEMINI_API_KEY`

**Recommended:**
3. ✅ Get Google Cloud Vision API (better OCR)
4. ✅ Get OpenAI API (fallback)

**Production:**
5. ✅ Setup Firebase (if deploying)

**That's it!** The system will work with just Gemini API key. Everything else is optional.

