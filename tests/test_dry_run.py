#!/usr/bin/env python3
"""
Dry Run Test Script
Tests the full system without executing any commands (safe for production)
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_dry_test():
    """Run dry-run test of the deception system"""

    print("🧪 MIRAGE Dry Run Test")
    print("=" * 50)

    # Set config directory
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    os.environ['CONFIG_DIR'] = config_dir
    print(f"Config directory: {config_dir}")

    try:
        from sys_core import SystemMonitor

        print("\n1. Initializing System Monitor...")
        monitor = SystemMonitor(dry_run=True, use_llm=True)
        print("   ✓ System monitor initialized")

        print("\n2. Testing configuration loading...")
        # Test that config files load
        monitor.content_manager.load_dynamic_files()
        print("   ✓ Configuration files loaded")

        print("\n3. Testing persona loading...")
        personas = monitor.content_manager.load_personas()
        print(f"   ✓ Loaded {len(personas)} personas: {list(personas.keys())}")

        print("\n4. Testing prompt generation...")
        from PromptEngine import SPADEPromptEngine, ContextState

        engine = SPADEPromptEngine()
        context = ContextState(
            current_day=1,
            narrative_arc="System Testing",
            daily_task="Verify dry run functionality",
            recent_commands=["echo 'test'"],
            files_modified=[],
            current_project="mirage-test",
            build_status="passing",
            threat_level="none",
            fingerprint_detected=False
        )

        for persona in list(personas.keys())[:2]:  # Test first 2 personas
            prompt = engine.build_prompt(persona, context)
            print(f"   ✓ Generated prompt for {persona} ({len(prompt)} chars)")

        print("\n5. Testing LLM integration (if available)...")
        try:
            from LLM_Provider import LLMProvider
            llm = LLMProvider()
            test_prompt = "Say 'test' and nothing else."
            response = llm.generate(test_prompt)
            print(f"   ✓ LLM responded: '{response}'")
        except Exception as e:
            print(f"   ⚠️  LLM not available: {e}")

        print("\n6. Testing anti-fingerprinting...")
        from AntiFingerprint import AntiFingerprintManager
        afm = AntiFingerprintManager()
        proc_version = afm.get_proc_file("/proc/version")
        print(f"   ✓ Generated /proc/version ({len(proc_version)} chars)")

        print("\n7. Testing command analysis...")
        from AntiFingerprint import AttackerBehaviorDetector
        detector = AttackerBehaviorDetector()

        test_commands = [
            "ls -la",
            "cat /proc/self/exe",  # Should be detected
            "git status"
        ]

        for cmd in test_commands:
            result = detector.analyze_command(cmd)
            status = "DETECTED" if result else "OK"
            print(f"   ✓ '{cmd}' -> {status}")

        print("\n8. Testing directory structure...")
        required_dirs = ['config', 'logs']
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                print(f"   ✓ {dir_name}/ directory exists")
            else:
                print(f"   ✗ {dir_name}/ directory missing")

        print("\n" + "=" * 50)
        print("🎉 DRY RUN TEST COMPLETED SUCCESSFULLY")
        print("The system is ready for deployment!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ DRY RUN TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = run_dry_test()
    sys.exit(0 if success else 1)