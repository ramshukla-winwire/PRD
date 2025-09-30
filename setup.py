#!/usr/bin/env python3
"""
Setup script for Groq BRD Generator - Hackathon Version
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def check_groq_key():
    """Check if Groq API key is set"""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️  GROQ_API_KEY environment variable not set")
        print("📝 Please set your Groq API key:")
        print("   export GROQ_API_KEY='your_api_key_here'")
        print("🌐 Get your API key at: https://console.groq.com/")
        return False
    
    print("✅ GROQ_API_KEY is set")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "PRDAgent/data",
        "PRDAgent/templates/user_generated"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting BRD Generator...")
    print("🌐 Opening http://localhost:8501")
    
    try:
        os.chdir("PRDAgent")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main setup function"""
    print("🚀 Groq BRD Generator - Hackathon Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Check Groq API key
    has_key = check_groq_key()
    
    if not has_key:
        print("\\n⚠️  Please set your GROQ_API_KEY and run the script again")
        sys.exit(1)
    
    print("\\n✅ Setup complete!")
    print("🎯 Ready to generate lightning-fast BRDs with Groq!")
    
    # Ask if user wants to start the app
    response = input("\\n🚀 Start the application now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        run_application()
    else:
        print("\\n📝 To start later, run: streamlit run PRDAgent/streamlit_app.py")

if __name__ == "__main__":
    main()
