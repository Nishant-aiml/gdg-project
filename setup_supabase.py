"""
Quick Supabase Setup Helper Script
Helps you set up Supabase connection
"""

import os
import sys
from pathlib import Path

def check_psycopg2():
    """Check if psycopg2-binary is installed"""
    try:
        import psycopg2
        print("[OK] psycopg2-binary is installed")
        return True
    except ImportError:
        print("[FAIL] psycopg2-binary is not installed")
        print("   Install it with: pip install psycopg2-binary")
        return False

def check_env_file():
    """Check if .env file exists and has DATABASE_URL"""
    backend_dir = Path(__file__).parent / "backend"
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("[FAIL] .env file not found in backend folder")
        print(f"   Create it at: {env_file}")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "DATABASE_URL" in content:
            # Check if it's not empty
            for line in content.split('\n'):
                if line.startswith("DATABASE_URL="):
                    value = line.split("=", 1)[1].strip()
                    if value and value != "":
                        print("[OK] DATABASE_URL found in .env file")
                        return True
            print("[WARN] DATABASE_URL is empty in .env file")
            return False
        else:
            print("[FAIL] DATABASE_URL not found in .env file")
            return False

def test_connection():
    """Test database connection"""
    try:
        from config.database import engine
        # Try to connect
        with engine.connect() as conn:
            print("[OK] Database connection successful!")
            return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in backend/.env")
        print("2. Make sure password is correct (no spaces)")
        print("3. Make sure Supabase project is active")
        return False

def main():
    print("=" * 60)
    print("Supabase Setup Checker")
    print("=" * 60)
    print()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    if backend_dir.exists():
        os.chdir(backend_dir)
        sys.path.insert(0, str(backend_dir))
    else:
        print("[FAIL] Backend directory not found")
        return
    
    print("1. Checking PostgreSQL driver...")
    pg_ok = check_psycopg2()
    print()
    
    print("2. Checking .env file...")
    env_ok = check_env_file()
    print()
    
    if pg_ok and env_ok:
        print("3. Testing database connection...")
        conn_ok = test_connection()
        print()
        
        if conn_ok:
            print("=" * 60)
            print("[SUCCESS] All checks passed! Supabase is ready to use.")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Initialize tables: python -c 'from config.database import init_db; init_db()'")
            print("2. Start backend: python -m uvicorn main:app --reload")
        else:
            print("=" * 60)
            print("[FAIL] Connection test failed. Please fix the issues above.")
            print("=" * 60)
    else:
        print("=" * 60)
        print("[WARN] Please fix the issues above before testing connection.")
        print("=" * 60)
        print("\nQuick setup:")
        print("1. Install: pip install psycopg2-binary")
        print("2. Create backend/.env file")
        print("3. Add: DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres")

if __name__ == "__main__":
    main()

