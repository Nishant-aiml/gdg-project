# Backend .env File Template

## Location
Create this file: `backend/.env`

## Content Template

### For Local Development (SQLite - Current)
```env
# Leave DATABASE_URL empty or commented to use SQLite
# DATABASE_URL=

# API Configuration
API_BASE=http://127.0.0.1:8000
```

### For Production (Supabase PostgreSQL - After Setup)
```env
# Supabase PostgreSQL Connection
# Get this from Supabase Dashboard → Settings → Database → Connection string
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres

# API Configuration
API_BASE=http://127.0.0.1:8000

# Optional: Other configurations
# OPENAI_API_KEY=your-key-here (if needed)
# GEMINI_API_KEY=your-key-here (if needed)
```

## How to Create

1. **Go to backend folder:**
   ```
   C:\Users\datta\OneDrive\Desktop\gdg\backend
   ```

2. **Create .env file:**
   - Open Notepad
   - Paste the template above
   - Save As → Location: `backend` folder
   - Name: `.env`
   - Type: "All Files"

3. **Fill in values:**
   - For now (local dev): Leave DATABASE_URL empty
   - After Supabase: Add your connection string

## Current Status

**Right now (before Supabase):**
- ✅ Backend uses SQLite (no .env needed)
- ✅ Works fine for development

**After Supabase setup:**
- ⏭️ Create `backend/.env`
- ⏭️ Add DATABASE_URL
- ✅ Backend will use PostgreSQL

## Important Notes

- **Frontend `.env.local`** = Firebase config (✅ you have this)
- **Backend `.env`** = Database config (⏭️ create after Supabase)
- **No root `.env`** = Not needed

## When to Create backend/.env

**Option 1: Now (for local dev)**
- Create empty `.env` or with just `API_BASE`
- Backend will use SQLite (works fine)

**Option 2: After Supabase (recommended)**
- Set up Supabase first
- Get connection string
- Create `.env` with DATABASE_URL
- Backend will use PostgreSQL

**Both options work!** Choose what's easier for you.

