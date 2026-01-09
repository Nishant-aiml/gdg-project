# Testing & Setup Guide

## ✅ Test Results

### 1. Backend Health Endpoint
**Status:** Testing...

**How to test:**
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health"
```

**Expected response:**
```json
{"status": "healthy"}
```

---

### 2. Firebase Authentication
**Status:** ✅ **WORKING**

**Test Results:**
- Firebase Admin SDK: ✅ Initialized
- Project ID: ✅ Set (accreditation-platform)
- Token Verification: ✅ Ready

**How it works:**
1. Frontend: User signs in with Firebase (Email/Google)
2. Frontend: Gets Firebase ID token
3. Frontend: Sends token to backend `/api/auth/login`
4. Backend: Verifies token using Firebase Admin SDK
5. Backend: Returns user info and role

**Test Firebase:**
- Open: http://localhost:3000/login
- Try Google Sign-In or Email/Password
- Should work if backend is running

---

### 3. Supabase PostgreSQL Setup

**Current Status:** Not configured (using SQLite)

**To Set Up Supabase:**

#### Step 1: Create Supabase Account (5 min)
1. Go to https://supabase.com/
2. Sign up / Login
3. Click "New project"
4. Name: `accreditation-platform`
5. **Save the database password!**
6. Choose region closest to you
7. Click "Create new project"
8. Wait 2-3 minutes

#### Step 2: Get Connection String (2 min)
1. In Supabase dashboard: Settings → Database
2. Find "Connection string" section
3. Click "URI" tab
4. Copy the connection string
5. **Replace `[YOUR-PASSWORD]`** with your actual password

**Example:**
```
postgresql://postgres:MyPassword123!@db.abcdefghijk.supabase.co:5432/postgres
```

#### Step 3: Install PostgreSQL Driver (1 min)
```powershell
cd backend
pip install psycopg2-binary
```

#### Step 4: Add to Environment (2 min)
1. Open root `.env` file (in project root, not backend folder)
2. Add this line (use YOUR connection string):
```env
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
```
3. Save the file

#### Step 5: Test Connection (1 min)
```powershell
cd backend
python -c "from config.database import DB_TYPE, engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT 1')); print(f'Database: {DB_TYPE}'); print('Connection: SUCCESS'); conn.close()"
```

#### Step 6: Initialize Database (30 sec)
```powershell
cd backend
python -c "from config.database import init_db; init_db(); print('✅ Database tables created!')"
```

---

## 🎯 Quick Test Commands

### Test Backend Health:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health"
```

### Test Firebase:
```powershell
cd backend
python -c "from services.firebase_auth import initialize_firebase_admin; app = initialize_firebase_admin(); print('Firebase:', 'OK' if app else 'FAILED')"
```

### Test Database:
```powershell
cd backend
python -c "from config.database import DB_TYPE; print(f'Database Type: {DB_TYPE}')"
```

---

## 📋 Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend Health** | ⏳ Testing | Start backend first |
| **Firebase Auth** | ✅ Working | Admin SDK initialized |
| **Supabase Setup** | ⏳ Pending | Follow steps above |

---

## 🚀 Next Steps

1. ✅ **Firebase:** Already working
2. ⏳ **Backend:** Start server and test health
3. ⏳ **Supabase:** Follow setup steps above

---

**See detailed guides:**
- `SUPABASE_SETUP_DETAILED.md` - Complete setup guide
- `QUICK_START_SUPABASE.md` - 5-minute quick start

