"""
Test script to verify OpenAI setup is working correctly.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_setup():
    """Test that OpenAI API key is loaded and can connect."""
    print("Testing OpenAI setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: Please update your .env file with your actual OpenAI API key")
        print("Current value:", api_key)
        return False
    
    print("✅ API key loaded successfully")
    
    # Test OpenAI connection
    try:
        client = OpenAI(api_key=api_key)
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, OpenAI is working!'"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API connection successful!")
        print("Response:", response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_setup()
    if success:
        print("\n🎉 Everything is set up correctly! You can now use your RAG scripts with OpenAI.")
    else:
        print("\n⚠️  Please fix the issues above before using the RAG scripts.") 