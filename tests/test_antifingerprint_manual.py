#!/usr/bin/env python3
"""
Test Anti-Fingerprinting Module
Tests /proc file generation and honeypot signature detection
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AntiFingerprint import AntiFingerprintManager

def test_proc_files():
    """Test /proc file generation"""
    manager = AntiFingerprintManager()

    print("=== Testing /proc/version ===")
    version = manager.get_proc_file("/proc/version")
    print(version)
    assert version, "Empty /proc/version"
    assert "Linux version" in version, "Invalid /proc/version format"
    print("✓ PASS: /proc/version generation\n")

    print("=== Testing /proc/cpuinfo (first 500 chars) ===")
    cpuinfo = manager.get_proc_file("/proc/cpuinfo")
    print(cpuinfo[:500])
    assert cpuinfo, "Empty /proc/cpuinfo"
    assert "processor" in cpuinfo, "Invalid /proc/cpuinfo format"
    print("✓ PASS: /proc/cpuinfo generation\n")

    print("=== Testing /proc/meminfo ===")
    meminfo = manager.get_proc_file("/proc/meminfo")
    print(meminfo)
    assert meminfo, "Empty /proc/meminfo"
    assert "MemTotal" in meminfo, "Invalid /proc/meminfo format"
    print("✓ PASS: /proc/meminfo generation\n")

    print("=== Testing /proc/mounts (honeypot signature check) ===")
    mounts = manager.get_proc_file("/proc/mounts")
    print(mounts)
    # Verify no honeypot signatures
    assert "hostfs" not in mounts.lower(), "FAIL: hostfs found (UML signature)"
    assert "uml" not in mounts.lower(), "FAIL: UML signature found"
    assert "hppfs" not in mounts.lower(), "FAIL: hppfs found (honeypot signature)"
    print("✓ PASS: No honeypot signatures detected\n")

    print("=== Testing /etc/os-release ===")
    os_release = manager.get_system_file("/etc/os-release")
    print(os_release)
    assert os_release, "Empty /etc/os-release"
    assert "PRETTY_NAME" in os_release, "Invalid /etc/os-release format"
    print("✓ PASS: /etc/os-release generation\n")

if __name__ == "__main__":
    print("🧪 Testing Anti-Fingerprinting Module\n")
    test_proc_files()
    print("🎉 All anti-fingerprinting tests passed!")