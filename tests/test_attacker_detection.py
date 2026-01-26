#!/usr/bin/env python3
"""
Test Attacker Detection Module
Tests fingerprinting attempt detection
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AntiFingerprint import AttackerBehaviorDetector

def test_fingerprint_detection():
    """Test detection of fingerprinting attempts"""
    detector = AttackerBehaviorDetector()

    # These should be detected as fingerprinting attempts
    fingerprint_commands = [
        "busybox dd if=$SHELL bs=22 count=1",  # Cowrie detection
        "cat /proc/self/exe",                   # Binary inspection
        "cat /proc/mounts | grep hostfs",       # UML detection
        "echo $SHELL | md5sum",                 # Shell fingerprint
        "ls -la /proc/1/exe",                   # Init process check
        "cat /proc/version | grep UML",         # UML signature check
        "mount | grep hostfs",                  # Host filesystem detection
    ]

    print("=== Testing Fingerprint Detection ===")
    detected_count = 0
    for cmd in fingerprint_commands:
        result = detector.analyze_command(cmd)
        if result:
            print(f"✓ DETECTED: {cmd}")
            print(f"    Pattern: {result['pattern']}")
            detected_count += 1
        else:
            print(f"✗ MISSED: {cmd}")

    assert detected_count == len(fingerprint_commands), f"Missed {len(fingerprint_commands) - detected_count} fingerprint attempts"
    print(f"\n✓ PASS: Detected {detected_count}/{len(fingerprint_commands)} fingerprint attempts\n")

def test_normal_commands():
    """Test that normal commands don't trigger detection"""
    detector = AttackerBehaviorDetector()

    # These should NOT be detected
    normal_commands = [
        "ls -la /home/user",
        "cd /tmp",
        "git status",
        "vim main.py",
        "python -c 'print(\"hello\")'",
        "npm install",
        "docker build .",
        "ps aux | grep python",
    ]

    print("=== Testing Normal Commands (should not trigger) ===")
    false_positives = 0
    for cmd in normal_commands:
        result = detector.analyze_command(cmd)
        if result:
            print(f"✗ FALSE POSITIVE: {cmd}")
            print(f"    Incorrectly detected as: {result['pattern']}")
            false_positives += 1
        else:
            print(f"✓ OK: {cmd}")

    assert false_positives == 0, f"Had {false_positives} false positives"
    print(f"\n✓ PASS: No false positives in {len(normal_commands)} normal commands\n")

if __name__ == "__main__":
    print("🧪 Testing Attacker Detection Module\n")
    test_fingerprint_detection()
    test_normal_commands()
    print("🎉 All attacker detection tests passed!")