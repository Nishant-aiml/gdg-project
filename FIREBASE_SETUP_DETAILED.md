# Firebase Authentication Setup - Detailed Step-by-Step Guide

## Prerequisites
- A Google account
- Your project folder open
- A text editor (VS Code, Notepad++, etc.)

---

## Step 1: Create Firebase Project (5 minutes)

### 1.1 Go to Firebase Console
1. Open your web browser (Chrome, Firefox, Edge - any browser works)
2. Type in address bar: `https://console.firebase.google.com/`
3. Press Enter
4. You'll see Firebase homepage

### 1.2 Sign In
1. Click "Sign in" button (top right)
2. Use your Google account to sign in
3. If you don't have Google account, create one first at gmail.com

### 1.3 Create New Project
1. Click "Add project" button (big button in center, or top right)
2. A popup will appear asking for project name
3. Type: `accreditation-platform` (or any name you like)
4. Click "Continue" button
5. **Google Analytics screen appears:**
   - You can disable it (toggle OFF) - not needed for now
   - OR keep it enabled if you want analytics
   - Click "Continue"
6. Wait 30-60 seconds for project to be created
7. When you see "Your new project is ready", click "Continue"

**✅ Step 1 Complete!** You now have a Firebase project.

---

## Step 2: Enable Authentication (3 minutes)

### 2.1 Open Authentication
1. Look at the left sidebar menu
2. Find "Authentication" (it has a key icon 🔑)
3. Click on "Authentication"
4. You'll see a page saying "Get started"
5. Click the "Get started" button

### 2.2 Enable Google Sign-In
1. You'll see a page with tabs: "Users", "Sign-in method"
2. Click on "Sign-in method" tab (at the top)
3. You'll see a list of sign-in providers
4. Find "Google" in the list
5. Click on "Google" (the row, not just the toggle)
6. A popup will appear
7. **Toggle the "Enable" switch to ON** (top of popup)
8. **Project support email:** Enter your email address
9. Click "Save" button (bottom right)
10. You'll see "Provider enabled" message

**✅ Step 2 Complete!** Google authentication is now enabled.

---

## Step 3: Add Localhost to Authorized Domains (2 minutes)

### 3.1 Go to Authorized Domains
1. Still in "Authentication" page
2. Still on "Sign-in method" tab
3. Scroll down to bottom of the page
4. Find section called "Authorized domains"
5. You'll see a list of domains

### 3.2 Add Localhost
1. Click "Add domain" button
2. A popup will appear
3. Type: `localhost` (exactly like this, no http:// or www)
4. Click "Add" button
5. You'll see `localhost` added to the list

**✅ Step 3 Complete!** You can now test login on localhost.

---

## Step 4: Get Firebase Configuration (3 minutes)

### 4.1 Go to Project Settings
1. Look at the left sidebar
2. At the very bottom, you'll see a gear icon ⚙️
3. Click on the gear icon
4. A menu will appear
5. Click "Project settings" (first option)

### 4.2 Add Web App
1. Scroll down the page
2. Find section called "Your apps"
3. You'll see icons for different platforms (iOS, Android, Web)
4. Click on the **Web icon** (looks like `</>` or `<>`)
5. A popup will appear asking for app nickname
6. Type: `accreditation-frontend`
7. **IMPORTANT:** Do NOT check "Also set up Firebase Hosting"
8. Click "Register app" button

### 4.3 Copy Configuration
1. After clicking "Register app", you'll see code
2. It will look like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSyAbc123xyz...",
     authDomain: "accreditation-platform.firebaseapp.com",
     projectId: "accreditation-platform",
     storageBucket: "accreditation-platform.appspot.com",
     messagingSenderId: "123456789012",
     appId: "1:123456789012:web:abc123def456"
   };
   ```
3. **Copy all of this code** (select all and Ctrl+C)
4. Keep it somewhere safe (Notepad, etc.) - you'll need it next

**✅ Step 4 Complete!** You have your Firebase configuration.

---

## Step 5: Add Configuration to Your Project (5 minutes)

### 5.1 Navigate to Frontend Folder
1. Open File Explorer (Windows Explorer)
2. Go to: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`
3. You should see files like `package.json`, `next.config.js`, etc.

### 5.2 Create .env.local File
1. In the `frontend` folder, right-click in empty space
2. Select "New" → "Text Document"
3. Name it: `.env.local` (including the dot at the start)
4. **IMPORTANT:** If Windows asks "Are you sure you want to change the extension?", click "Yes"
5. If it shows as `.env.local.txt`, rename it to remove `.txt`

**Troubleshooting:** If you can't create `.env.local`:
- Open Notepad
- Go to File → Save As
- Navigate to `frontend` folder
- File name: `.env.local`
- Save as type: "All Files" (not Text Document)
- Click Save

### 5.3 Add Firebase Variables
1. Open `.env.local` file in a text editor
2. Copy and paste this template:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
   NEXT_PUBLIC_FIREBASE_APP_ID=
   ```

3. **Fill in the values** from the config you copied:
   - `NEXT_PUBLIC_FIREBASE_API_KEY=` → value from `apiKey: "..."` (without quotes)
   - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=` → value from `authDomain: "..."` (without quotes)
   - `NEXT_PUBLIC_FIREBASE_PROJECT_ID=` → value from `projectId: "..."` (without quotes)
   - `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=` → value from `storageBucket: "..."` (without quotes)
   - `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=` → value from `messagingSenderId: "..."` (without quotes)
   - `NEXT_PUBLIC_FIREBASE_APP_ID=` → value from `appId: "..."` (without quotes)

4. **Example of what it should look like:**
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAbc123xyz789
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=accreditation-platform.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=accreditation-platform
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=accreditation-platform.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
   NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abc123def456
   ```

5. **Save the file** (Ctrl+S)

**✅ Step 5 Complete!** Firebase config is now in your project.

---

## Step 6: Test Firebase Connection (2 minutes)

### 6.1 Start Frontend Server
1. Open Command Prompt or PowerShell
2. Navigate to frontend folder:
   ```bash
   cd C:\Users\datta\OneDrive\Desktop\gdg\frontend
   ```
3. Start the server:
   ```bash
   npm run dev
   ```
4. Wait for it to start (you'll see "Ready" message)
5. Keep this window open

### 6.2 Test Login
1. Open your browser
2. Go to: `http://localhost:3000`
3. You should see your app
4. Try to click "Login" or "Sign In" button
5. A Google sign-in popup should appear
6. Select your Google account
7. Click "Allow" or "Continue"
8. You should be logged in!

**✅ Step 6 Complete!** Firebase authentication is working!

---

## Troubleshooting

### Problem: Can't create .env.local file
**Solution:**
- Use Notepad
- Save As → Choose "All Files" type
- Name it exactly `.env.local`

### Problem: Login doesn't work
**Check:**
1. Is `.env.local` in the `frontend` folder? (not in root)
2. Did you restart the server after creating `.env.local`?
3. Are all values filled in (no empty values)?
4. Did you remove quotes from the values?

### Problem: "localhost not authorized"
**Solution:**
- Go back to Firebase Console
- Authentication → Sign-in method → Scroll down
- Make sure `localhost` is in authorized domains

### Problem: Can't find Firebase config
**Solution:**
- Go to Firebase Console
- Click gear icon ⚙️ → Project settings
- Scroll to "Your apps" section
- If you don't see web app, click `</>` icon to add one

---

## What's Next?

After Firebase is set up:
1. ✅ Authentication will work
2. ⏭️ Set up database (PostgreSQL on Supabase/Neon)
3. ⏭️ Set up file storage (Cloudflare R2 or AWS S3)

See `SETUP_GUIDE.md` for database and storage setup options.

---

## Summary Checklist

- [ ] Created Firebase project
- [ ] Enabled Google authentication
- [ ] Added localhost to authorized domains
- [ ] Got Firebase configuration
- [ ] Created `.env.local` file in frontend folder
- [ ] Added all 6 Firebase variables
- [ ] Tested login successfully

**You're done with Firebase setup! 🎉**

