# Next Steps After Supabase Setup

## ✅ What You've Done

1. ✅ Created Supabase account
2. ✅ Created project
3. ✅ Got connection string
4. ✅ Added DATABASE_URL to .env

---

## 🎯 Next Steps

### Step 1: Verify Connection (1 minute)

Test if your Supabase connection works:

```powershell
cd backend
python setup_supabase.py
```

**Expected output:**
```
[OK] psycopg2-binary is installed
[OK] DATABASE_URL found in .env file
[OK] Database connection successful!
```

**If it fails:**
- Check your password in DATABASE_URL (no spaces)
- Make sure Supabase project is active
- Verify connection string format

---

### Step 2: Initialize Database Tables (30 seconds)

Create all the tables in your Supabase database:

```powershell
cd backend
python -c "from config.database import init_db; init_db(); print('✅ Tables created!')"
```

**This creates:**
- Users table
- Institutions table
- Departments table
- Batches table
- Documents table
- And all other required tables

---

### Step 3: Verify Tables in Supabase (1 minute)

1. **Go to Supabase Dashboard**
2. **Click:** "Table Editor" (left sidebar)
3. **You should see:**
   - `users`
   - `institutions`
   - `departments`
   - `batches`
   - `documents`
   - And other tables

**If tables are there:** ✅ Database is ready!

---

### Step 4: Test Backend with Supabase (2 minutes)

1. **Start backend:**
   ```powershell
   cd backend
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Check startup message:**
   - Should say: "Using PostgreSQL database (Supabase)"
   - NOT: "Using SQLite database"

3. **Test health endpoint:**
   ```powershell
   Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health"
   ```

**Expected:** `{"status": "healthy"}`

---

### Step 5: Test Full Flow (5 minutes)

1. **Start frontend:**
   ```powershell
   cd frontend
   npm run dev
   ```

2. **Open:** http://localhost:3000

3. **Test login:**
   - Try Google Sign-In
   - Or Email/Password sign up
   - Should work!

4. **Create a batch:**
   - Select a mode (AICTE, NBA, etc.)
   - Upload documents
   - Process them
   - Check dashboard

5. **Verify data in Supabase:**
   - Go to Supabase Dashboard → Table Editor
   - Check `batches` table
   - Check `documents` table
   - Your data should be there!

---

## 📋 Quick Checklist

- [ ] Connection test passed (`python setup_supabase.py`)
- [ ] Database tables initialized (`init_db()`)
- [ ] Tables visible in Supabase dashboard
- [ ] Backend starts with PostgreSQL (not SQLite)
- [ ] Health endpoint works
- [ ] Frontend can connect to backend
- [ ] Login works
- [ ] Data saves to Supabase

---

## 🎉 You're Done!

Once all steps are complete:
- ✅ Supabase PostgreSQL is working
- ✅ Data persists in cloud database
- ✅ Platform is fully functional
- ✅ Ready for production use

---

## 🆘 Troubleshooting

### Connection fails:
- Check password in DATABASE_URL (no spaces, special chars URL-encoded)
- Verify Supabase project is active
- Check connection string format

### Tables not created:
- Make sure you ran `init_db()`
- Check for errors in terminal
- Verify DATABASE_URL is correct

### Backend still uses SQLite:
- Check `.env` file has DATABASE_URL (not commented)
- Restart backend server
- Check startup logs

---

**See detailed guides:**
- `SUPABASE_SETUP_DETAILED.md` - Complete setup guide
- `TEST_RESULTS_AND_SETUP.md` - Testing guide

