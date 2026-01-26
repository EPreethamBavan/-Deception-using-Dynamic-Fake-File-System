#!/usr/bin/env python3
"""
Test User Artifact Generation
Tests creation of user files like .bashrc, .gitconfig, etc.
"""

import tempfile
import os
import sys
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UserArtifactGenerator import UserArtifactGenerator

def test_artifact_generation():
    """Test user artifact generation"""

    # Create temp directory structure
    temp_dir = tempfile.mkdtemp()
    home_dir = os.path.join(temp_dir, "home", "test_dev")
    os.makedirs(home_dir)

    print(f"Test home directory: {home_dir}")

    try:
        # Configure persona
        personas = {
            "test_dev": {
                "home_dir": home_dir,
                "work_hours": [9, 17],
                "role": "Developer"
            }
        }

        # Generate artifacts
        generator = UserArtifactGenerator(personas)
        generator.generate_all_artifacts("test_dev")

        # Verify files were created
        expected_files = [
            ".bashrc",
            ".gitconfig",
            ".vimrc",
        ]

        print("\n=== Generated Files ===")
        created_files = []
        for filename in expected_files:
            filepath = os.path.join(home_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"✓ {filename} ({size} bytes)")
                created_files.append(filename)
            else:
                print(f"✗ MISSING: {filename}")

        assert len(created_files) == len(expected_files), f"Missing files: {set(expected_files) - set(created_files)}"

        # Show .bashrc content
        bashrc_path = os.path.join(home_dir, ".bashrc")
        if os.path.exists(bashrc_path):
            print("\n=== .bashrc Content (first 500 chars) ===")
            with open(bashrc_path, 'r') as f:
                content = f.read()
                print(content[:500])
                if len(content) > 500:
                    print("... (truncated)")

            # Verify .bashrc has expected content
            assert "HISTSIZE" in content, ".bashrc missing HISTSIZE"
            assert "HISTTIMEFORMAT" in content, ".bashrc missing HISTTIMEFORMAT"
            print("✓ PASS: .bashrc has required configuration")

        # Show .gitconfig content
        gitconfig_path = os.path.join(home_dir, ".gitconfig")
        if os.path.exists(gitconfig_path):
            print("\n=== .gitconfig Content ===")
            with open(gitconfig_path, 'r') as f:
                content = f.read()
                print(content)

            # Verify .gitconfig has expected sections
            assert "[user]" in content, ".gitconfig missing [user] section"
            assert "name" in content and "email" in content, ".gitconfig missing user info"
            print("✓ PASS: .gitconfig has required configuration")

        # Show .vimrc content
        vimrc_path = os.path.join(home_dir, ".vimrc")
        if os.path.exists(vimrc_path):
            print("\n=== .vimrc Content (first 300 chars) ===")
            with open(vimrc_path, 'r') as f:
                content = f.read()
                print(content[:300])
                if len(content) > 300:
                    print("... (truncated)")

            print("✓ PASS: .vimrc generated")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n✓ Cleanup: Removed test directory {temp_dir}")

if __name__ == "__main__":
    print("🧪 Testing User Artifact Generation\n")
    test_artifact_generation()
    print("\n🎉 All artifact generation tests passed!")