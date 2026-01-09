# Firebase Next Steps - After Enabling Authentication

## ✅ What You've Done
- ✅ Enabled Email/Password authentication
- ✅ Enabled Google Sign-In
- ✅ Set support email: dattanishant2@gmail.com

## 📋 Next Steps (5 minutes)

### Step 1: Get Firebase Configuration (2 min)

1. **Go to Project Settings**
   - In Firebase Console, look at the left sidebar
   - At the bottom, find the gear icon ⚙️
   - Click on the gear icon
   - Click "Project settings" from the menu

2. **Add Web App (if not done)**
   - Scroll down to "Your apps" section
   - If you see a web app already, skip to Step 3
   - If not, click the web icon `</>` (looks like `<>`)
   - App nickname: `accreditation-frontend`
   - **DO NOT** check "Also set up Firebase Hosting"
   - Click "Register app"

3. **Copy Configuration**
   - You'll see code that looks like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "project-831601787756.firebaseapp.com",
     projectId: "project-831601787756",
     storageBucket: "project-831601787756.appspot.com",
     messagingSenderId: "831601787756",
     appId: "1:831601787756:web:abc123..."
   };
   ```
   - **Copy all of this** (select all and Ctrl+C)
   - Keep it open - you'll need it next

### Step 2: Add Configuration to Frontend (2 min)

1. **Go to Frontend Folder**
   - Open File Explorer
   - Navigate to: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`

2. **Create .env.local File**
   - Right-click in the folder → New → Text Document
   - Name it: `.env.local` (with the dot at the start)
   - If Windows asks about changing extension, click "Yes"
   - If it shows as `.env.local.txt`, rename it to remove `.txt`

   **Alternative method:**
   - Open Notepad
   - Go to File → Save As
   - Navigate to `frontend` folder
   - File name: `.env.local`
   - Save as type: "All Files" (important!)
   - Click Save

3. **Add Firebase Variables**
   - Open `.env.local` in a text editor
   - Copy and paste this template:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
   NEXT_PUBLIC_FIREBASE_APP_ID=
   ```

4. **Fill in Your Values**
   - From the config you copied, fill in each value:
   - `NEXT_PUBLIC_FIREBASE_API_KEY=` → value from `apiKey: "..."` (remove quotes)
   - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=` → value from `authDomain: "..."` (remove quotes)
   - `NEXT_PUBLIC_FIREBASE_PROJECT_ID=` → value from `projectId: "..."` (remove quotes)
   - `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=` → value from `storageBucket: "..."` (remove quotes)
   - `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=` → value from `messagingSenderId: "..."` (remove quotes)
   - `NEXT_PUBLIC_FIREBASE_APP_ID=` → value from `appId: "..."` (remove quotes)

5. **Example (based on your project ID):**
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAbc123xyz789
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=project-831601787756.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=project-831601787756
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=project-831601787756.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=831601787756
   NEXT_PUBLIC_FIREBASE_APP_ID=1:831601787756:web:abc123def456
   ```

6. **Save the File** (Ctrl+S)

### Step 3: Add Localhost to Authorized Domains (1 min)

1. **Go Back to Firebase Console**
   - In left sidebar, click "Authentication"
   - Click "Sign-in method" tab
   - Scroll down to "Authorized domains" section

2. **Add Localhost**
   - Click "Add domain" button
   - Type: `localhost` (exactly like this, no http://)
   - Click "Add"
   - You should see `localhost` in the list

### Step 4: Test Login (1 min)

1. **Start Frontend Server**
   - Open Command Prompt or PowerShell
   - Navigate to frontend:
     ```bash
     cd C:\Users\datta\OneDrive\Desktop\gdg\frontend
     ```
   - Start server:
     ```bash
     npm run dev
     ```
   - Wait for "Ready" message

2. **Test in Browser**
   - Open browser
   - Go to: http://localhost:3000
   - Try to login
   - You should see:
     - Google sign-in button (for Google login)
     - Email/password form (for email login)
   - Try both methods!

## ✅ Verification Checklist

- [ ] Firebase config copied from console
- [ ] `.env.local` file created in `frontend` folder
- [ ] All 6 environment variables added
- [ ] `localhost` added to authorized domains
- [ ] Frontend server started
- [ ] Login tested successfully

## 🎉 Done!

Your Firebase authentication is now set up and ready to use!

**Next:** Set up Supabase for database (see `SUPABASE_SETUP_DETAILED.md`)

