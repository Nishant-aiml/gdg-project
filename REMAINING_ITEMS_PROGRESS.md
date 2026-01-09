# Remaining Items Progress

## ✅ Completed

### 1. Trends Department-Wise Validation (`trends-1`)
- ✅ `ProductionGuard.validate_trends_data_contract()` enforces:
  - Same institution
  - Same department
  - Minimum 3 distinct years
  - Strict academic_year ordering
- ✅ Trends endpoint uses ProductionGuard
- ✅ Forecast endpoint uses ProductionGuard
- **Status**: ✅ Complete

### 2. Chatbot Grounding (`chatbot-1`)
- ✅ `explain_score()` function calls `/api/kpi/details/{batch_id}/{kpi_type}`
- ✅ Refuses to answer if KPI details API fails
- ✅ Uses ONLY backend API data, no inference
- ✅ System prompt enforces grounding
- **Status**: ✅ Complete

### 3. File Format Support (`files-1`)
- ✅ `parse_pdf_document()` - PDF support
- ✅ `parse_excel_document()` - Excel (.xlsx, .xls) support
- ✅ `parse_csv_document()` - CSV support
- ✅ `parse_word_document()` - Word (.docx) support
- ✅ All parsers have retry logic with 30s timeout
- **Status**: ✅ Complete

### 4. Performance Verification (`perf-1`)
- ✅ Batch creation uses `BackgroundTasks` and `threading.Thread`
- ✅ Returns immediately (<2 seconds)
- ✅ Heavy processing deferred to background
- ✅ Request timeouts implemented (30s parsing, 60s AI, 20s chatbot)
- ✅ Retry logic for parsing failures
- **Status**: ✅ Complete

## 🔄 In Progress

### 5. Role-Based UI Rendering (`auth-4`)
- ✅ Navbar shows role badge
- ✅ Admin-only navigation link added
- ✅ Dashboard action buttons conditionally shown
- ⚠️ Need to add more role-based filtering in other pages
- **Status**: 🔄 60% Complete

### 6. Department-Wise Data Storage (`data-2`)
- ✅ Backend filters batches by role (admin/college/department)
- ✅ Batch creation links to user/institution/department
- ⚠️ Need to add institution/department selectors in frontend
- ⚠️ Need to verify department filtering in all queries
- **Status**: 🔄 70% Complete

### 7. Evidence Requirement Enforcement (`evidence-1`)
- ✅ `ProductionGuard.validate_evidence_required()` exists
- ✅ Added evidence validation to FSR calculation
- ⚠️ Need to add to all other KPI calculations
- **Status**: 🔄 20% Complete

## 📋 Remaining

### 8. Frontend Completeness (`frontend-1`)
- Need to verify all pages are visible and functional
- Need to test all navigation flows

### 9. End-to-End Test (`e2e-1`)
- Full user journey test needed

## 🎯 Next Steps

1. Complete evidence enforcement for all KPIs
2. Add institution/department selectors in frontend
3. Complete role-based UI rendering
4. Frontend completeness check
5. End-to-end test

