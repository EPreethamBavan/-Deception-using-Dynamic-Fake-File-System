#!/usr/bin/env python3
"""
Test Bash History Generation
Tests .bash_history file creation with timestamps
"""

import tempfile
import os
import sys
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AntiFingerprint import BashHistoryManager

def test_bash_history_generation():
    """Test bash history generation with timestamps"""

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    print(f"Test directory: {temp_dir}")

    try:
        # Initialize manager
        manager = BashHistoryManager(
            username="test_user",
            home_dir=temp_dir,
            persona_config={"work_hours": [9, 17]}
        )

        # Add commands
        commands = [
            "cd ~/projects",
            "git pull origin main",
            "npm install",
            "npm run build",
            "git status",
        ]

        print("=== Adding Commands ===")
        for cmd in commands:
            manager.add_command(cmd)
            print(f"✓ Added: {cmd}")

        # Flush to file
        manager.flush_to_file()

        # Read and verify
        history_file = os.path.join(temp_dir, ".bash_history")
        assert os.path.exists(history_file), "History file not created"

        with open(history_file, 'r') as f:
            content = f.read()

        print("\n=== Generated .bash_history ===")
        print(content)

        # Verify timestamps are present
        lines = content.strip().split('\n')
        timestamp_count = sum(1 for line in lines if line.startswith('#'))

        print(f"\nCommands added: {len(commands)}")
        print(f"Timestamp lines: {timestamp_count}")
        print(f"Total lines: {len(lines)}")

        assert timestamp_count >= len(commands), f"Missing timestamps! Expected at least {len(commands)}, got {timestamp_count}"
        assert len(lines) >= len(commands) * 2, f"Missing command lines! Expected at least {len(commands) * 2}, got {len(lines)}"

        # Verify commands are present (without timestamps)
        command_lines = [line for line in lines if not line.startswith('#')]
        for cmd in commands:
            assert cmd in command_lines, f"Command not found in history: {cmd}"

        print("✓ PASS: Timestamps present and commands recorded correctly")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n✓ Cleanup: Removed test directory {temp_dir}")

if __name__ == "__main__":
    print("🧪 Testing Bash History Generation\n")
    test_bash_history_generation()
    print("\n🎉 All bash history tests passed!")