"""Quick start script for running the API without installing dependencies."""

import sys
import subprocess
import os


def main():
    """Run the FastAPI application."""
    print("=" * 60)
    print("FPL Optimizer API - Quick Start")
    print("=" * 60)

    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n⚠️  No .env file found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file. Please update with your settings.")
        else:
            print("❌ .env.example not found. Please create .env manually.")
            sys.exit(1)

    print("\n📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies installed")
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")

    print("\n🚀 Starting FPL Optimizer API...")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n💡 Press Ctrl+C to stop the server\n")

    # Run the application
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
