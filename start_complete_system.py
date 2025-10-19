"""
Complete Math Routing Agent System Startup Script
Starts both backend and frontend with all advanced features.
"""

import subprocess
import sys
import time
import threading
import requests
from pathlib import Path

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server."""
    print("🚀 Starting Math Routing Agent Backend...")
    print("   Features: Knowledge Base, Web Search, Human-in-the-Loop Learning")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.main_full:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")

def start_frontend():
    """Start the frontend server."""
    print("🌐 Starting Math Routing Agent Frontend...")
    print("   URL: http://localhost:3000")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        print("Run: python setup_frontend.py")
        return
    
    try:
        subprocess.run(["npm", "start"], cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")

def wait_for_backend():
    """Wait for backend to be ready."""
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_backend():
            print("✅ Backend is ready!")
            return True
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ Backend failed to start within 30 seconds")
    return False

def run_tests():
    """Run system tests."""
    print("\n🧪 Running system tests...")
    try:
        result = subprocess.run([
            sys.executable, "test_advanced_system.py"
        ], input="\n", text=True, capture_output=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("⚠️  Some tests failed, but system is running")
    except Exception as e:
        print(f"⚠️  Test execution failed: {e}")

def main():
    """Main function."""
    print("🎯 Math Routing Agent - Complete System")
    print("=" * 50)
    
    # Check if backend is already running
    if check_backend():
        print("✅ Backend is already running!")
    else:
        print("🚀 Starting backend...")
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        if not wait_for_backend():
            print("❌ Failed to start backend")
            sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Check if frontend should be started
    if len(sys.argv) > 1 and sys.argv[1] == "frontend":
        print("\n🌐 Starting frontend...")
        start_frontend()
    else:
        print("\n🎉 Backend is running successfully!")
        print("\n📚 Available Features:")
        print("   ✅ Knowledge Base Routing")
        print("   ✅ Web Search Routing") 
        print("   ✅ Human-in-the-Loop Feedback")
        print("   ✅ Learning Analytics")
        print("   ✅ Advanced Math Problem Solving")
        
        print("\n🌐 Access Points:")
        print("   📖 API Documentation: http://localhost:8000/docs")
        print("   🔍 Interactive API: http://localhost:8000")
        print("   📊 Health Check: http://localhost:8000/health")
        
        print("\n🚀 To start frontend:")
        print("   python start_complete_system.py frontend")
        print("\n   Or manually:")
        print("   cd frontend && npm start")
        
        print("\n🛑 Press Ctrl+C to stop the backend")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
        sys.exit(0)
