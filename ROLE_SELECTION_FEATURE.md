# ✅ Role Selection Feature Added

## 🎯 Feature Overview

Users can now select their role (Department or Institution) during sign up. The selected role is stored as a Firebase custom claim and determines which features are available to the user.

---

## ✅ Changes Made

### 1. **Sign Up Page** (`frontend/app/signup/page.tsx`)
- ✅ Added role selection UI with two options:
  - **Department**: Single department access
  - **Institution**: All departments access
- ✅ Role selection buttons with visual feedback
- ✅ Role is passed to sign-up functions

### 2. **Authentication Functions** (`frontend/lib/auth.ts`)
- ✅ `signUpWithEmail()` now accepts `role` parameter
- ✅ `signInWithGoogle()` now accepts optional `role` parameter
- ✅ Both functions call `/auth/set-role` endpoint to set Firebase custom claims
- ✅ Fresh token is retrieved after role is set to include custom claims

### 3. **Backend Endpoint** (`backend/routers/auth.py`)
- ✅ Added `/auth/set-role` POST endpoint
- ✅ Validates role ('department' or 'institution')
- ✅ Sets Firebase custom claims via `set_user_role()`

### 4. **Firebase Auth Service** (`backend/services/firebase_auth.py`)
- ✅ Added `set_user_role()` function to set custom claims
- ✅ Updated `verify_firebase_token()` to extract custom claims from token
- ✅ Updated `get_user_role()` to check custom claims first (root level)
- ✅ Falls back to email domain if no custom claims found

---

## 🔐 Role-Based Features

### **Department Users**
- ✅ Single department access
- ✅ Can create batches for their department
- ✅ Can view their department's evaluations
- ✅ Can compare batches
- ✅ Can view trends
- ❌ **No Forecast access** (hidden in navbar)
- ❌ **No Dashboard access** (institution-only)

### **Institution Users**
- ✅ All departments access
- ✅ Can view all departments' evaluations
- ✅ Can filter by department in EvaluationSelector
- ✅ **Dashboard access** (institution-only navigation item)
- ✅ Can access Forecast page
- ✅ Can compare across departments
- ✅ Can view trends across departments

---

## 🎨 UI Changes

### Sign Up Page
- Added role selection section with two cards:
  - **Department Card**: Shows "Single department access"
  - **Institution Card**: Shows "All departments access"
- Cards are clickable and show selected state
- Icons: Users (department) and Building2 (institution)

---

## 🔄 How It Works

1. **User Signs Up:**
   - User selects role (Department or Institution)
   - User creates account (email/password or Google)
   - Frontend calls `/auth/set-role` with selected role
   - Backend sets Firebase custom claim `{role: 'department' | 'institution'}`

2. **User Logs In:**
   - Backend verifies Firebase token
   - Backend reads custom claim from token
   - Role is returned to frontend
   - Frontend filters features based on role

3. **Feature Access:**
   - Navbar filters navigation items based on role
   - ProtectedRoute component enforces role requirements
   - EvaluationSelector shows department filter for institution users

---

## 📋 Role-Based Feature Matrix

| Feature | Department | Institution |
|---------|-----------|-------------|
| Create Batch | ✅ | ✅ |
| Upload Documents | ✅ | ✅ |
| View Dashboard | ❌ | ✅ |
| Compare Batches | ✅ | ✅ |
| View Trends | ✅ | ✅ |
| View Forecast | ❌ | ✅ |
| Filter by Department | ❌ | ✅ |
| View All Departments | ❌ | ✅ |

---

## 🧪 Testing

### Test Sign Up with Role Selection:
1. Go to `/signup`
2. Select role (Department or Institution)
3. Create account
4. Verify role is set correctly
5. Check navbar for role-appropriate features

### Test Role-Based Features:
1. **Department User:**
   - Should NOT see "Forecast" in navbar
   - Should NOT see "Dashboard" in navbar
   - Should only see their department's evaluations

2. **Institution User:**
   - Should see "Forecast" in navbar
   - Should see "Dashboard" in navbar
   - Should see department filter in EvaluationSelector
   - Should see all departments' evaluations

---

## ✅ Summary

- ✅ Role selection added to signup page
- ✅ Backend endpoint to set roles via Firebase custom claims
- ✅ Role-based feature filtering implemented
- ✅ Department users: Limited access (no Forecast, no Dashboard)
- ✅ Institution users: Full access (all features)

**Users can now choose their role during sign up, and features are automatically filtered based on their role! 🎉**

