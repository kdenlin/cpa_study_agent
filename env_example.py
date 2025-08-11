"""
Example of how to load and use environment variables in your CPA Study Agent project.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def setup_openai_client():
    """Set up OpenAI client using environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return None
    
    print("✅ OpenAI API key loaded successfully")
    
    # Create OpenAI client
    client = OpenAI(api_key=api_key)
    return client

def example_usage():
    """Example of how to use the OpenAI client."""
    client = setup_openai_client()
    
    if client is None:
        print("Cannot proceed without API key")
        return
    
    # Example: Get available models
    try:
        models = client.models.list()
        print(f"Available models: {len(models.data)} models found")
    except Exception as e:
        print(f"Error accessing OpenAI API: {e}")

if __name__ == "__main__":
    example_usage() 