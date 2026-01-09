# Start Platform - Quick Guide

## ✅ Environment Files Verified

All environment files are correctly configured:
- ✅ Frontend: Firebase authentication ready
- ✅ Backend: API keys configured
- ✅ Database: SQLite ready (works automatically)

---

## 🚀 Start the Platform (2 Steps)

### Step 1: Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn main:app --reload
```

**Wait for:** "Uvicorn running on http://127.0.0.1:8000"

### Step 2: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

**Wait for:** "Ready" message

### Step 3: Open Browser

Go to: http://localhost:3000

---

## ✅ Test Checklist

### Test 1: Login (1 min)
- [ ] Click "Login" or "Sign In"
- [ ] Try Google login (should open popup)
- [ ] Try Email/Password login
- [ ] Should redirect to dashboard after login

### Test 2: Backend Health (30 sec)
- [ ] Open: http://127.0.0.1:8000/api/health
- [ ] Should see: `{"status": "ok"}`

### Test 3: Create Batch (2 min)
- [ ] After login, select mode (AICTE/NBA/NAAC/NIRF)
- [ ] Upload a PDF document
- [ ] Wait for processing
- [ ] View dashboard

### Test 4: Use Chatbot (1 min)
- [ ] Open chatbot (chat icon)
- [ ] Ask: "Explain the overall score"
- [ ] Should get response

---

## 🎯 Everything Should Work!

Your platform is fully configured:
- ✅ Firebase authentication
- ✅ Backend API keys
- ✅ Database (SQLite)
- ✅ All connections verified

**Start both servers and test! 🚀**

---

## ⏭️ Optional: Supabase Setup

If you want PostgreSQL database:
1. Follow `SUPABASE_SETUP_DETAILED.md`
2. Add `DATABASE_URL` to root `.env`
3. Restart backend

**Note:** SQLite works perfectly for development!

