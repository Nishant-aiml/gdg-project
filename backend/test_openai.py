"""Quick test of OpenAI API connectivity."""
import os
from openai import OpenAI
import time

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Try loading from .env
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

print(f"API Key present: {'Yes' if api_key else 'No'}")
print(f"API Key prefix: {api_key[:8]}..." if api_key else "N/A")

# Test API call
client = OpenAI(api_key=api_key)
print("\nTesting OpenAI API...")

try:
    start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Fast model for testing
        messages=[
            {"role": "user", "content": "Say hello in 5 words."}
        ],
        timeout=30
    )
    elapsed = time.time() - start
    print(f"✅ API call succeeded in {elapsed:.2f}s")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API call failed: {e}")
    import traceback
    traceback.print_exc()
