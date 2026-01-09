# Frontend-Backend Connection Testing Guide

## Prerequisites

1. **Backend must be running:**
   ```bash
   cd backend
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Frontend must be running:**
   ```bash
   cd frontend
   npm run dev
   ```

## Automated Testing

### Run Comprehensive Test Suite

```bash
python test_frontend_backend_connections.py
```

This will test:
- ✅ Health check
- ✅ Batch APIs (create, list)
- ✅ Dashboard APIs (data, evaluations, trends, forecast, KPI details)
- ✅ Comparison APIs
- ✅ Report APIs
- ✅ Chatbot APIs
- ✅ Invalid batch handling
- ✅ Role-based access

### Expected Output

```
============================================================
  FRONTEND-BACKEND CONNECTION TEST SUITE
============================================================

[PASS] Backend is running

============================================================
1. HEALTH CHECK
============================================================
[PASS] Health Check - Status 200

============================================================
2. BATCH APIs
============================================================
[PASS] List Batches - Status 200
ℹ   Found 5 existing batches
[PASS] Create AICTE Batch - Status 200
ℹ   Created batch: abc123...

... (more tests)
```

## Manual Testing Checklist

### 1. Dashboard Flow ✅

**Steps:**
1. Open browser to `http://localhost:3000`
2. Login with Firebase (department or institution user)
3. Should land on Dashboard page
4. **Evaluation Selector** should be visible
5. Select an evaluation from dropdown
6. Dashboard should load with:
   - Real KPI cards (not dummy data)
   - Sufficiency percentage
   - Compliance flags
   - Information blocks

**Verify:**
- ✅ No dummy/placeholder data
- ✅ Null values show "Insufficient Data" (not 0)
- ✅ Invalid batches show warning banner
- ✅ All data comes from backend API

### 2. KPI Drill-Down Modal ✅

**Steps:**
1. On dashboard, click any KPI card
2. Modal should open
3. Should display:
   - Formula
   - Parameter contributions
   - Step-by-step calculation
   - Evidence snippets

**Verify:**
- ✅ Modal calls `/api/dashboard/kpi-details/{batch_id}?kpi_type={kpi_type}`
- ✅ Shows real calculations (not frontend math)
- ✅ Missing parameters marked clearly
- ✅ Evidence includes page numbers and snippets

### 3. Trends Page ✅

**Steps:**
1. Click "View Trends" button on dashboard
2. Should navigate to `/trends?batch_id={id}`
3. If < 3 years data:
   - Should show "Insufficient Data" banner
   - Should NOT render empty graphs
   - Should show backend error message
4. If ≥ 3 years data:
   - Should show meaningful line charts
   - Should show slope indicators
   - Should show trend insights

**Verify:**
- ✅ Calls `/api/dashboard/trends/{batch_id}`
- ✅ Handles insufficient data gracefully
- ✅ Only renders graphs when data available
- ✅ Invalid batches excluded

### 4. Forecast Page ✅

**Steps:**
1. Click "View Forecast" button on dashboard
2. Should navigate to `/forecast?batch_id={id}`
3. Select a KPI from dropdown
4. If < 3 years data:
   - Should show "Insufficient Data" banner
   - Should show backend error reason
   - Should NOT render forecast chart
5. If ≥ 3 years data:
   - Should show forecast line chart
   - Should show confidence bands
   - Should show forecast table

**Verify:**
- ✅ Calls `/api/dashboard/forecast/{batch_id}/{kpi_name}`
- ✅ Handles insufficient data gracefully
- ✅ Shows predicted values with confidence intervals
- ✅ Invalid batches excluded

### 5. Comparison Page ✅

**Steps:**
1. Navigate to `/compare`
2. Select 2+ batches
3. Click "Compare Institutions"
4. Should show:
   - Comparison results
   - Winner institution
   - KPI comparison charts
   - Category winners

**Verify:**
- ✅ Calls `/api/compare?batch_ids={ids}`
- ✅ Prevents cross-department comparison
- ✅ Shows validation message if invalid
- ✅ Displays skipped batches with reasons
- ✅ Invalid batches excluded

### 6. Report Generation ✅

**Steps:**
1. On dashboard, click "Generate Report"
2. Should show loading state
3. PDF should download automatically
4. Report should include:
   - Scores
   - Sufficiency
   - Compliance flags
   - Gaps and recommendations
   - Evidence summary

**Verify:**
- ✅ Calls `/api/reports/generate`
- ✅ Calls `/api/reports/download/{batch_id}`
- ✅ Handles errors gracefully
- ✅ Invalid batches cannot generate reports

### 7. Chatbot ✅

**Steps:**
1. Open chatbot (click chat icon)
2. Ask: "Explain the overall score"
3. Should return grounded answer
4. Should show citations (if available)

**Verify:**
- ✅ Calls `/api/chatbot/query`
- ✅ Uses current batch_id and page context
- ✅ Answers grounded to backend data
- ✅ Handles errors gracefully

### 8. Invalid Batch Handling ✅

**Steps:**
1. Find or create an invalid batch (0% sufficiency or null overall_score)
2. Try to view dashboard
3. Should show warning banner
4. Try to compare
5. Should be excluded from comparison
6. Try to view trends
7. Should show error or be excluded
8. Try to generate forecast
9. Should show error

**Verify:**
- ✅ Invalid batches marked by backend
- ✅ Frontend shows clear warnings
- ✅ Excluded from analysis operations
- ✅ Clear action required message

### 9. Role-Based Access ✅

**Steps:**
1. Login as department user
2. Should only see own department's batches
3. Try to access other department's batch
4. Should be denied (403 or redirect)
5. Login as institution user
6. Should see all departments
7. Can switch between departments

**Verify:**
- ✅ ProtectedRoute enforces authentication
- ✅ Backend enforces role-based access
- ✅ Department users restricted to own department
- ✅ Institution users can access all

## Data Contract Verification

### Null Value Handling
- ✅ Frontend displays `null` as "Insufficient Data"
- ✅ Frontend does NOT convert `null` to `0`
- ✅ Frontend does NOT fabricate values
- ✅ Backend returns `null` for missing data

### Error Handling
- ✅ All API calls have try/catch blocks
- ✅ Error messages displayed to users
- ✅ Graceful degradation when data insufficient
- ✅ No silent failures

## Browser Console Checks

Open browser DevTools (F12) and check:

1. **Network Tab:**
   - All API calls return 200 (or expected error codes)
   - No 500 errors
   - No CORS errors
   - Response times reasonable

2. **Console Tab:**
   - No JavaScript errors
   - No unhandled promise rejections
   - No API call failures

3. **Application Tab:**
   - Firebase auth tokens present
   - User role stored correctly

## Common Issues & Solutions

### Backend Not Running
**Error:** `Connection refused` or `ECONNREFUSED`
**Solution:** Start backend: `cd backend && uvicorn main:app --reload`

### CORS Errors
**Error:** `CORS policy blocked`
**Solution:** Check backend CORS settings in `backend/main.py`

### 401 Unauthorized
**Error:** `401 Unauthorized` on API calls
**Solution:** Check Firebase auth token, ensure user is logged in

### 403 Forbidden
**Error:** `403 Forbidden` on API calls
**Solution:** Check user role and department access

### Null Values Showing as 0
**Error:** KPIs showing 0 instead of "Insufficient Data"
**Solution:** Check frontend null handling in `frontend/app/dashboard/page.tsx`

### Invalid Batch Not Excluded
**Error:** Invalid batches still showing in comparison
**Solution:** Check backend `is_invalid` flag and frontend filtering

## Test Results Summary

After running all tests, verify:

- ✅ All critical endpoints respond correctly
- ✅ No dummy data in responses
- ✅ Null values handled correctly
- ✅ Invalid batches excluded
- ✅ Role-based access enforced
- ✅ Error messages user-friendly
- ✅ UI reflects backend data accurately

## Next Steps

1. Run automated test suite
2. Complete manual testing checklist
3. Test with real user accounts (both roles)
4. Test with various data scenarios:
   - Valid batches
   - Invalid batches
   - Insufficient data batches
   - Multi-year data batches
5. Verify all error messages are clear
6. Test edge cases (empty lists, null responses, etc.)

