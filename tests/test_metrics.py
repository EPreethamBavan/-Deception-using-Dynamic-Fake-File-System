#!/usr/bin/env python3
"""
Test Metrics Collection
Tests recording and reporting of system metrics
"""

import tempfile
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UserArtifactGenerator import MetricsCollector

def test_metrics_collection():
    """Test metrics recording and reporting"""

    # Create temp file for metrics
    metrics_file = tempfile.mktemp(suffix=".json")
    print(f"Metrics file: {metrics_file}")

    try:
        collector = MetricsCollector(metrics_file)

        # Simulate a session
        print("=== Recording Session Activity ===")

        collector.record_session_start("test_session_001")
        print("✓ Session started: test_session_001")

        collector.record_command("test_session_001")
        collector.record_command("test_session_001")
        collector.record_command("test_session_001", is_fingerprint=True)
        collector.record_command("test_session_001")
        print("✓ Recorded 4 commands (1 fingerprint attempt)")

        collector.record_session_end("test_session_001")
        print("✓ Session ended: test_session_001")

        # Get summary
        summary = collector.get_summary()
        print("\n=== Metrics Summary ===")
        print(f"Total sessions: {summary.get('total_sessions', 0)}")
        print(f"Total commands: {summary.get('total_commands', 0)}")
        print(f"Fingerprint attempts: {summary.get('fingerprint_attempts', 0)}")

        # Verify
        assert summary['total_sessions'] == 1, f"Session count mismatch: expected 1, got {summary['total_sessions']}"
        assert summary['total_commands'] == 4, f"Command count mismatch: expected 4, got {summary['total_commands']}"
        assert summary['fingerprint_attempts'] == 1, f"Fingerprint count mismatch: expected 1, got {summary['fingerprint_attempts']}"
        print("✓ PASS: Metrics collection working correctly")

        # Check file contents
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                data = json.load(f)
            print(f"\n=== Raw Metrics File ({len(data)} entries) ===")
            for i, entry in enumerate(data[:3]):  # Show first 3 entries
                print(f"  {i+1}. {entry}")
            if len(data) > 3:
                print(f"  ... and {len(data)-3} more entries")
        else:
            print("⚠️  WARNING: Metrics file not created")

    finally:
        # Cleanup
        if os.path.exists(metrics_file):
            os.remove(metrics_file)
            print(f"\n✓ Cleanup: Removed metrics file {metrics_file}")

def test_multiple_sessions():
    """Test metrics with multiple sessions"""

    metrics_file = tempfile.mktemp(suffix=".json")

    try:
        collector = MetricsCollector(metrics_file)

        # Session 1
        collector.record_session_start("session_1")
        collector.record_command("session_1")
        collector.record_command("session_1", is_fingerprint=True)
        collector.record_session_end("session_1")

        # Session 2
        collector.record_session_start("session_2")
        collector.record_command("session_2")
        collector.record_command("session_2")
        collector.record_command("session_2")
        collector.record_session_end("session_2")

        summary = collector.get_summary()

        assert summary['total_sessions'] == 2, f"Expected 2 sessions, got {summary['total_sessions']}"
        assert summary['total_commands'] == 5, f"Expected 5 commands, got {summary['total_commands']}"
        assert summary['fingerprint_attempts'] == 1, f"Expected 1 fingerprint attempt, got {summary['fingerprint_attempts']}"

        print("✓ PASS: Multiple session metrics correct")

    finally:
        if os.path.exists(metrics_file):
            os.remove(metrics_file)

if __name__ == "__main__":
    print("🧪 Testing Metrics Collection\n")
    test_metrics_collection()
    test_multiple_sessions()
    print("\n🎉 All metrics collection tests passed!")