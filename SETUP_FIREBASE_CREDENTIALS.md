# 🔐 Setup Firebase Service Account Credentials

## ✅ Step 1: You've Already Done This!
You've downloaded the Firebase service account JSON file and placed it in the `backend/` directory.

## 🔍 Step 2: Find the Filename

The JSON file should have a name like:
- `accreditation-platform-xxxxx.json` (downloaded from Firebase Console)
- Or any name you chose (e.g., `firebase-service-account.json`)

## 📝 Step 3: Update `.env` File

Add this line to your `.env` file (in the project root):

```env
GOOGLE_APPLICATION_CREDENTIALS=./backend/your-filename.json
```

Replace `your-filename.json` with the actual filename of your Firebase service account JSON file.

**Example:**
If your file is named `accreditation-platform-abc123.json`, add:
```env
GOOGLE_APPLICATION_CREDENTIALS=./backend/accreditation-platform-abc123.json
```

## 🔒 Step 4: Add to .gitignore (Important!)

Add the service account file to `.gitignore` to prevent committing it to git:

```gitignore
# Firebase service account (DO NOT COMMIT)
backend/*service*account*.json
backend/accreditation-platform-*.json
```

Or add the specific filename if you know it.

## 🚀 Step 5: Restart Backend

After updating `.env`, restart your backend server.

## ✅ Verification

When the backend starts, you should see:
```
INFO - Firebase Admin initialized with service account credentials
```

If you see this message, Firebase authentication is configured correctly!

---

## 📋 Quick Checklist

- [x] Download Firebase service account JSON file
- [x] Place JSON file in `backend/` directory
- [ ] Find the exact filename
- [ ] Add `GOOGLE_APPLICATION_CREDENTIALS=./backend/filename.json` to `.env`
- [ ] Add filename to `.gitignore`
- [ ] Restart backend
- [ ] Verify: "Firebase Admin initialized with service account credentials" in logs

---

## 🎯 Next Steps

Once you've completed the steps above:
1. Tell me the filename of your JSON file
2. OR update the `.env` file yourself with the path
3. Then restart the backend

The authentication should work after this! 🎉

