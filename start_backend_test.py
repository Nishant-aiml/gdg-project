"""Start backend and run tests"""
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def start_backend():
    """Start backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("Starting backend server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    print("Waiting for backend to start...")
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("✓ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"  Waiting... ({i+1}/{max_wait})")
    return False

def run_tests():
    """Run test suite"""
    os.chdir(Path(__file__).parent)
    print("\nRunning test suite...")
    result = subprocess.run([sys.executable, "test_frontend_backend_connections.py"])
    return result.returncode

if __name__ == "__main__":
    try:
        # Start backend
        backend_process = start_backend()
        
        # Wait for backend
        if not wait_for_backend():
            print("✗ Backend did not start in time")
            backend_process.terminate()
            sys.exit(1)
        
        # Run tests
        test_result = run_tests()
        
        # Cleanup
        backend_process.terminate()
        
        sys.exit(test_result)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        if 'backend_process' in locals():
            backend_process.terminate()
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        if 'backend_process' in locals():
            backend_process.terminate()
        sys.exit(1)

