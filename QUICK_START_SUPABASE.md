# Quick Start: Supabase Setup (5 Minutes)

## Step 1: Create Supabase Project (2 min)
1. Go to https://supabase.com/
2. Sign up / Login
3. Click "New project"
4. Name: `accreditation-platform`
5. **Save the password!** (you'll need it)
6. Choose region closest to you
7. Click "Create new project"
8. Wait 2 minutes

## Step 2: Get Connection String (1 min)
1. In Supabase: Settings → Database
2. Find "Connection string" section
3. Click "URI" tab
4. Copy the connection string
5. **Replace `[YOUR-PASSWORD]`** with your saved password
   - Example: `postgresql://postgres:MyPassword123!@db.xxxxx.supabase.co:5432/postgres`

## Step 3: Install PostgreSQL Driver (1 min)
```bash
cd backend
pip install psycopg2-binary
```

## Step 4: Add to Backend (1 min)
1. Create `backend/.env` file
2. Add this line (use YOUR connection string):
   ```env
   DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```
3. Save the file

## Step 5: Test (30 sec)
```bash
cd backend
python -c "from config.database import init_db; init_db(); print('✅ Database ready!')"
```

## Done! 🎉

Your backend now uses Supabase PostgreSQL!

**Next:** Set up file storage (see SUPABASE_SETUP_DETAILED.md Part 4)

