# Complete Supabase Setup Guide

## 📋 Overview

This guide will help you set up Supabase (PostgreSQL database + file storage) for your accreditation platform.

**Time needed:** 15-20 minutes

---

## Part 1: Create Supabase Account & Project

### Step 1: Sign Up
1. Go to https://supabase.com/
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### Step 2: Create Project
1. Click "New project"
2. Fill in:
   - **Name:** `accreditation-platform`
   - **Database Password:** Generate or create one (SAVE IT!)
   - **Region:** Choose closest to you
3. Click "Create new project"
4. Wait 2-3 minutes

### Step 3: Get Connection String
1. Go to: Settings → Database
2. Find "Connection string" section
3. Click "URI" tab
4. Copy the connection string
5. **Replace `[YOUR-PASSWORD]`** with your actual password

**Example:**
```
postgresql://postgres:MyPassword123!@db.abcdefghijk.supabase.co:5432/postgres
```

---

## Part 2: Set Up File Storage

### Step 1: Create Storage Bucket
1. In Supabase dashboard, click "Storage" (left sidebar)
2. Click "New bucket"
3. Name: `documents`
4. Toggle "Public bucket" to ON
5. Click "Create bucket"

**Done!** Your file storage is ready.

---

## Part 3: Configure Backend

### Step 1: Install PostgreSQL Driver
```bash
cd backend
pip install psycopg2-binary
```

### Step 2: Create .env File
1. Go to `backend` folder
2. Create file named `.env` (with the dot)
3. Add this line (use YOUR connection string):
   ```env
   DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```
4. Save the file

### Step 3: Test Connection
```bash
cd backend
python setup_supabase.py
```

This will check:
- ✅ PostgreSQL driver installed
- ✅ .env file exists
- ✅ Database connection works

### Step 4: Initialize Database Tables
```bash
python -c "from config.database import init_db; init_db(); print('Tables created!')"
```

---

## Part 4: Verify Setup

### Check Supabase Dashboard
1. Go to Supabase dashboard
2. Click "Table Editor" (left sidebar)
3. You should see all your tables:
   - batches
   - blocks
   - files
   - users
   - institutions
   - departments
   - etc.

### Test Backend
1. Start backend:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```
2. Check logs - should say "Using PostgreSQL database (Supabase)"

---

## What Changed?

✅ Backend now automatically:
- Uses PostgreSQL if `DATABASE_URL` is set (Supabase)
- Falls back to SQLite if not set (local development)
- All your code works the same - no changes needed!

---

## Troubleshooting

### "Module not found: psycopg2"
**Fix:**
```bash
pip install psycopg2-binary
```

### "Connection refused"
**Check:**
1. Is password correct? (no spaces, exact match)
2. Is connection string correct?
3. Is Supabase project active?

### "Can't create .env file"
**Fix:**
- Use Notepad
- Save As → "All Files"
- Name: `.env`

---

## Next Steps

After Supabase is set up:
1. ✅ Database ready (PostgreSQL)
2. ✅ File storage ready
3. ⏭️ Update file upload code to use Supabase Storage (optional)
4. ⏭️ Test with real data

---

## Quick Reference

**Connection String Format:**
```
postgresql://postgres:PASSWORD@db.PROJECT-ID.supabase.co:5432/postgres
```

**Storage Bucket:**
- Name: `documents`
- Public: Yes

**Environment Variable:**
```env
DATABASE_URL=your-connection-string-here
```

---

## Need Help?

1. Check `SUPABASE_SETUP_DETAILED.md` for step-by-step instructions
2. Run `python setup_supabase.py` to check your setup
3. Check Supabase dashboard for connection issues

**You're all set! 🚀**

