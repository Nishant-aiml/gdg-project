# ⚡ Quick Start - Minimum Setup (5 Minutes)

**For local development, you only need these 2 things:**

## 1. Google Gemini API Key (FREE) 🆓

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

## 2. Create `.env` File

Create `backend/.env` with just this:

```env
GEMINI_API_KEY=your_gemini_key_here
```

**That's it!** The system will work with:
- ✅ Chatbot (using Gemini)
- ✅ OCR (using PaddleOCR - no setup needed)
- ✅ Database (using SQLite - no setup needed)

**Optional (but recommended):**
- Google Cloud Vision API (better OCR, free tier)
- OpenAI API (chatbot fallback)

See `SETUP_GUIDE.md` for full setup instructions.
