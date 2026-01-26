#!/usr/bin/env python3
"""
Test Runner Script
Runs all MIRAGE tests in sequence
"""

import os
import sys
import subprocess
import time

def run_test(test_file, description):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('='*60)

    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, test_file],
                              capture_output=True, text=True, timeout=60)
        end_time = time.time()

        print(f"Exit code: {result.returncode}")
        print(".2f"
        if result.returncode == 0:
            print("✅ PASSED")
        else:
            print("❌ FAILED")

        if result.stdout:
            print("\n--- STDOUT ---")
            print(result.stdout)

        if result.stderr:
            print("\n--- STDERR ---")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""

    print("🧪 MIRAGE Test Suite Runner")
    print("=" * 60)

    # Set environment
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(test_dir)
    config_dir = os.path.join(project_dir, 'config')

    os.environ['CONFIG_DIR'] = config_dir
    os.environ['PYTHONPATH'] = project_dir

    print(f"Project directory: {project_dir}")
    print(f"Config directory: {config_dir}")
    print(f"Python path: {os.environ['PYTHONPATH']}")

    # Test files to run
    tests = [
        ("test_antifingerprint_manual.py", "Anti-Fingerprinting Module Tests"),
        ("test_attacker_detection.py", "Attacker Detection Tests"),
        ("test_bash_history.py", "Bash History Generation Tests"),
        ("test_prompt_engine.py", "SPADE Prompt Engine Tests"),
        ("test_artifact_generation.py", "User Artifact Generation Tests"),
        ("test_llm_connection.py", "LLM Connection Tests"),
        ("test_full_pipeline.py", "Full Pipeline Tests"),
        ("test_metrics.py", "Metrics Collection Tests"),
        ("test_concurrent_personas.py", "Concurrent Persona Tests"),
        ("test_dry_run.py", "Dry Run Integration Test"),
    ]

    # Run unit tests first (if available)
    unit_test_file = os.path.join(project_dir, "test_deception.py")
    if os.path.exists(unit_test_file):
        print(f"\n{'='*60}")
        print("Running: Unit Tests (test_deception.py)")
        print('='*60)

        try:
            result = subprocess.run([sys.executable, unit_test_file],
                                  capture_output=True, text=True, timeout=120)
            print(f"Exit code: {result.returncode}")
            if result.returncode == 0:
                print("✅ UNIT TESTS PASSED")
            else:
                print("❌ UNIT TESTS FAILED")

            if result.stdout:
                print("\n--- UNIT TEST OUTPUT ---")
                print(result.stdout[-2000:])  # Last 2000 chars

            if result.stderr:
                print("\n--- UNIT TEST ERRORS ---")
                print(result.stderr[-1000:])  # Last 1000 chars

        except Exception as e:
            print(f"❌ UNIT TEST ERROR: {e}")

    # Run individual tests
    results = []
    for test_file, description in tests:
        test_path = os.path.join(test_dir, test_file)
        if os.path.exists(test_path):
            success = run_test(test_path, description)
            results.append((test_file, success))
        else:
            print(f"\n⚠️  SKIPPED: {test_file} (file not found)")
            results.append((test_file, None))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)

    passed = 0
    failed = 0
    skipped = 0

    for test_file, success in results:
        if success is None:
            print(f"⚠️  SKIPPED: {test_file}")
            skipped += 1
        elif success:
            print(f"✅ PASSED: {test_file}")
            passed += 1
        else:
            print(f"❌ FAILED: {test_file}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0 and skipped == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    elif failed == 0:
        print("⚠️  SOME TESTS SKIPPED - Check configuration")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())