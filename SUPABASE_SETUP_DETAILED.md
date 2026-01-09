# Supabase Setup Guide - Step by Step (Like a Kid)

## What is Supabase?
Supabase is like a free database in the cloud. It gives you:
- PostgreSQL database (very reliable)
- File storage (for your PDFs)
- Free to start
- Easy to use

---

## Part 1: Create Supabase Account (5 minutes)

### Step 1: Go to Supabase Website
1. Open your web browser
2. Type in address bar: `https://supabase.com/`
3. Press Enter
4. You'll see Supabase homepage

### Step 2: Sign Up
1. Click "Start your project" button (big green button)
2. You'll see sign-up options:
   - **Option A:** Sign up with GitHub (easiest - if you have GitHub account)
   - **Option B:** Sign up with email
3. Choose one and sign up
4. If using email, check your email and verify it

### Step 3: Create Organization (if needed)
1. After signing up, you might be asked to create an organization
2. Organization name: `My Projects` (or any name)
3. Click "Create organization"

**✅ Part 1 Complete!** You now have a Supabase account.

---

## Part 2: Create Supabase Project (5 minutes)

### Step 1: Create New Project
1. After logging in, you'll see your dashboard
2. Click "New project" button (top right, green button)
3. A form will appear

### Step 2: Fill Project Details
1. **Organization:** Select your organization (should be selected already)
2. **Name:** Type `accreditation-platform` (or any name you like)
3. **Database Password:** 
   - Click "Generate a password" OR create your own
   - **IMPORTANT:** Save this password! Write it down somewhere safe
   - You'll need it later
   - Example: `MySecurePassword123!`
4. **Region:** 
   - Click the dropdown
   - Choose the region closest to you
   - Examples: "US East (North Virginia)", "Europe West (London)", etc.
   - This affects speed - choose closest to your users

### Step 3: Create Project
1. Check the pricing plan (should show "Free" tier)
2. Click "Create new project" button (green button at bottom)
3. **Wait 2-3 minutes** - Supabase is setting up your database
4. You'll see a progress bar
5. When it says "Project is ready", you're done!

**✅ Part 2 Complete!** You now have a Supabase project with PostgreSQL database.

---

## Part 3: Get Database Connection String (3 minutes)

### Step 1: Go to Project Settings
1. In your Supabase dashboard, look at the left sidebar
2. Find "Settings" (gear icon ⚙️ at the bottom)
3. Click on "Settings"
4. A menu will appear
5. Click "Database" (first option)

### Step 2: Find Connection String
1. Scroll down the page
2. Find section called "Connection string"
3. You'll see tabs: "URI", "JDBC", "Golang", etc.
4. Click on "URI" tab (should be selected already)
5. You'll see a connection string that looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. **Copy this entire string** (select all and Ctrl+C)
7. **IMPORTANT:** Replace `[YOUR-PASSWORD]` with the password you saved earlier
   - Example: If password is `MySecurePassword123!`
   - Replace `[YOUR-PASSWORD]` with `MySecurePassword123!`
   - Final string: `postgresql://postgres:MySecurePassword123!@db.xxxxx.supabase.co:5432/postgres`
   

**✅ Part 3 Complete!** You have your database connection string.

---

## Part 4: Set Up File Storage (5 minutes)

### Step 1: Go to Storage
1. In left sidebar, find "Storage" (folder icon 📁)
2. Click on "Storage"

### Step 2: Create Storage Bucket
1. Click "New bucket" button (top right)
2. A popup will appear
3. **Bucket name:** Type `documents` (exactly like this)
4. **Public bucket:** 
   - Toggle this ON (make it public)
   - This allows your app to access files
5. Click "Create bucket" button
6. You'll see your bucket created

### Step 3: Set Up Bucket Policies (Optional - for security)
1. Click on your "documents" bucket
2. Go to "Policies" tab
3. For now, you can skip this (we'll use public bucket)
4. For production, you'll want to add proper policies

**✅ Part 4 Complete!** You have file storage set up.

---

## Part 5: Add Connection to Your Backend (10 minutes)

### Step 1: Install PostgreSQL Driver
1. Open Command Prompt or PowerShell
2. Navigate to backend folder:
   ```bash
   cd C:\Users\datta\OneDrive\Desktop\gdg\backend
   ```
3. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```
4. Wait for installation to complete

### Step 2: Create .env File in Backend
1. Go to your backend folder in File Explorer
2. Look for a file named `.env` (if it exists, open it; if not, create it)
3. If creating new:
   - Right-click → New → Text Document
   - Name it: `.env` (with the dot at the start)
   - Make sure it's not `.env.txt`

### Step 3: Add Database URL
1. Open `.env` file in text editor
2. Add this line (replace with YOUR connection string):
   ```env
   DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```
3. **Replace `YOUR-PASSWORD`** with your actual password
4. **Replace `xxxxx`** with your actual Supabase project ID
5. Example:
   ```env
   DATABASE_URL=postgresql://postgres:MySecurePassword123!@db.abcdefghijk.supabase.co:5432/postgres
   ```
6. Save the file (Ctrl+S)

### Step 4: Update Database Configuration
1. Open `backend/config/database.py` in your code editor
2. We need to modify it to use PostgreSQL instead of SQLite
3. I'll show you the changes in the next section

**✅ Part 5 Complete!** Backend is configured to use Supabase.

---

## Part 6: Update Backend Code (I'll do this for you)

I'll update your backend code to use PostgreSQL. Just follow along!

---

## Part 7: Test the Connection (2 minutes)

### Step 1: Test Database Connection
1. Open Command Prompt
2. Navigate to backend:
   ```bash
   cd C:\Users\datta\OneDrive\Desktop\gdg\backend
   ```
3. Test connection:
   ```bash
   python -c "from config.database import engine; print('Database connected!' if engine else 'Failed')"
   ```

### Step 2: Initialize Database Tables
1. Run this command:
   ```bash
   python -c "from config.database import init_db; init_db(); print('Database initialized!')"
   ```

**✅ Part 7 Complete!** Your database is connected and ready!

---

## Troubleshooting

### Problem: Can't connect to database
**Check:**
1. Is password correct? (no spaces, exact match)
2. Is connection string correct? (copy-paste from Supabase)
3. Is `.env` file in the `backend` folder?
4. Did you install `psycopg2-binary`?

### Problem: "Module not found: psycopg2"
**Solution:**
```bash
pip install psycopg2-binary
```

### Problem: "Connection refused"
**Check:**
1. Is your Supabase project active? (check Supabase dashboard)
2. Is the connection string correct?
3. Try copying connection string again from Supabase

### Problem: Can't create .env file
**Solution:**
- Use Notepad
- Save As → Choose "All Files" type
- Name it exactly `.env`

---

## What's Next?

After Supabase is set up:
1. ✅ Database is ready (PostgreSQL)
2. ✅ File storage is ready
3. ⏭️ Update backend code (I'll do this next)
4. ⏭️ Test everything works

---

## Summary Checklist

- [ ] Created Supabase account
- [ ] Created new project
- [ ] Saved database password
- [ ] Got connection string
- [ ] Created storage bucket
- [ ] Installed psycopg2-binary
- [ ] Created `.env` file in backend
- [ ] Added DATABASE_URL to `.env`
- [ ] Tested connection

**You're ready for the next step! 🎉**

