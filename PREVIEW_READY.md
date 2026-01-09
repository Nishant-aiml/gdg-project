# 🚀 Preview Ready!

Your AI-Powered Accreditation & Compliance Platform is now running!

## 🌐 Access Points

### Frontend (Main Application)
**URL:** http://localhost:3000

This is your main application interface where you can:
- Upload documents
- View dashboard
- Check KPIs
- Compare institutions
- View trends and forecasts
- Use the chatbot

### Backend API
**URL:** http://localhost:8000

### API Documentation (Interactive)
**URL:** http://localhost:8000/docs

This is an interactive API documentation where you can:
- Test all API endpoints
- See request/response formats
- Try API calls directly

---

## 📋 What You Can Do Now

### 1. Upload Documents
- Go to: http://localhost:3000/upload
- Upload PDF, Excel, CSV, or Word documents
- System will process them automatically

### 2. View Dashboard
- Go to: http://localhost:3000/dashboard
- See KPI scores, sufficiency, and compliance status
- Click on any KPI card to see detailed breakdown

### 3. Compare Institutions
- Go to: http://localhost:3000/compare
- Select multiple batches to compare
- See side-by-side comparison

### 4. View Trends
- Go to: http://localhost:3000/trends
- See year-over-year trends
- Requires at least 3 years of data

### 5. Use Chatbot
- Available on dashboard and other pages
- Ask questions like:
  - "Explain this score"
  - "What is FSR?"
  - "How is infrastructure calculated?"

---

## 🛠️ Server Status

### Backend Server
- **Status:** Running on port 8000
- **Location:** PowerShell window (first window)
- **Stop:** Press `Ctrl+C` in the backend window

### Frontend Server
- **Status:** Running on port 3000
- **Location:** PowerShell window (second window)
- **Stop:** Press `Ctrl+C` in the frontend window

---

## ✅ System Status

- ✅ Backend API: Running
- ✅ Frontend UI: Running
- ✅ Database: SQLite (initialized)
- ✅ Chatbot: Gemini API configured
- ✅ OCR: PaddleOCR (fallback available)

---

## 🎯 Quick Test

1. **Test Backend:**
   - Open: http://localhost:8000/docs
   - Try the `/api/batches/list` endpoint

2. **Test Frontend:**
   - Open: http://localhost:3000
   - Navigate through the pages

3. **Test Chatbot:**
   - Go to dashboard
   - Open chatbot
   - Ask: "What is this platform?"

---

## 📝 Notes

- Both servers are running in separate PowerShell windows
- To stop servers: Press `Ctrl+C` in each window
- To restart: Run `START_PREVIEW.ps1` again
- Database is stored in: `backend/storage/db/accreditation.db`

---

## 🎉 Enjoy Your Preview!

The platform is fully functional and ready for testing!

