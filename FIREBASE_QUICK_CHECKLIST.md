# Firebase Setup - Quick Checklist

## ✅ What You've Done
- [x] Enabled Email/Password authentication
- [x] Enabled Google Sign-In
- [x] Set support email

## 📋 What to Do Next (5 minutes)

### Step 1: Get Firebase Config (2 min)
- [ ] Go to Firebase Console: https://console.firebase.google.com/
- [ ] Select project: `project-831601787756`
- [ ] Click gear icon ⚙️ → Project settings
- [ ] Scroll to "Your apps" section
- [ ] If no web app: Click `</>` icon → Register app
- [ ] Copy the `firebaseConfig` object

### Step 2: Create .env.local File (2 min)
- [ ] Go to: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`
- [ ] Create file: `.env.local` (with the dot!)
- [ ] Add these 6 lines (fill with YOUR values):

```env
NEXT_PUBLIC_FIREBASE_API_KEY=YOUR_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=project-831601787756.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=project-831601787756
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=project-831601787756.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=831601787756
NEXT_PUBLIC_FIREBASE_APP_ID=YOUR_APP_ID
```

**Fill in:**
- `YOUR_API_KEY` → from `apiKey` in config
- `YOUR_APP_ID` → from `appId` in config
- Other values are already filled for you!

### Step 3: Add Localhost (1 min)
- [ ] Go to Firebase Console
- [ ] Authentication → Sign-in method
- [ ] Scroll to "Authorized domains"
- [ ] Click "Add domain"
- [ ] Type: `localhost`
- [ ] Click "Add"

### Step 4: Test (1 min)
- [ ] Open terminal
- [ ] `cd frontend`
- [ ] `npm run dev`
- [ ] Open browser: http://localhost:3000
- [ ] Try to login (Google or Email)
- [ ] Should work! ✅

## 🎯 That's It!

After this, Firebase authentication will be fully working!

**See `FIREBASE_NEXT_STEPS.md` for detailed instructions.**

