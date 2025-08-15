#!/usr/bin/env python3
"""
Debug script to troubleshoot OpenAI API key issues.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def debug_openai_setup():
    """Debug OpenAI API key setup."""
    print("🔍 Debugging OpenAI API Key Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"1. API Key Found: {'✅ Yes' if api_key else '❌ No'}")
    
    if api_key:
        print(f"2. API Key Length: {len(api_key)} characters")
        print(f"3. API Key Starts With: {api_key[:10]}...")
        print(f"4. API Key Ends With: ...{api_key[-4:]}")
        
        # Check for common issues
        if api_key == "your_openai_api_key_here":
            print("❌ Issue: API key is set to placeholder value")
            return False
        
        if api_key.strip() == "":
            print("❌ Issue: API key is empty or only whitespace")
            return False
        
        if not (api_key.startswith("sk-") or api_key.startswith("sk-proj-")):
            print("❌ Issue: API key doesn't start with 'sk-' or 'sk-proj-'")
            return False
        
        # Test OpenAI connection
        print("\n5. Testing OpenAI Connection...")
        try:
            client = OpenAI(api_key=api_key)
            
            # Make a simple test call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'Hello, API is working!'"}
                ],
                max_tokens=20
            )
            
            print("✅ OpenAI API connection successful!")
            print(f"Response: {response.choices[0].message.content}")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI API connection failed: {e}")
            return False
    else:
        print("❌ No API key found in environment variables")
        print("\nTo fix this:")
        print("For local development:")
        print("1. Create a .env file in the project root")
        print("2. Add: OPENAI_API_KEY=your_actual_api_key_here")
        print("3. Make sure the .env file is in the same directory as app.py")
        print("\nFor Hugging Face Spaces:")
        print("1. Go to your repository settings")
        print("2. Navigate to 'Secrets and variables' > 'Actions'")
        print("3. Add a new repository secret named 'OPENAI_API_KEY'")
        print("4. Set the value to your actual OpenAI API key")
        return False

def check_env_file():
    """Check if .env file exists and has correct format."""
    print("\n🔍 Checking .env file...")
    
    env_files = [".env", "env.py", "env_example.py"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ Found: {env_file}")
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if "OPENAI_API_KEY" in content:
                        print(f"   Contains OPENAI_API_KEY: ✅")
                    else:
                        print(f"   Contains OPENAI_API_KEY: ❌")
            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"❌ Not found: {env_file}")
    
    # Check current working directory
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Files in current directory:")
    for file in os.listdir("."):
        if file.endswith(('.env', '.py')) or 'env' in file.lower():
            print(f"  - {file}")

if __name__ == "__main__":
    print("Starting OpenAI API Key Debug...\n")
    
    check_env_file()
    print("\n" + "=" * 50)
    
    success = debug_openai_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OpenAI setup is working correctly!")
    else:
        print("⚠️  Please fix the issues above before running the main application.")
