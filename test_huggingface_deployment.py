#!/usr/bin/env python3
"""
Test script for Hugging Face Spaces deployment
This script helps verify that your OpenAI API key is properly configured.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_setup():
    """Test the environment setup for Hugging Face Spaces."""
    print("🧪 Testing Hugging Face Spaces Environment Setup")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if we're on Hugging Face Spaces
    space_id = os.getenv('SPACE_ID')
    is_huggingface = space_id is not None
    
    print(f"Environment: {'Hugging Face Spaces' if is_huggingface else 'Local Development'}")
    if is_huggingface:
        print(f"Space ID: {space_id}")
        print(f"Space Title: {os.getenv('SPACE_TITLE', 'Unknown')}")
        print(f"Space Host: {os.getenv('SPACE_HOST', 'Unknown')}")
    
    print("\n" + "-" * 60)
    
    # Test API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        print("\n💡 To fix this:")
        if is_huggingface:
            print("1. Go to your Hugging Face repository settings")
            print("2. Navigate to 'Secrets and variables' > 'Actions'")
            print("3. Add a new repository secret:")
            print("   - Name: OPENAI_API_KEY")
            print("   - Value: your_actual_openai_api_key")
            print("4. Wait 2-3 minutes for redeployment")
        else:
            print("1. Create a .env file in the project root")
            print("2. Add: OPENAI_API_KEY=your_actual_api_key_here")
        return False
    
    print(f"✅ OPENAI_API_KEY found")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    
    # Validate key format
    if api_key.startswith("sk-") or api_key.startswith("sk-proj-"):
        print("✅ API key format is valid")
    else:
        print("❌ API key format is invalid")
        print("   Expected to start with 'sk-' or 'sk-proj-'")
        return False
    
    # Test OpenAI connection
    print("\n" + "-" * 60)
    print("Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from Hugging Face Spaces!' if this is working."}
            ],
            max_tokens=20
        )
        
        print("✅ OpenAI API connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("\n💡 Possible issues:")
        print("1. API key is invalid or expired")
        print("2. Insufficient credits in your OpenAI account")
        print("3. Network connectivity issues")
        return False

def test_app_imports():
    """Test that all required modules can be imported."""
    print("\n" + "=" * 60)
    print("Testing application imports...")
    
    required_modules = [
        'flask',
        'openai',
        'chromadb',
        'pdfplumber',
        'dotenv'
    ]
    
    all_good = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("🚀 Hugging Face Spaces Deployment Test")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_app_imports()
    
    # Test environment
    env_ok = test_environment_setup()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    
    if imports_ok and env_ok:
        print("\n🎉 All tests passed! Your deployment should work correctly.")
        print("💡 If you're still having issues, check the Hugging Face Spaces logs.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
