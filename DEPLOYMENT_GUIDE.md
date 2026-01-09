# Deployment Guide - Railway + Vercel + Firebase

## 🎯 Architecture Overview

- **Backend**: Railway.app (FastAPI)
- **Frontend**: Vercel (Next.js)
- **Database**: Firebase Firestore
- **Storage**: Firebase Storage
- **Auth**: Firebase Authentication

---

## 📋 Prerequisites

1. Railway account (https://railway.app)
2. Vercel account (https://vercel.com)
3. Firebase project (https://console.firebase.google.com)

---

## 🔧 Step 1: Firebase Setup

### 1.1 Create Firebase Project
1. Go to Firebase Console
2. Create new project
3. Enable Firestore Database
4. Enable Firebase Storage
5. Enable Firebase Authentication

### 1.2 Generate Service Account Key
1. Go to Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Download JSON file
4. Save as `firebase-service-account.json` (locally)

### 1.3 Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write for authenticated users
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Department users can only access their department
    match /batches/{batchId} {
      allow read: if request.auth != null && 
        resource.data.department_id == request.auth.token.department_id;
      allow write: if request.auth != null && 
        request.resource.data.department_id == request.auth.token.department_id;
    }
  }
}
```

### 1.4 Storage Security Rules
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /documents/{institutionId}/{departmentId}/{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## 🚂 Step 2: Railway Backend Deployment

### 2.1 Create Railway Project
1. Go to Railway.app
2. Create new project
3. Connect GitHub repository (or deploy from local)

### 2.2 Add Service
1. Click "New Service"
2. Select "GitHub Repo" or "Empty Service"
3. Choose backend directory

### 2.3 Configure Environment Variables
Add to Railway environment variables:

```bash
# Firebase
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# OR use base64 encoded JSON
FIREBASE_SERVICE_ACCOUNT_BASE64=<base64-encoded-json>

# OpenAI (for fallback)
OPENAI_API_KEY=your_openai_key

# Gemini (primary chatbot)
GEMINI_API_KEY=your_gemini_key

# Firebase Config
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com

# Other settings
UNSTRUCTURED_LOCAL=true
```

### 2.4 Deploy
1. Railway will auto-detect Python
2. Install dependencies from `requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.5 Get Backend URL
- Railway provides public URL
- Example: `https://your-backend.railway.app`
- Add to Vercel environment variables

---

## ▲ Step 3: Vercel Frontend Deployment

### 3.1 Create Vercel Project
1. Go to Vercel dashboard
2. Import GitHub repository
3. Select frontend directory

### 3.2 Configure Environment Variables
Add to Vercel:

```bash
# Backend API
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Firebase (for client-side)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

### 3.3 Deploy
1. Vercel auto-detects Next.js
2. Builds and deploys automatically
3. Provides public URL

---

## 🔐 Step 4: Firebase Authentication Setup

### 4.1 Enable Authentication Providers
1. Go to Firebase Console → Authentication
2. Enable Email/Password
3. Enable Google (optional)

### 4.2 Configure Roles
Use custom claims for roles:
- `department_user`: Can access only their department
- `college_admin`: Can access all departments in institution
- `system_admin`: Full access

### 4.3 Frontend Integration
Update `frontend/lib/firebase.ts`:
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
```

---

## 📁 Step 5: File Storage Migration

### 5.1 Update Upload Service
Replace local file storage with Firebase Storage:

```python
from google.cloud import storage

def upload_to_firebase(file_path: str, destination_path: str) -> str:
    client = storage.Client()
    bucket = client.bucket(os.getenv("FIREBASE_STORAGE_BUCKET"))
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(file_path)
    return blob.public_url
```

### 5.2 Update Document Paths
- Store Firebase Storage URLs instead of local paths
- Update download logic to use Firebase Storage

---

## 🧪 Step 6: Testing

### 6.1 Test Backend
```bash
curl https://your-backend.railway.app/health
```

### 6.2 Test Frontend
1. Visit Vercel URL
2. Test login
3. Test document upload
4. Test dashboard

### 6.3 Test Firebase
1. Check Firestore collections
2. Check Storage files
3. Check Authentication users

---

## 🔄 Step 7: Data Migration (If Needed)

If migrating from SQLite:

1. Export SQLite data
2. Run migration script:
```python
python scripts/migrate_to_firestore.py
```

---

## 📊 Monitoring

### Railway
- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts

### Vercel
- View analytics
- Monitor performance
- Check build logs

### Firebase
- Monitor Firestore usage
- Check Storage usage
- View Authentication logs

---

## 🚨 Troubleshooting

### Backend Issues
- Check Railway logs
- Verify environment variables
- Check Firebase service account permissions

### Frontend Issues
- Check Vercel build logs
- Verify environment variables
- Check Firebase config

### Database Issues
- Check Firestore security rules
- Verify indexes are created
- Check query limits

---

## ✅ Deployment Checklist

- [ ] Firebase project created
- [ ] Firestore enabled
- [ ] Storage enabled
- [ ] Authentication enabled
- [ ] Service account key generated
- [ ] Railway project created
- [ ] Backend deployed to Railway
- [ ] Environment variables set in Railway
- [ ] Vercel project created
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set in Vercel
- [ ] Firebase config added to frontend
- [ ] Authentication tested
- [ ] File upload tested
- [ ] Dashboard tested
- [ ] All endpoints working

---

## 🎯 Post-Deployment

1. **Set up monitoring**: Railway + Vercel analytics
2. **Configure backups**: Firestore automatic backups
3. **Set up alerts**: For errors and high usage
4. **Document access**: Share credentials securely
5. **Test all flows**: User flow, system flow, data flow

---

**Status**: Ready for deployment after Firestore migration

