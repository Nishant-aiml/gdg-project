# Firebase Firestore Migration Plan
## Railway + Vercel + Firebase Architecture

## 🎯 Migration Overview

**Current**: SQLite + SQLAlchemy  
**Target**: Firebase Firestore  
**Deployment**: Railway (Backend) + Vercel (Frontend) + Firebase (DB/Storage/Auth)

---

## 📋 Firestore Collections Structure

### 1. `institutions`
```typescript
{
  institution_id: string (auto-generated),
  name: string,
  code: string?,
  created_at: timestamp,
  is_active: boolean
}
```

### 2. `departments`
```typescript
{
  department_id: string (auto-generated),
  institution_id: string,
  name: string,
  code: string?,
  created_at: timestamp,
  is_active: boolean
}
```

### 3. `batches`
```typescript
{
  batch_id: string (primary key),
  institution_id: string,
  department_id: string,
  academic_year: string, // "2024-25"
  accreditation_mode: string, // "aicte" | "nba" | "naac" | "nirf"
  mode: string, // legacy compatibility
  new_university: boolean,
  status: string, // "created" | "processing" | "completed" | "failed" | "invalid"
  is_valid: boolean, // true = valid, false = invalid
  is_invalid: number, // 0 = valid, 1 = invalid (legacy)
  authenticity_score: number?,
  created_at: timestamp,
  updated_at: timestamp,
  errors: string[]?,
  // Results stored as nested objects
  sufficiency_result: object?,
  kpi_results: object?,
  compliance_results: object?,
  trend_results: object?,
  approval_classification: object?,
  approval_readiness: object?,
  unified_report: object?
}
```

### 4. `documents`
```typescript
{
  document_id: string (primary key),
  batch_id: string,
  institution_id: string,
  department_id: string,
  academic_year: string,
  filename: string,
  filepath: string, // Firebase Storage path
  file_size: number,
  document_hash: string, // SHA256 for deduplication
  file_type: string, // "pdf" | "xlsx" | "csv" | "docx"
  uploaded_at: timestamp,
  is_valid: boolean
}
```

### 5. `blocks`
```typescript
{
  block_id: string (primary key),
  batch_id: string,
  institution_id: string,
  department_id: string,
  academic_year: string,
  block_type: string, // "faculty_information", etc.
  data: object, // extracted_data
  confidence: number,
  extraction_confidence: number,
  evidence_snippet: string?,
  evidence_page: number?,
  source_doc: string, // filename
  is_outdated: boolean,
  is_low_quality: boolean,
  is_invalid: boolean,
  created_at: timestamp
}
```

### 6. `kpis`
```typescript
{
  kpi_id: string (auto-generated),
  batch_id: string,
  institution_id: string,
  department_id: string,
  academic_year: string,
  kpi_name: string, // "fsr_score", "infrastructure_score", etc.
  kpi_value: number?,
  kpi_details: object?, // parameter breakdown
  calculated_at: timestamp,
  is_valid: boolean
}
```

### 7. `compliance_flags`
```typescript
{
  flag_id: string (auto-generated),
  batch_id: string,
  institution_id: string,
  department_id: string,
  academic_year: string,
  severity: string, // "low" | "medium" | "high"
  message: string,
  title: string,
  reason: string,
  recommendation: string?,
  created_at: timestamp
}
```

### 8. `approval_results`
```typescript
{
  result_id: string (auto-generated),
  batch_id: string,
  institution_id: string,
  department_id: string,
  academic_year: string,
  category: string, // "aicte" | "nba" | "naac" | "nirf"
  subtype: string, // "new" | "renewal" | "unknown"
  signals: object?,
  readiness_score: number?,
  created_at: timestamp
}
```

### 9. `trends`
```typescript
{
  trend_id: string (auto-generated),
  institution_id: string,
  department_id: string,
  kpi_name: string,
  year: number,
  value: number,
  calculated_at: timestamp
}
```

### 10. `forecasts`
```typescript
{
  forecast_id: string (auto-generated),
  institution_id: string,
  department_id: string,
  kpi_name: string,
  forecast_year: number,
  predicted_value: number,
  lower_bound: number,
  upper_bound: number,
  confidence: number,
  model_info: object,
  created_at: timestamp
}
```

---

## 🔄 Migration Steps

### Phase 1: Firebase Setup
1. Create Firebase project
2. Enable Firestore
3. Enable Firebase Storage
4. Enable Firebase Authentication
5. Generate service account key
6. Add to Railway environment variables

### Phase 2: Database Layer Refactor
1. Create `backend/config/firestore.py` - Firestore client
2. Create `backend/services/firestore_service.py` - CRUD operations
3. Replace SQLAlchemy queries with Firestore queries
4. Update all routers to use Firestore service

### Phase 3: File Storage Migration
1. Upload files to Firebase Storage instead of local filesystem
2. Update document paths to Firebase Storage URLs
3. Update file upload/download logic

### Phase 4: Authentication Integration
1. Integrate Firebase Auth
2. Add role-based access control
3. Update frontend to use Firebase Auth

### Phase 5: Deployment
1. Deploy backend to Railway
2. Deploy frontend to Vercel
3. Configure environment variables
4. Test end-to-end

---

## 📝 Implementation Files Needed

### Backend
- `backend/config/firestore.py` - Firestore client initialization
- `backend/services/firestore_service.py` - CRUD operations
- `backend/services/storage_service.py` - Firebase Storage operations
- `backend/middleware/auth.py` - Firebase Auth middleware

### Frontend
- `frontend/lib/firebase.ts` - Firebase client initialization
- `frontend/lib/auth.ts` - Authentication helpers
- Update all API calls to include auth tokens

---

## ⚠️ Critical Considerations

1. **Data Migration**: Need script to migrate existing SQLite data to Firestore
2. **Query Performance**: Firestore queries are different from SQL - need indexes
3. **Transactions**: Firestore transactions are different - need careful handling
4. **File Storage**: All files must move to Firebase Storage
5. **Real-time Updates**: Can use Firestore listeners for real-time status

---

## 🚀 Next Steps

1. Create Firestore service layer
2. Update database operations
3. Migrate file storage
4. Test locally
5. Deploy to Railway + Vercel

