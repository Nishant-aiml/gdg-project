# Create Root .env File - Simple Steps

## 📍 Location

Create this file in the **project root** (same folder as `frontend` and `backend`):

```
C:\Users\datta\OneDrive\Desktop\gdg\.env
```

**NOT here:**
- ❌ `backend/.env` (wrong location)
- ❌ `frontend/.env` (wrong location)

## 📝 What to Put in It

### Option 1: For Now (Before Supabase)
Create an empty file or add:
```env
# Backend will use SQLite automatically if DATABASE_URL is not set
API_BASE=http://127.0.0.1:8000
```

### Option 2: After Supabase Setup
```env
# Supabase PostgreSQL Connection
# Get this from Supabase Dashboard → Settings → Database
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres

# API Configuration
API_BASE=http://127.0.0.1:8000
```

## 🛠️ How to Create

### Method 1: Using Notepad

1. **Open Notepad**
2. **Paste the content** (from Option 1 or 2 above)
3. **Save As:**
   - Navigate to: `C:\Users\datta\OneDrive\Desktop\gdg`
   - File name: `.env` (with the dot!)
   - Save as type: "All Files"
   - Click Save

### Method 2: Using File Explorer

1. **Go to project root:**
   ```
   C:\Users\datta\OneDrive\Desktop\gdg
   ```

2. **Create new file:**
   - Right-click → New → Text Document
   - Name: `.env`
   - Open with Notepad
   - Paste content
   - Save

## ✅ Verify Location

The file should be here:
```
C:\Users\datta\OneDrive\Desktop\gdg\.env
```

You should see it next to:
- `frontend` folder
- `backend` folder
- `README.md` file
- etc.

## 🎯 When to Create

**Right now:** 
- Create empty `.env` or with just `API_BASE`
- Backend will work with SQLite

**After Supabase:**
- Update `.env` with `DATABASE_URL`
- Backend will use PostgreSQL

## 📋 Quick Checklist

- [ ] File created in root folder (not in backend or frontend)
- [ ] Named exactly `.env` (with the dot)
- [ ] Contains at least `API_BASE` (or `DATABASE_URL` after Supabase)

## That's It!

Simple: One file in root folder for backend config! 🎉

