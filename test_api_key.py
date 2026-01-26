import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API Key: {api_key[:5]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

models_to_test = [
    "gemini-2.5-flash", 
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
]

print("\n--- Model Availability Check ---")
for model_name in models_to_test:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"SUCCESS! (Response length: {len(response.text)})")
        print(f"Response Preview: {response.text[:50]}...")
    except Exception as e:
        print(f"FAILED: {str(e)[:100]}...")
