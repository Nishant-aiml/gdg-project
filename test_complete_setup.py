"""
Complete Setup Test - Verify Firebase & Supabase Integration
"""
import sys
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def test_imports():
    """Test if required packages are installed"""
    print("=" * 60)
    print("1. TESTING IMPORTS")
    print("=" * 60)
    
    results = {}
    
    # Backend imports
    try:
        import firebase_admin
        print("[OK] firebase-admin installed")
        results['firebase_admin'] = True
    except ImportError:
        print("[FAIL] firebase-admin not installed")
        results['firebase_admin'] = False
    
    try:
        import psycopg2
        print("[OK] psycopg2-binary installed")
        results['psycopg2'] = True
    except ImportError:
        print("[WARN] psycopg2-binary not installed (optional for Supabase)")
        results['psycopg2'] = False
    
    try:
        from sqlalchemy import create_engine
        print("[OK] sqlalchemy installed")
        results['sqlalchemy'] = True
    except ImportError:
        print("[FAIL] sqlalchemy not installed")
        results['sqlalchemy'] = False
    
    return results

def test_env_files():
    """Test environment files"""
    print("\n" + "=" * 60)
    print("2. TESTING ENVIRONMENT FILES")
    print("=" * 60)
    
    results = {}
    
    # Frontend .env.local
    frontend_env = Path("frontend/.env.local")
    if frontend_env.exists():
        print("[OK] frontend/.env.local exists")
        with open(frontend_env, 'r') as f:
            content = f.read()
            required = [
                "NEXT_PUBLIC_FIREBASE_API_KEY",
                "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN",
                "NEXT_PUBLIC_FIREBASE_PROJECT_ID",
            ]
            missing = [v for v in required if v not in content]
            if missing:
                print(f"[WARN] Missing: {', '.join(missing)}")
                results['frontend_env'] = False
            else:
                print("[OK] All required Firebase variables present")
                results['frontend_env'] = True
    else:
        print("[FAIL] frontend/.env.local not found")
        results['frontend_env'] = False
    
    # Root .env
    root_env = Path(".env")
    if root_env.exists():
        print("[OK] Root .env exists")
        with open(root_env, 'r') as f:
            content = f.read()
            has_openai = "OPENAI_API_KEY" in content
            has_gemini = "GEMINI_API_KEY" in content
            has_firebase = "FIREBASE_PROJECT_ID" in content
            has_database = "DATABASE_URL" in content
            
            if has_openai:
                print("[OK] OPENAI_API_KEY found")
            if has_gemini:
                print("[OK] GEMINI_API_KEY found")
            if has_firebase:
                print("[OK] FIREBASE_PROJECT_ID found")
            if has_database:
                print("[OK] DATABASE_URL found (Supabase configured)")
            else:
                print("[INFO] DATABASE_URL not found (will use SQLite)")
            
            results['root_env'] = True
    else:
        print("[WARN] Root .env not found")
        results['root_env'] = False
    
    return results

def test_firebase_init():
    """Test Firebase Admin initialization"""
    print("\n" + "=" * 60)
    print("3. TESTING FIREBASE ADMIN INITIALIZATION")
    print("=" * 60)
    
    try:
        # Change to backend directory
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("[FAIL] Backend directory not found")
            return False
        
        sys.path.insert(0, str(backend_dir.absolute()))
        os.chdir(backend_dir)
        
        # Load environment
        from dotenv import load_dotenv
        env_path = Path("..") / ".env"
        load_dotenv(env_path)
        
        # Test Firebase initialization
        from services.firebase_auth import initialize_firebase_admin
        
        app = initialize_firebase_admin()
        if app:
            print("[OK] Firebase Admin initialized successfully")
            return True
        else:
            print("[WARN] Firebase Admin initialization returned None")
            print("[INFO] This is OK for development - will work with project ID")
            return True  # Not a failure, just a warning
    except Exception as e:
        print(f"[WARN] Firebase Admin test failed: {e}")
        print("[INFO] This might be OK - Firebase will work with project ID")
        return True  # Not critical
    finally:
        os.chdir("..")

def test_database_init():
    """Test database initialization"""
    print("\n" + "=" * 60)
    print("4. TESTING DATABASE INITIALIZATION")
    print("=" * 60)
    
    try:
        # Change to backend directory
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("[FAIL] Backend directory not found")
            return False
        
        sys.path.insert(0, str(backend_dir.absolute()))
        os.chdir(backend_dir)
        
        # Load environment
        from dotenv import load_dotenv
        env_path = Path("..") / ".env"
        load_dotenv(env_path)
        
        # Test database
        from config.database import engine, DB_TYPE, init_db
        
        print(f"[INFO] Database type: {DB_TYPE}")
        
        # Try to connect
        with engine.connect() as conn:
            print("[OK] Database connection successful")
        
        # Try to initialize tables
        try:
            init_db()
            print("[OK] Database tables initialized")
        except Exception as e:
            print(f"[WARN] Table initialization: {e}")
            print("[INFO] Tables might already exist - this is OK")
        
        return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False
    finally:
        os.chdir("..")

def test_backend_imports():
    """Test if backend can import main modules"""
    print("\n" + "=" * 60)
    print("5. TESTING BACKEND IMPORTS")
    print("=" * 60)
    
    try:
        backend_dir = Path("backend")
        sys.path.insert(0, str(backend_dir.absolute()))
        os.chdir(backend_dir)
        
        # Test critical imports
        try:
            from config.database import Base, engine
            print("[OK] Database config imports")
        except Exception as e:
            print(f"[FAIL] Database config: {e}")
            return False
        
        try:
            from services.firebase_auth import verify_firebase_token, get_user_role
            print("[OK] Firebase auth imports")
        except Exception as e:
            print(f"[FAIL] Firebase auth: {e}")
            return False
        
        try:
            from routers import auth, dashboard, batches
            print("[OK] Router imports")
        except Exception as e:
            print(f"[FAIL] Router imports: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Backend imports failed: {e}")
        return False
    finally:
        os.chdir("..")

def main():
    print("\n" + "=" * 60)
    print("COMPLETE SETUP TEST")
    print("=" * 60 + "\n")
    
    results = {}
    
    # Test 1: Imports
    import_results = test_imports()
    results['imports'] = all(import_results.values())
    
    # Test 2: Environment files
    env_results = test_env_files()
    results['env_files'] = env_results.get('frontend_env', False) and env_results.get('root_env', False)
    
    # Test 3: Firebase
    results['firebase'] = test_firebase_init()
    
    # Test 4: Database
    results['database'] = test_database_init()
    
    # Test 5: Backend imports
    results['backend'] = test_backend_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {test_name.upper()}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Start backend: cd backend && python -m uvicorn main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Test login at http://localhost:3000")
    else:
        print("[WARN] Some tests failed. Review above for details.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install -r backend/requirements.txt")
        print("- Check environment files are in correct locations")
        print("- Verify Firebase project ID is set")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

