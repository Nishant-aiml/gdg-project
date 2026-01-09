# Production-Ready Accreditation Platform - Implementation Checklist

## ✅ COMPLETED

### 1. Zero Dummy Data Policy
- ✅ KPI detailed service uses real backend computation only
- ✅ No hardcoded scores in backend services
- ✅ Evidence tracking in extraction pipeline
- ✅ "Not enough data" responses instead of fabricating values

### 2. Backend as Single Source of Truth
- ✅ KPI drill-down API (`/api/kpis/{batch_id}/{kpi_name}/details`)
- ✅ All calculations in backend services
- ✅ Frontend must call backend APIs (pending frontend update)

### 3. Production Safety - Invalid Batch Enforcement
- ✅ `is_invalid` flag in Batch model
- ✅ Validation logic in optimized pipeline
- ✅ Comparison engine excludes invalid batches
- ✅ Trends exclude invalid batches

### 4. Department-Wise Data Hierarchy
- ✅ Database schema: `institution_name`, `department_name`, `academic_year`
- ✅ Batch creation accepts hierarchy fields
- ✅ Indexed for fast queries

### 5. Document Hash Deduplication
- ✅ `document_hash` field in File model
- ✅ Hash calculation utility
- ✅ Duplicate detection on upload
- ✅ Database cleanup script for duplicates

### 6. Database Cleanup & Hygiene
- ✅ Cleanup script for:
  - Duplicate documents
  - Invalid batches
  - Orphaned files/blocks
  - Uniqueness enforcement (institution + department + year)

### 7. AI Model Prioritization
- ✅ Gemini (free tier) as primary chatbot
- ✅ GPT-5 Nano as fallback 1
- ✅ GPT-5 Mini as fallback 2
- ✅ Google Cloud Vision API (free tier) for OCR

### 8. Pipeline Optimization
- ✅ Fast path / Heavy path separation
- ✅ Async worker support
- ✅ Stage-based progress updates

## ⏳ PENDING (Critical)

### 1. Frontend Cleanup
- [ ] Remove all hardcoded parameter tables
- [ ] Remove dummy KPI values
- [ ] Remove placeholder trend data
- [ ] All data from `/api/kpis/{batch_id}/{kpi_name}/details`
- [ ] Show "Not enough data" instead of fabricating

### 2. Extraction Pipeline Enhancement
- [ ] Extract institution/department from documents if not provided
- [ ] Enhanced evidence tracking (page numbers, snippets)
- [ ] Store evidence in Block model

### 3. Trends Engine
- [ ] Department-wise filtering
- [ ] 3-year minimum enforcement
- [ ] Slope, CAGR, best/worst year calculation
- [ ] Disable when insufficient data

### 4. Forecast Engine
- [ ] Statistical model (simple, explainable)
- [ ] Confidence bands
- [ ] Disable when insufficient data
- [ ] Explanation text

### 5. Performance Optimization
- [ ] API response caching
- [ ] Database query indexing
- [ ] Frontend lazy loading
- [ ] Skeleton loaders
- [ ] Mobile-first responsiveness

## 📋 Implementation Priority

### Phase 1: Critical Backend (DONE)
1. ✅ Invalid batch enforcement
2. ✅ Document hash deduplication
3. ✅ Database cleanup script
4. ✅ Department hierarchy schema

### Phase 2: Frontend Cleanup (NEXT)
1. Remove dummy data from dashboard
2. Remove dummy data from comparison
3. Remove dummy data from trends
4. Use backend APIs exclusively

### Phase 3: Enhanced Features
1. Trends department-wise filtering
2. Forecast statistical model
3. Performance optimizations
4. Mobile responsiveness

## 🧪 Acceptance Tests

### Backend Tests
- [x] Real PDF → real KPI scores
- [x] CSV/Excel → proper extraction
- [x] No KPI without evidence
- [x] Invalid batches excluded from comparison
- [ ] Trends require 3+ years
- [ ] Forecast disabled when insufficient data

### Frontend Tests
- [ ] Dashboard loads <1s
- [ ] No dummy data displayed
- [ ] All data from backend APIs
- [ ] "Not enough data" shown when appropriate
- [ ] Mobile responsive

## 🚀 Deployment Checklist

1. ✅ Environment variables configured (.env)
2. ✅ Dependencies installed
3. ✅ Database schema updated
4. ⏳ Frontend cleaned (dummy data removed)
5. ⏳ Performance optimizations applied
6. ⏳ Acceptance tests passed

## 📝 Notes

- All backend services follow "zero dummy data" policy
- Invalid batches are automatically excluded from all operations
- Document deduplication prevents duplicate uploads
- Database cleanup script should be run periodically
- Frontend cleanup is the next critical step

