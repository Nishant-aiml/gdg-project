# 🧪 What to Test - Key Features & Changes

## 🎯 What You're Seeing

The homepage you see is the **entry point**. The real functionality is in the pages you can navigate to.

---

## 🚀 Key Features to Test

### 1. **Upload Documents** (Main Feature)
**URL:** http://localhost:3000/upload

**What to do:**
1. Click on any mode (AICTE, UGC, or Mixed)
2. Or go directly to: http://localhost:3000/upload
3. Upload a PDF, Excel, or CSV file
4. System will:
   - Extract data using AI
   - Calculate KPIs automatically
   - Show processing progress

**What's new:**
- ✅ Fully async processing (doesn't block UI)
- ✅ Real-time progress updates
- ✅ Automatic KPI calculation
- ✅ Evidence tracking for every score

---

### 2. **Dashboard with Real KPIs** (Core Feature)
**URL:** http://localhost:3000/dashboard?batch_id=YOUR_BATCH_ID

**What to do:**
1. After uploading, you'll be redirected to dashboard
2. Or go to: http://localhost:3000/dashboard
3. You'll see:
   - **KPI Cards** (FSR, Infrastructure, Placement, Lab Compliance, Overall Score)
   - **Sufficiency Score** (how complete the data is)
   - **Processing Status**

**What's new:**
- ✅ **NO dummy data** - All scores come from real calculations
- ✅ **Evidence-backed** - Every score traces to document evidence
- ✅ **KPI Drill-down** - Click any KPI card to see:
   - Formula used
   - Input parameters
   - Weights
   - Evidence snippets
   - Page numbers

---

### 3. **KPI Details Modal** (New Feature)
**How to access:**
1. Go to dashboard
2. Click on any KPI card (e.g., "FSR", "Infrastructure")
3. Modal opens showing:
   - **Formula:** Exact formula used
   - **Parameters:** All input values
   - **Weights:** Official weights from handbooks
   - **Contributions:** How each parameter contributes
   - **Evidence:** Document snippets + page numbers

**What's new:**
- ✅ **Real backend data only** - No hardcoded values
- ✅ **Evidence traceability** - Every number has proof
- ✅ **All 4 modes supported:** AICTE, NBA, NAAC, NIRF

---

### 4. **Chatbot with Score Explanation** (New Feature)
**How to access:**
1. Go to dashboard or any page
2. Open the chatbot (usually bottom-right or sidebar)
3. Ask questions like:
   - "Explain this score"
   - "Why is FSR low?"
   - "What is missing for approval?"

**What's new:**
- ✅ **Grounded to backend** - Uses real API data only
- ✅ **Explain score feature** - Calls `/api/kpi/details` internally
- ✅ **No hallucination** - Refuses to answer if data is missing
- ✅ **Evidence-based** - Shows evidence snippets in responses

---

### 5. **Compare Institutions** (Enhanced)
**URL:** http://localhost:3000/compare

**What to do:**
1. Select multiple batches to compare
2. See side-by-side comparison
3. View strengths/weaknesses

**What's new:**
- ✅ **Invalid batch exclusion** - Only valid batches shown
- ✅ **Department-wise filtering** - No cross-department mixing
- ✅ **Real comparison** - Uses actual calculated scores

---

### 6. **Trends & Forecasts** (Enhanced)
**URL:** http://localhost:3000/trends

**What to do:**
1. View year-over-year trends
2. Requires at least 3 years of data
3. See forecast predictions

**What's new:**
- ✅ **Data contract enforcement** - Same institution, same department
- ✅ **Minimum 3 years** - Proper error if insufficient data
- ✅ **No flat-line graphs** - Handles missing data correctly

---

### 7. **API Documentation** (Interactive)
**URL:** http://localhost:8000/docs

**What to do:**
1. Test all API endpoints
2. See request/response formats
3. Try API calls directly

**Key endpoints to test:**
- `POST /api/batches/create` - Create new batch
- `GET /api/dashboard/{batch_id}` - Get dashboard data
- `GET /api/kpi/details/{batch_id}/{kpi_type}` - Get KPI breakdown
- `POST /api/chatbot/query` - Chat with AI
- `POST /api/chatbot/explain_score` - Explain a score

---

## 🔍 What Changed Behind the Scenes

### 1. **Production Hardening**
- ✅ Invalid batches automatically marked and excluded
- ✅ No dummy data anywhere
- ✅ Missing data returns `NULL`, not zero
- ✅ Every score traces to evidence

### 2. **Performance Optimizations**
- ✅ Async batch creation (returns immediately)
- ✅ Request timeouts (30s parsing, 60s AI, 20s chatbot)
- ✅ Retry logic for failures
- ✅ Caching for frequently accessed data

### 3. **Chatbot Enhancements**
- ✅ Grounded to backend APIs only
- ✅ "Explain score" feature
- ✅ Refuses policy/hypothetical questions
- ✅ Evidence-based responses

### 4. **Formula Engine**
- ✅ All 4 modes: AICTE, NBA, NAAC, NIRF
- ✅ Official handbook formulas
- ✅ No fallback values
- ✅ Evidence required for calculations

---

## 🧪 Quick Test Flow

### Test 1: Upload & Process
1. Go to: http://localhost:3000/upload
2. Upload a PDF document
3. Watch processing progress
4. Wait for completion

### Test 2: View Dashboard
1. After processing, view dashboard
2. See real KPI scores
3. Click on any KPI card
4. See detailed breakdown with evidence

### Test 3: Use Chatbot
1. Open chatbot
2. Ask: "Explain the FSR score"
3. See evidence-based explanation
4. Ask: "What is missing?"
5. Get real recommendations

### Test 4: Check API
1. Go to: http://localhost:8000/docs
2. Try: `GET /api/dashboard/{batch_id}`
3. See real data in response
4. No dummy values

---

## 📊 What Makes This Different

### Before (Hypothetical):
- ❌ Dummy data in UI
- ❌ Hardcoded scores
- ❌ No evidence tracking
- ❌ Chatbot hallucinates
- ❌ Invalid batches shown

### Now (Production-Ready):
- ✅ Real data only
- ✅ Backend-driven calculations
- ✅ Evidence for every score
- ✅ Chatbot grounded to APIs
- ✅ Invalid batches excluded

---

## 🎯 Next Steps

1. **Upload a document** to see real processing
2. **View dashboard** to see calculated KPIs
3. **Click KPI cards** to see evidence
4. **Use chatbot** to ask questions
5. **Check API docs** to see backend data

The homepage is just the start - the real functionality is in the pages you navigate to!

