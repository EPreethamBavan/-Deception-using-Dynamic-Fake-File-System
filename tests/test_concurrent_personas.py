#!/usr/bin/env python3
"""
Test Concurrent Persona Processing
Tests multiple personas generating prompts simultaneously
"""

import threading
import time
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PromptEngine import SPADEPromptEngine, ContextState

def test_concurrent_personas():
    """Test concurrent persona prompt generation"""

    engine = SPADEPromptEngine()
    results = {}
    errors = []

    def test_persona(persona_name):
        try:
            context = ContextState(
                current_day=1,
                narrative_arc="Test Sprint",
                daily_task="Test task implementation",
                recent_commands=["git status", "vim test.py"],
                files_modified=["src/test.py"],
                current_project="test-project",
                build_status="passing",
                threat_level="none",
                fingerprint_detected=False
            )

            start = time.time()
            prompt = engine.build_prompt(persona_name, context)
            elapsed = time.time() - start

            results[persona_name] = {
                'prompt_length': len(prompt),
                'generation_time': elapsed,
                'success': True
            }
        except Exception as e:
            errors.append(f"{persona_name}: {e}")
            results[persona_name] = {
                'success': False,
                'error': str(e)
            }

    # Test personas concurrently
    personas = ["dev_alice", "sys_bob", "svc_ci"]
    threads = []

    print("=== Starting Concurrent Persona Test ===")
    print(f"Testing {len(personas)} personas simultaneously...")

    start_time = time.time()

    for persona in personas:
        t = threading.Thread(target=test_persona, args=(persona,))
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    total_time = time.time() - start_time

    print("
=== Results ===")
    print(".3f"    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  ✗ {error}")

    success_count = 0
    for persona, data in results.items():
        if data['success']:
            print(f"✓ {persona}: {data['prompt_length']} chars in {data['generation_time']:.3f}s")
            success_count += 1
        else:
            print(f"✗ {persona}: FAILED - {data['error']}")

    print("
=== Summary ===")
    print(f"Successful: {success_count}/{len(personas)}")
    print(".3f"
    if success_count > 0:
        avg_time = sum(data['generation_time'] for data in results.values() if data['success']) / success_count
        print(".3f"
    assert success_count == len(personas), f"Only {success_count}/{len(personas)} personas succeeded"
    assert total_time < 10.0, f"Concurrent execution took too long: {total_time:.3f}s"

    print("✓ PASS: All personas processed concurrently")

def test_sequential_baseline():
    """Test sequential processing for comparison"""

    engine = SPADEPromptEngine()
    personas = ["dev_alice", "sys_bob", "svc_ci"]

    context = ContextState(
        current_day=1,
        narrative_arc="Test Sprint",
        daily_task="Test task implementation",
        recent_commands=["git status", "vim test.py"],
        files_modified=["src/test.py"],
        current_project="test-project",
        build_status="passing",
        threat_level="none",
        fingerprint_detected=False
    )

    print("\n=== Sequential Baseline Test ===")

    start_time = time.time()
    results = {}

    for persona in personas:
        start = time.time()
        prompt = engine.build_prompt(persona, context)
        elapsed = time.time() - start
        results[persona] = {
            'prompt_length': len(prompt),
            'generation_time': elapsed
        }
        print(f"✓ {persona}: {len(prompt)} chars in {elapsed:.3f}s")

    total_time = time.time() - start_time
    print(".3f"
    print("✓ PASS: Sequential processing completed")

if __name__ == "__main__":
    print("🧪 Testing Concurrent Persona Processing\n")
    test_concurrent_personas()
    test_sequential_baseline()
    print("\n🎉 All concurrent processing tests passed!")