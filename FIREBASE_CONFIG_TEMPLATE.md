# Firebase Configuration Template

## Your Project Info
- **Project ID:** project-831601787756
- **Support Email:** dattanishant2@gmail.com

## Where to Find Your Config

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project: `project-831601787756`
3. Click gear icon ⚙️ → Project settings
4. Scroll to "Your apps" section
5. Find your web app (or add one by clicking `</>` icon)
6. Copy the `firebaseConfig` object

## .env.local Template

Create `frontend/.env.local` file with this template:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=YOUR_API_KEY_HERE
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=project-831601787756.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=project-831601787756
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=project-831601787756.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=831601787756
NEXT_PUBLIC_FIREBASE_APP_ID=YOUR_APP_ID_HERE
```

## How to Fill It

From the Firebase config you copied:

1. **apiKey** → `NEXT_PUBLIC_FIREBASE_API_KEY`
   - Example: `AIzaSyAbc123xyz789...`
   - Copy the entire value (it's long)

2. **authDomain** → `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
   - Should be: `project-831601787756.firebaseapp.com`

3. **projectId** → `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
   - Should be: `project-831601787756`

4. **storageBucket** → `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
   - Should be: `project-831601787756.appspot.com`

5. **messagingSenderId** → `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
   - Should be: `831601787756`

6. **appId** → `NEXT_PUBLIC_FIREBASE_APP_ID`
   - Example: `1:831601787756:web:abc123def456`
   - Copy the entire value

## Important Notes

- ✅ Remove quotes from values (no `"` around them)
- ✅ No spaces around `=`
- ✅ One variable per line
- ✅ File must be named exactly `.env.local` (with the dot)
- ✅ File must be in `frontend` folder (not root)

## Example of Complete File

```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyC7vK8mN9oP0qR1sT2uV3wX4yZ5a6b7c8d9e0f
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=project-831601787756.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=project-831601787756
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=project-831601787756.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=831601787756
NEXT_PUBLIC_FIREBASE_APP_ID=1:831601787756:web:1a2b3c4d5e6f7g8h9i0j
```

## After Saving

1. **Restart frontend server** (if it's running):
   - Stop it (Ctrl+C)
   - Start again: `npm run dev`

2. **Test login:**
   - Go to http://localhost:3000
   - Try to login
   - Should work!

## Troubleshooting

**"Firebase config not found"**
- Check `.env.local` is in `frontend` folder
- Check all 6 variables are filled
- Restart the server

**"localhost not authorized"**
- Go to Firebase Console
- Authentication → Sign-in method
- Scroll to "Authorized domains"
- Add `localhost`

**"Invalid API key"**
- Double-check you copied the entire API key
- Make sure no quotes around values
- Make sure no extra spaces

