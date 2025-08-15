#!/usr/bin/env python3
"""
Hugging Face Spaces Configuration
This file helps with environment variable setup for Hugging Face Spaces deployment.
"""

import os
from dotenv import load_dotenv

def setup_huggingface_environment():
    """
    Set up environment variables for Hugging Face Spaces deployment.
    This function ensures that the OpenAI API key is properly configured.
    """
    # Load environment variables from .env file (for local development)
    load_dotenv()
    
    # Check if we're running on Hugging Face Spaces
    is_huggingface = os.getenv('SPACE_ID') is not None
    
    if is_huggingface:
        print("🚀 Running on Hugging Face Spaces")
        
        # On Hugging Face Spaces, environment variables should be available
        # through the secrets configuration
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            print("✅ OpenAI API key found in Hugging Face Spaces environment")
            print(f"   Key starts with: {api_key[:10]}...")
            print(f"   Key length: {len(api_key)} characters")
            
            # Validate the key format
            if api_key.startswith("sk-") or api_key.startswith("sk-proj-"):
                print("✅ API key format is valid")
                return True
            else:
                print("❌ API key format is invalid")
                print("   Expected to start with 'sk-' or 'sk-proj-'")
                return False
        else:
            print("❌ OpenAI API key not found in Hugging Face Spaces environment")
            print("💡 Make sure to add OPENAI_API_KEY to your repository secrets:")
            print("   1. Go to your repository settings")
            print("   2. Navigate to 'Secrets and variables' > 'Actions'")
            print("   3. Add a new repository secret named 'OPENAI_API_KEY'")
            print("   4. Set the value to your actual OpenAI API key")
            return False
    else:
        print("🏠 Running locally")
        
        # For local development, check for .env file
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            print("✅ OpenAI API key found in local environment")
            return True
        else:
            print("❌ OpenAI API key not found in local environment")
            print("💡 Create a .env file with: OPENAI_API_KEY=your_actual_api_key_here")
            return False

def get_environment_info():
    """
    Get information about the current environment for debugging.
    """
    info = {
        'space_id': os.getenv('SPACE_ID'),
        'space_title': os.getenv('SPACE_TITLE'),
        'space_host': os.getenv('SPACE_HOST'),
        'space_author': os.getenv('SPACE_AUTHOR'),
        'is_huggingface': os.getenv('SPACE_ID') is not None,
        'api_key_present': os.getenv('OPENAI_API_KEY') is not None,
        'api_key_length': len(os.getenv('OPENAI_API_KEY', '')),
        'api_key_prefix': os.getenv('OPENAI_API_KEY', '')[:10] if os.getenv('OPENAI_API_KEY') else None
    }
    
    print("🔍 Environment Information:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    return info

if __name__ == "__main__":
    print("🔧 Hugging Face Spaces Configuration Check")
    print("=" * 50)
    
    get_environment_info()
    print("\n" + "=" * 50)
    
    success = setup_huggingface_environment()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Environment is properly configured!")
    else:
        print("⚠️  Please fix the configuration issues above.")
