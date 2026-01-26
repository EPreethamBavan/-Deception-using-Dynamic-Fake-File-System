#!/usr/bin/env python3
"""
Test LLM Connection
Tests connection to Google Gemini API
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_llm_connection():
    """Test LLM API connection"""

    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Try to load from .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break

    if not api_key:
        print("⚠️  WARNING: No GEMINI_API_KEY found in environment or config/.env")
        print("   Set GEMINI_API_KEY environment variable or add to config/.env to run this test")
        return

    # Set the API key
    os.environ['GEMINI_API_KEY'] = api_key

    try:
        from LLM_Provider import LLMProvider

        provider = LLMProvider()

        # Test simple generation
        prompt = """You are a senior developer. Generate a single realistic bash command
that you would run while working on a Python backend project.
Output only the command, nothing else."""

        print("=== Testing LLM Connection ===")
        print(f"Prompt: {prompt}")

        response = provider.generate(prompt)
        print(f"LLM Response: {response}")

        # Verify response looks like a command
        assert response, "Empty response from LLM"
        assert len(response) < 500, f"Response too long ({len(response)} chars) - not a command"
        assert not response.startswith(" "), f"Response starts with space: '{response}'"
        assert not response.endswith(" "), f"Response ends with space: '{response}'"

        # Should look like a command (contain common command patterns)
        command_indicators = ['git', 'python', 'pip', 'cd', 'ls', 'vim', 'nano', 'mkdir', 'rm', 'cp', 'mv']
        has_command_indicator = any(indicator in response.lower() for indicator in command_indicators)

        if has_command_indicator:
            print("✓ PASS: Response looks like a realistic command")
        else:
            print(f"⚠️  WARNING: Response may not be a typical command: '{response}'")

        print("✓ PASS: LLM connection working")

    except ImportError as e:
        print(f"✗ FAIL: Import error: {e}")
        print("   Make sure google-generativeai is installed: pip install google-generativeai")
        raise
    except Exception as e:
        print(f"✗ FAIL: LLM connection error: {e}")
        print("   Check your GEMINI_API_KEY and internet connection")
        raise

if __name__ == "__main__":
    print("🧪 Testing LLM Connection\n")
    test_llm_connection()
    print("\n🎉 LLM connection test passed!")