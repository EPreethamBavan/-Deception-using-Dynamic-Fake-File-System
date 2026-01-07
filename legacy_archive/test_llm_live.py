from LLM_Provider import LLMProvider
import os

# Load env
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

print(f"Testing with API Key: {os.environ.get('GEMINI_API_KEY')[:5]}...")

provider = LLMProvider()
persona_data = {"home_dir": "/home/test_user"}
context = {"monthly_task": "Test LLM Integration", "recent_history": "Login"}

print("Requesting scene from Gemini...")
scene = provider.generate_scene("test_user", persona_data, context)
print("Result:")
print(scene)

if scene['name'] != "Mock Generated Scene":
    print("SUCCESS: Received dynamic response.")
else:
    print("FAILURE: Fallback to mock (Check logs/key).")
