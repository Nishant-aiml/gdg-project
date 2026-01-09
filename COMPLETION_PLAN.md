# 🎯 Platform Completion Plan

## Current Status Audit

### ✅ What EXISTS (Backend)
- Firebase Auth backend endpoints
- Auth middleware (but commented out)
- All 4 modes (AICTE/NBA/NAAC/NIRF) in backend
- KPI details endpoint with evidence
- Invalid batch marking
- Department-wise schema
- Comparison/Trends/Forecast endpoints
- Chatbot with explain_score

### ❌ What's MISSING (Critical)

#### 1. AUTHENTICATION (CRITICAL - NOT OPTIONAL)
- ❌ Frontend login page
- ❌ Frontend auth state management
- ❌ Protected routes in frontend
- ❌ Auth middleware enabled on backend APIs
- ❌ User ownership tracking (user_id, institution_id, department_id)
- ❌ Role-based UI rendering

#### 2. PLATFORM MODEL (CORE FIX)
- ❌ Institution entity/table
- ❌ Department entity/table
- ❌ User-Institution-Department linking
- ❌ Historical data reuse
- ❌ Document versioning

#### 3. MODES (FRONTEND MISSING)
- ❌ Mode selector shows only AICTE/UGC/Mixed
- ❌ Missing NBA/NAAC/NIRF in UI
- ❌ Dynamic KPI cards per mode

#### 4. FRONTEND COMPLETENESS
- ⚠️ KPI drill-down exists but needs verification
- ⚠️ Invalid batch UX needs improvement
- ⚠️ Institution/Department selectors missing
- ⚠️ Year selector missing

---

## Implementation Priority

### Phase 1: Authentication (MANDATORY)
1. Create frontend login page
2. Add Firebase Auth client
3. Add auth state management
4. Add protected route wrapper
5. Enable auth middleware on backend
6. Add user context to all requests

### Phase 2: Platform Model
1. Create Institution/Department tables
2. Link users to institutions/departments
3. Add user_id to batches
4. Implement data filtering by user

### Phase 3: Mode Selector
1. Update homepage to show all 4 modes
2. Make KPI cards dynamic per mode
3. Add mode-specific explanations

### Phase 4: Frontend Polish
1. Add Institution/Department selectors
2. Improve invalid batch UX
3. Verify all features work end-to-end

---

## Files to Create/Modify

### Frontend (NEW)
- `frontend/app/login/page.tsx` - Login page
- `frontend/lib/auth.ts` - Auth utilities
- `frontend/components/AuthProvider.tsx` - Auth context
- `frontend/components/ProtectedRoute.tsx` - Route protection
- `frontend/lib/firebase.ts` - Firebase client init

### Frontend (MODIFY)
- `frontend/app/page.tsx` - Add all 4 modes
- `frontend/app/dashboard/page.tsx` - Add auth checks, institution/dept selectors
- `frontend/lib/api.ts` - Add auth headers to all requests

### Backend (MODIFY)
- `backend/main.py` - Enable auth middleware
- `backend/config/database.py` - Add Institution/Department/User tables
- `backend/routers/*` - Add auth dependencies to all endpoints

---

## Acceptance Criteria

✅ User can log in
✅ User can only see their institution/department data
✅ All 4 modes selectable in UI
✅ KPI drill-down shows formula, parameters, weights, evidence
✅ Invalid batches clearly marked with reasons
✅ Comparison uses only valid batches
✅ Trends show department-wise history
✅ Chatbot grounded to backend only
✅ No dummy data anywhere
✅ Full user journey works end-to-end

