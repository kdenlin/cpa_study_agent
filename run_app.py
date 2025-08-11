#!/usr/bin/env python3
"""
Startup script for the CPA Study Assistant web application.
"""

import os
import sys
from dotenv import load_dotenv

def check_setup():
    """Check if the application is properly set up."""
    print("🔍 Checking application setup...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured!")
        print("Please update your .env file with your actual API key.")
        return False
    
    print("✅ OpenAI API key configured")
    
    # Check if required directories exist
    required_dirs = ['data/questions', 'app/db/chroma_db_test', 'templates']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"⚠️  Directory {dir_path} not found - creating it...")
            os.makedirs(dir_path, exist_ok=True)
    
    print("✅ All required directories exist")
    return True

def main():
    """Main startup function."""
    print("🎓 CPA Study Assistant")
    print("=" * 50)
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        sys.exit(1)
    
    print("\n✅ Setup complete! Starting the application...")
    print("\n🌐 The application will be available at: http://localhost:5000")
    print("📱 You can access it from any device on your network")
    print("\n💡 Tips:")
    print("   - Press Ctrl+C to stop the application")
    print("   - Make sure your OpenAI API key is valid")
    print("   - Check that your practice questions are in data/questions/")
    print("\n" + "=" * 50)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 