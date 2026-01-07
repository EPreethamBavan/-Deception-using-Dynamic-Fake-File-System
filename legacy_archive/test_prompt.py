import sys
import os
import json

# Add current directory to path so we can import LLM_Provider
sys.path.append(os.getcwd())

from LLM_Provider import LLMProvider

def test_prompt_construction():
    provider = LLMProvider(api_key="TEST_KEY", model_name="mock-model")
    
    # Mock Data
    persona_name = "dev_alice"
    persona_data = {"home_dir": "/home/alice", "work_hours": [9, 17]}
    
    # Mock Context
    context = {
        "monthly_plan": {
            "narrative_arc": "Migrate to Cloud Native Architecture",
            "current_day": "15",
            "daily_task": "Containerize the payment service"
        },
        "recent_history": "Edited Dockerfile"
    }
    
    print("--- GENERATING PROMPT ---")
    prompt = provider._construct_prompt(persona_name, persona_data, context)
    print(prompt)
    print("-------------------------")

if __name__ == "__main__":
    test_prompt_construction()
