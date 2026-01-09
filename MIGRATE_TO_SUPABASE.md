# Migration Guide: SQLite to Supabase PostgreSQL

## Quick Migration Steps

### Step 1: Install PostgreSQL Driver
```bash
cd backend
pip install psycopg2-binary
```

### Step 2: Get Supabase Connection String
1. Go to Supabase Dashboard
2. Settings → Database
3. Copy "Connection string" (URI format)
4. Replace `[YOUR-PASSWORD]` with your actual password

### Step 3: Add to .env File
Create or update `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

### Step 4: Test Connection
```bash
cd backend
python -c "from config.database import engine; print('Connected!' if engine else 'Failed')"
```

### Step 5: Initialize Tables
```bash
python -c "from config.database import init_db; init_db(); print('Tables created!')"
```

## What Changed?

The backend now:
- ✅ Automatically detects PostgreSQL if `DATABASE_URL` is set
- ✅ Falls back to SQLite if `DATABASE_URL` is not set (for local dev)
- ✅ All your existing code works the same way
- ✅ No code changes needed in your application

## Verify It Works

1. Check Supabase Dashboard → Table Editor
2. You should see all your tables created:
   - batches
   - blocks
   - files
   - users
   - institutions
   - departments
   - etc.

## Data Migration (Optional)

If you have existing SQLite data you want to migrate:

1. Export SQLite data:
   ```bash
   sqlite3 storage/db/temp_batches.db .dump > backup.sql
   ```

2. Convert to PostgreSQL format (manual editing or use a tool)

3. Import to Supabase (via Supabase SQL Editor)

**Note:** For fresh setup, you don't need to migrate - just start fresh!

