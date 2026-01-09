# DATABASE_URL Added to .env

## ✅ What Was Added

I've added a `DATABASE_URL` placeholder to your `.env` file.

**Location:** At the end of the file

**Content:**
```env
# Supabase PostgreSQL Database (Optional - uses SQLite if not set)
# DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

---

## 🔧 How to Use

### Option 1: Use SQLite (Current - Works Now)
**Do nothing!** The line is commented out, so backend will use SQLite automatically.

### Option 2: Use Supabase PostgreSQL
1. **Get your Supabase connection string:**
   - Go to Supabase Dashboard → Settings → Database
   - Copy the "URI" connection string
   - Replace `[YOUR-PASSWORD]` with your password

2. **Uncomment and update the line:**
   ```env
   DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```

3. **Save the file**

4. **Test connection:**
   ```powershell
   cd backend
   python setup_supabase.py
   ```

---

## 📋 Current .env Structure

Your `.env` file now has:
1. OpenAI API Key
2. Gemini API Key
3. Google Cloud Vision (commented)
4. Firebase Project ID
5. **DATABASE_URL (commented - ready for Supabase)**

---

## ✅ Status

- ✅ `.env` file updated
- ✅ DATABASE_URL placeholder added
- ✅ Currently using SQLite (works fine)
- ⏳ Ready for Supabase when you get connection string

---

**Next:** Get your Supabase connection string and uncomment the DATABASE_URL line!

