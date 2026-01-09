# Create .env.local File - Exact Steps

## Your Firebase Config is Ready!

I've prepared your configuration. Here's exactly what to do:

## Step 1: Create the File (2 minutes)

### Method 1: Using Notepad (Easiest)

1. **Open Notepad**
   - Press Windows key
   - Type "Notepad"
   - Press Enter

2. **Copy and Paste This Exact Content:**
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCMjAl_wX-ctw65PDyaOV1MVsNQU9UM6vE
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=accreditation-platform.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=accreditation-platform
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=accreditation-platform.firebasestorage.app
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=831601787756
   NEXT_PUBLIC_FIREBASE_APP_ID=1:831601787756:web:7cc042ed455cc79151e949
   NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000/api
   ```

3. **Save the File**
   - Click File → Save As
   - Navigate to: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`
   - **File name:** `.env.local` (with the dot!)
   - **Save as type:** "All Files" (important! Not "Text Documents")
   - Click Save

### Method 2: Using File Explorer

1. **Go to Frontend Folder**
   - Open File Explorer
   - Navigate to: `C:\Users\datta\OneDrive\Desktop\gdg\frontend`

2. **Create New File**
   - Right-click in empty space
   - New → Text Document
   - Name it: `.env.local` (with the dot!)
   - If Windows warns about extension, click "Yes"

3. **Open and Paste**
   - Right-click `.env.local` → Open with → Notepad
   - Paste the content from above
   - Save (Ctrl+S)

## Step 2: Verify File Location

The file should be here:
```
C:\Users\datta\OneDrive\Desktop\gdg\frontend\.env.local
```

**NOT here:**
- ❌ `C:\Users\datta\OneDrive\Desktop\gdg\.env.local` (wrong folder)
- ❌ `C:\Users\datta\OneDrive\Desktop\gdg\frontend\.env.local.txt` (wrong extension)

## Step 3: Test It Works

1. **Start Frontend:**
   ```bash
   cd C:\Users\datta\OneDrive\Desktop\gdg\frontend
   npm run dev
   ```

2. **Check for Errors:**
   - If you see "Firebase config not found" → File is in wrong location
   - If no errors → It's working! ✅

## Step 4: Add Localhost to Firebase (1 min)

1. Go to: https://console.firebase.google.com/
2. Select project: `accreditation-platform`
3. Authentication → Sign-in method
4. Scroll to "Authorized domains"
5. Click "Add domain"
6. Type: `localhost`
7. Click "Add"

## Step 5: Test Login

1. Open: http://localhost:3000
2. Try to login
3. Should work! 🎉

## Troubleshooting

### "File won't save as .env.local"
**Fix:**
- Use Notepad
- Save As → Choose "All Files" type
- Name: `.env.local`

### "Firebase config not found"
**Check:**
- Is file in `frontend` folder? (not root)
- Is it named exactly `.env.local`? (not `.env.local.txt`)
- Did you restart the server after creating file?

### "localhost not authorized"
**Fix:**
- Go to Firebase Console
- Authentication → Sign-in method
- Add `localhost` to authorized domains

## ✅ Done!

After these steps, Firebase authentication will be fully working!

