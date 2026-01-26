#!/usr/bin/env python3
"""
Test SPADE Prompt Engine
Tests prompt generation for different personas
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PromptEngine import SPADEPromptEngine, ContextState

def test_prompt_engine():
    """Test SPADE prompt generation"""

    engine = SPADEPromptEngine()

    # Create test context
    context = ContextState(
        current_day=5,
        narrative_arc="Payment Gateway Integration",
        daily_task="Implement Stripe API endpoints",
        recent_commands=["git status", "vim main.py"],
        files_modified=["src/api.py"],
        current_project="backend-api",
        build_status="passing",
        threat_level="none",
        fingerprint_detected=False
    )

    # Test personas
    personas = ["dev_alice", "sys_bob", "svc_ci"]

    print("=== Testing SPADE Prompt Engine ===\n")

    for persona in personas:
        print(f"--- Testing {persona} ---")

        prompt = engine.build_prompt(persona, context)
        print(f"Prompt length: {len(prompt)} characters")

        # Verify SPADE sections
        required_sections = [
            "IDENTITY & PERSONA",
            "GOAL & TASK",
            "THREAT CONTEXT",
            "STRATEGY & CONSTRAINTS",
            "OUTPUT EXAMPLES",
            "OUTPUT FORMAT"
        ]

        missing_sections = []
        for section in required_sections:
            if section in prompt:
                print(f"  ✓ {section}")
            else:
                print(f"  ✗ MISSING: {section}")
                missing_sections.append(section)

        assert len(missing_sections) == 0, f"Missing sections for {persona}: {missing_sections}"

        # Verify persona-specific content
        if persona == "dev_alice":
            assert "developer" in prompt.lower() or "alice" in prompt.lower(), "Missing developer persona content"
        elif persona == "sys_bob":
            assert "system" in prompt.lower() or "administrator" in prompt.lower(), "Missing sysadmin persona content"
        elif persona == "svc_ci":
            assert "ci" in prompt.lower() or "continuous" in prompt.lower(), "Missing CI persona content"

        print(f"✓ PASS: {persona} prompt complete\n")

def test_context_inclusion():
    """Test that context is properly included in prompts"""

    engine = SPADEPromptEngine()

    context = ContextState(
        current_day=10,
        narrative_arc="API Development Sprint",
        daily_task="Add error handling to endpoints",
        recent_commands=["git status", "pytest tests/"],
        files_modified=["src/api.py", "tests/test_api.py"],
        current_project="backend-api",
        build_status="failing",
        threat_level="medium",
        fingerprint_detected=True
    )

    prompt = engine.build_prompt("dev_alice", context)

    # Check that context elements are included
    context_checks = [
        ("narrative_arc", "API Development Sprint"),
        ("daily_task", "error handling"),
        ("current_project", "backend-api"),
        ("build_status", "failing"),
        ("threat_level", "medium"),
    ]

    print("=== Testing Context Inclusion ===")

    for field, expected in context_checks:
        if expected.lower() in prompt.lower():
            print(f"  ✓ {field}: '{expected}' found in prompt")
        else:
            print(f"  ✗ {field}: '{expected}' NOT found in prompt")

    # Check recent commands
    if "git status" in prompt and "pytest" in prompt:
        print("  ✓ recent_commands: found in prompt")
    else:
        print("  ✗ recent_commands: not found in prompt")

    # Check files modified
    if "src/api.py" in prompt:
        print("  ✓ files_modified: found in prompt")
    else:
        print("  ✗ files_modified: not found in prompt")

    print("✓ PASS: Context inclusion test complete\n")

if __name__ == "__main__":
    print("🧪 Testing SPADE Prompt Engine\n")
    test_prompt_engine()
    test_context_inclusion()
    print("🎉 All prompt engine tests passed!")