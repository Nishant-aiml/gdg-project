"""
Verify all environment files are correctly set up
"""
import os
from pathlib import Path

def check_frontend_env():
    """Check frontend .env.local"""
    print("=" * 60)
    print("1. FRONTEND ENVIRONMENT (.env.local)")
    print("=" * 60)
    
    frontend_env = Path("frontend/.env.local")
    if not frontend_env.exists():
        print("[FAIL] frontend/.env.local not found")
        return False
    
    with open(frontend_env, 'r') as f:
        content = f.read()
    
    required_vars = [
        "NEXT_PUBLIC_FIREBASE_API_KEY",
        "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN",
        "NEXT_PUBLIC_FIREBASE_PROJECT_ID",
        "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET",
        "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID",
        "NEXT_PUBLIC_FIREBASE_APP_ID",
    ]
    
    missing = []
    for var in required_vars:
        if var not in content:
            missing.append(var)
        else:
            # Check if it has a value
            for line in content.split('\n'):
                if line.startswith(f"{var}="):
                    value = line.split("=", 1)[1].strip()
                    if not value or value == "":
                        missing.append(f"{var} (empty)")
                    else:
                        print(f"[OK] {var}")
                    break
    
    if missing:
        print(f"[FAIL] Missing or empty: {', '.join(missing)}")
        return False
    
    print("[SUCCESS] All Firebase variables configured")
    return True

def check_backend_env():
    """Check backend .env"""
    print("\n" + "=" * 60)
    print("2. BACKEND ENVIRONMENT (.env)")
    print("=" * 60)
    
    root_env = Path(".env")
    if not root_env.exists():
        print("[WARN] Root .env not found (backend will use defaults)")
        return True  # Not critical - SQLite works without it
    
    with open(root_env, 'r') as f:
        content = f.read()
    
    # Check for API keys
    has_openai = "OPENAI_API_KEY" in content and "OPENAI_API_KEY=" in content
    has_gemini = "GEMINI_API_KEY" in content and "GEMINI_API_KEY=" in content
    has_database = "DATABASE_URL" in content and "DATABASE_URL=" in content
    
    if has_openai:
        print("[OK] OPENAI_API_KEY found")
    else:
        print("[WARN] OPENAI_API_KEY not found (optional for chatbot)")
    
    if has_gemini:
        print("[OK] GEMINI_API_KEY found")
    else:
        print("[WARN] GEMINI_API_KEY not found (required for chatbot)")
    
    if has_database:
        print("[OK] DATABASE_URL found (PostgreSQL/Supabase)")
    else:
        print("[INFO] DATABASE_URL not found (will use SQLite - works fine)")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("ENVIRONMENT FILES VERIFICATION")
    print("=" * 60 + "\n")
    
    frontend_ok = check_frontend_env()
    backend_ok = check_backend_env()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if frontend_ok and backend_ok:
        print("[SUCCESS] All environment files are correctly configured!")
        print("\nNext steps:")
        print("1. Test Firebase login: cd frontend && npm run dev")
        print("2. Test backend: cd backend && python -m uvicorn main:app --reload")
        print("3. Optional: Set up Supabase (see SUPABASE_SETUP_DETAILED.md)")
    else:
        print("[WARN] Some issues found. Please review above.")
    
    print()

if __name__ == "__main__":
    main()

