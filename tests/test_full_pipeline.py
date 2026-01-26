#!/usr/bin/env python3
"""
Test Full Pipeline
Tests the complete generation pipeline from context to command
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_full_pipeline():
    """Test the complete generation pipeline"""

    print("=== Full Pipeline Test ===\n")

    # Set config directory
    os.environ['CONFIG_DIR'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')

    # 1. Initialize components
    print("1. Initializing components...")
    try:
        from PromptEngine import SPADEPromptEngine, ContextState
        from LLM_Provider import LLMProvider
        from AntiFingerprint import AntiFingerprintManager, AttackerBehaviorDetector

        prompt_engine = SPADEPromptEngine()
        llm_provider = LLMProvider()
        anti_fp = AntiFingerprintManager()
        detector = AttackerBehaviorDetector()
        print("   ✓ Components initialized\n")
    except ImportError as e:
        print(f"   ✗ FAIL: Import error: {e}")
        raise

    # 2. Create context
    print("2. Creating context...")
    context = ContextState(
        current_day=10,
        narrative_arc="API Development Sprint",
        daily_task="Add error handling to endpoints",
        recent_commands=["git status", "pytest tests/"],
        files_modified=["src/api.py"],
        current_project="backend-api",
        build_status="passing",
        threat_level="none",
        fingerprint_detected=False
    )
    print("   ✓ Context created\n")

    # 3. Generate prompt
    print("3. Generating SPADE prompt for dev_alice...")
    try:
        prompt = prompt_engine.build_prompt("dev_alice", context)
        print(f"   ✓ Prompt length: {len(prompt)} characters\n")
    except Exception as e:
        print(f"   ✗ FAIL: Prompt generation error: {e}")
        raise

    # 4. Call LLM (skip if no API key)
    print("4. Calling LLM...")
    try:
        response = llm_provider.generate(prompt)
        print(f"   ✓ LLM Response: {response[:200]}...")
        if len(response) > 200:
            print("      (truncated)")
        print()
    except Exception as e:
        print(f"   ⚠️  WARNING: LLM call failed (expected if no API key): {e}")
        print("   Skipping LLM response analysis\n")
        response = "git add src/api.py"  # Use a safe fallback

    # 5. Check for fingerprinting in response
    print("5. Analyzing response for safety...")
    try:
        detection = detector.analyze_command(response)
        if detection:
            print(f"   ⚠️  WARNING: Response triggered fingerprint detection: {detection}")
        else:
            print("   ✓ Response appears safe\n")
    except Exception as e:
        print(f"   ✗ FAIL: Detection analysis error: {e}")
        raise

    # 6. Generate /proc content
    print("6. Testing anti-fingerprinting /proc generation...")
    try:
        proc_version = anti_fp.get_proc_file("/proc/version")
        print(f"   ✓ /proc/version: {proc_version[:80]}...")
        if len(proc_version) > 80:
            print("      (truncated)")
        print()
    except Exception as e:
        print(f"   ✗ FAIL: /proc generation error: {e}")
        raise

    # 7. Test dynamic path generation (if LLM available)
    print("7. Testing dynamic path generation...")
    try:
        from LLM_Provider import LLMProvider
        provider = LLMProvider()
        paths = provider.generate_dynamic_paths("dev_alice", context)
        if paths:
            print(f"   ✓ Generated {len(paths)} dynamic paths")
            for i, path in enumerate(paths[:3]):  # Show first 3
                print(f"      {i+1}. {path}")
            if len(paths) > 3:
                print(f"      ... and {len(paths)-3} more")
        else:
            print("   ⚠️  WARNING: No dynamic paths generated (LLM may not be available)")
    except Exception as e:
        print(f"   ⚠️  WARNING: Dynamic path generation failed: {e}")

    print("\n=== Pipeline Test Complete ===")

if __name__ == "__main__":
    print("🧪 Testing Full Pipeline\n")
    test_full_pipeline()
    print("\n🎉 Full pipeline test completed!")