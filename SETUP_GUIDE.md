# Complete Setup Guide - Step by Step

## Part 1: Firebase Authentication Setup (For Login Only)

### Step 1: Create Firebase Project

1. **Go to Firebase Console**
   - Open your browser
   - Go to: https://console.firebase.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click "Add project" or "Create a project"
   - Enter project name: `accreditation-platform` (or any name you like)
   - Click "Continue"
   - **Disable Google Analytics** (optional - you can skip it)
   - Click "Create project"
   - Wait for project to be created (30 seconds)
   - Click "Continue"

### Step 2: Enable Authentication

1. **Go to Authentication**
   - In the left sidebar, click "Authentication"
   - Click "Get started"

2. **Enable Sign-in Methods**
   - Click on "Sign-in method" tab
   - Click on "Google" provider
   - Toggle "Enable" to ON
   - Enter your project support email (your email)
   - Click "Save"

3. **Add Authorized Domains** (for local testing)
   - Still in Authentication settings
   - Scroll down to "Authorized domains"
   - Click "Add domain"
   - Add: `localhost`
   - Click "Add"

### Step 3: Get Firebase Configuration

1. **Go to Project Settings**
   - Click the gear icon (⚙️) next to "Project Overview" in left sidebar
   - Click "Project settings"

2. **Get Web App Configuration**
   - Scroll down to "Your apps" section
   - Click the web icon (</>) to add a web app
   - Enter app nickname: `accreditation-frontend`
   - **DO NOT** check "Also set up Firebase Hosting"
   - Click "Register app"

3. **Copy Configuration**
   - You'll see a code block with `firebaseConfig`
   - It looks like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```
   - **Copy this entire config** - you'll need it in Step 4

### Step 4: Add Configuration to Frontend

1. **Create Environment File**
   - Go to your project folder: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`
   - Create a new file named: `.env.local`
   - Open it in a text editor

2. **Add Firebase Config**
   - Paste this template and fill in your values:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key-here
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
   NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123
   ```

3. **Fill in Your Values**
   - Replace each value with what you copied from Firebase Console
   - Example:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAbc123...
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=accreditation-platform.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=accreditation-platform
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=accreditation-platform.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=987654321
   NEXT_PUBLIC_FIREBASE_APP_ID=1:987654321:web:xyz789
   ```

4. **Save the File**
   - Save `.env.local` in the `frontend` folder
   - Make sure it's exactly `.env.local` (not `.env.local.txt`)

### Step 5: Test Firebase Connection

1. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test Login**
   - Open browser: http://localhost:3000
   - Try to login
   - You should see Google sign-in popup
   - After login, you should be authenticated

### Step 6: Set Up User Roles (Optional - for testing)

1. **Go to Firestore Database** (if you want to store user roles)
   - In Firebase Console, click "Firestore Database" in left sidebar
   - Click "Create database"
   - Choose "Start in test mode" (for development)
   - Select a location (choose closest to you)
   - Click "Enable"

2. **Create Users Collection** (optional)
   - Click "Start collection"
   - Collection ID: `users`
   - Document ID: (use your user UID from Authentication)
   - Add fields:
     - `role` (string): `department` or `institution`
     - `department_id` (string): your department ID (if department user)
   - Click "Save"

**Note:** For production, you'll want to set up proper security rules, but for now test mode works.

---

## Part 2: Alternative Storage & Database Options (Not MongoDB)

### Option 1: PostgreSQL + Supabase (Recommended - Easiest)

**Why Supabase?**
- Free tier available
- PostgreSQL database (very reliable)
- Built-in file storage
- Easy to set up
- Good documentation

#### Setup Steps:

1. **Create Supabase Account**
   - Go to: https://supabase.com/
   - Click "Start your project"
   - Sign up with GitHub or email

2. **Create New Project**
   - Click "New project"
   - Organization: Create new (or use existing)
   - Project name: `accreditation-platform`
   - Database password: Create a strong password (save it!)
   - Region: Choose closest to you
   - Click "Create new project"
   - Wait 2 minutes for setup

3. **Get Connection String**
   - Go to Project Settings (gear icon)
   - Click "Database" in left sidebar
   - Find "Connection string"
   - Copy the "URI" connection string
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`

4. **Update Backend Configuration**
   - In your project: `backend/.env`
   - Add:
   ```env
   DATABASE_URL=postgresql://postgres:your-password@db.xxx.supabase.co:5432/postgres
   ```

5. **Update Database Code**
   - The backend already uses SQLAlchemy
   - Just change the connection string
   - PostgreSQL works with SQLAlchemy automatically

6. **File Storage Setup**
   - In Supabase, go to "Storage"
   - Create a bucket: `documents`
   - Set it to "Public" (or "Private" with proper policies)
   - Use Supabase Storage API for file uploads

#### Pros:
- ✅ Free tier (500MB database, 1GB storage)
- ✅ PostgreSQL (very reliable)
- ✅ Built-in file storage
- ✅ Easy to use
- ✅ Good for production

#### Cons:
- ⚠️ Free tier has limits
- ⚠️ Need to migrate from SQLite

---

### Option 2: PostgreSQL + Railway (Good for Production)

**Why Railway?**
- Easy deployment
- PostgreSQL included
- File storage via Railway volumes or S3
- Pay-as-you-go pricing

#### Setup Steps:

1. **Create Railway Account**
   - Go to: https://railway.app/
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or "Empty Project")

3. **Add PostgreSQL Database**
   - Click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Wait for database to be created

4. **Get Connection String**
   - Click on PostgreSQL service
   - Go to "Variables" tab
   - Copy `DATABASE_URL`
   - It looks like: `postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

5. **Add to Backend**
   - Add to `backend/.env`:
   ```env
   DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```

6. **File Storage**
   - Option A: Use Railway volumes (for files)
   - Option B: Use AWS S3 (better for production)
   - Option C: Use Cloudflare R2 (cheaper alternative to S3)

#### Pros:
- ✅ Easy deployment
- ✅ PostgreSQL included
- ✅ Good for production
- ✅ Automatic backups

#### Cons:
- ⚠️ Costs money (but reasonable)
- ⚠️ Need to set up file storage separately

---

### Option 3: PostgreSQL + Neon (Serverless PostgreSQL)

**Why Neon?**
- Serverless PostgreSQL
- Free tier available
- Auto-scaling
- Branching (like Git for databases)

#### Setup Steps:

1. **Create Neon Account**
   - Go to: https://neon.tech/
   - Sign up with GitHub or email

2. **Create Project**
   - Click "Create a project"
   - Project name: `accreditation-platform`
   - Region: Choose closest
   - PostgreSQL version: 15 or 16
   - Click "Create project"

3. **Get Connection String**
   - After project creation, you'll see connection string
   - Copy it
   - Format: `postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb`

4. **Add to Backend**
   - Add to `backend/.env`:
   ```env
   DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb
   ```

5. **File Storage**
   - Use AWS S3 or Cloudflare R2 for file storage

#### Pros:
- ✅ Free tier (0.5GB storage)
- ✅ Serverless (auto-scales)
- ✅ Branching feature
- ✅ Good performance

#### Cons:
- ⚠️ Free tier has limits
- ⚠️ Need separate file storage

---

### Option 4: SQLite + Cloudflare R2 (Simple & Cheap)

**Why This Combo?**
- SQLite is simple (already using it)
- Cloudflare R2 is cheap storage
- Good for small to medium apps

#### Setup Steps:

1. **Keep SQLite** (no changes needed)
   - Your backend already uses SQLite
   - Works great for development and small deployments

2. **Set Up Cloudflare R2 for File Storage**
   - Go to: https://dash.cloudflare.com/
   - Sign up/login
   - Go to "R2" in left sidebar
   - Click "Create bucket"
   - Bucket name: `accreditation-documents`
   - Click "Create bucket"

3. **Get R2 Credentials**
   - Go to "Manage R2 API Tokens"
   - Click "Create API token"
   - Permissions: "Object Read & Write"
   - Click "Create API token"
   - **Save the credentials** (you'll see them only once)

4. **Add to Backend**
   - Install: `pip install boto3`
   - Add to `backend/.env`:
   ```env
   R2_ACCOUNT_ID=your-account-id
   R2_ACCESS_KEY_ID=your-access-key
   R2_SECRET_ACCESS_KEY=your-secret-key
   R2_BUCKET_NAME=accreditation-documents
   R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
   ```

5. **Update File Upload Code**
   - Modify backend to use R2 instead of local storage
   - Use boto3 to upload files to R2

#### Pros:
- ✅ SQLite is simple (no setup)
- ✅ R2 is very cheap ($0.015/GB/month)
- ✅ No egress fees
- ✅ Good for small apps

#### Cons:
- ⚠️ SQLite has concurrency limits
- ⚠️ Not ideal for high-traffic apps
- ⚠️ Need to migrate to PostgreSQL for production

---

## Recommended Setup for Production

### Best Combination:
1. **Authentication:** Firebase (as you're doing)
2. **Database:** PostgreSQL on Supabase or Neon
3. **File Storage:** Cloudflare R2 or AWS S3

### Why This Combo?
- ✅ Firebase: Free authentication, easy to use
- ✅ PostgreSQL: Reliable, scalable database
- ✅ R2/S3: Cheap, reliable file storage
- ✅ All have free tiers to start
- ✅ Easy to scale when needed

---

## Quick Start Checklist

### Firebase Setup:
- [ ] Create Firebase project
- [ ] Enable Google authentication
- [ ] Get Firebase config
- [ ] Add to `frontend/.env.local`
- [ ] Test login

### Database Setup (Choose One):
- [ ] **Option A:** Supabase PostgreSQL
- [ ] **Option B:** Railway PostgreSQL
- [ ] **Option C:** Neon PostgreSQL
- [ ] **Option D:** Keep SQLite + add R2

### File Storage Setup:
- [ ] Set up Cloudflare R2 (recommended)
- [ ] OR set up AWS S3
- [ ] Add credentials to `backend/.env`
- [ ] Update file upload code

---

## Need Help?

If you get stuck at any step:
1. Check the error message
2. Make sure all environment variables are set
3. Verify credentials are correct
4. Check that services are enabled in Firebase/Supabase/etc.

Good luck! 🚀
