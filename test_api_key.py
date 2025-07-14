from langchain_xai import ChatXAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("XAI_API_KEY")

print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    chat = ChatXAI(
        api_key=api_key,
        model="grok-2-vision-1212",
        temperature=0.2
    )
    
    response = chat.invoke([{"role": "user", "content": "Hello, this is a test"}])
    print("API key works!")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"Error: {e}")