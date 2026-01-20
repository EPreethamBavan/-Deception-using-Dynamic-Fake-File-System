#!/usr/bin/env python3
"""
test_deception.py - Test Suite for Deception Engine

Tests the core functionality of the deception system including:
- Anti-fingerprinting measures
- User artifact generation
- SPADE prompt engine
- Bash history with timestamps
- Metrics collection
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAntiFingerprintManager(unittest.TestCase):
    """Test anti-fingerprinting capabilities."""

    def setUp(self):
        from AntiFingerprint import AntiFingerprintManager
        self.manager = AntiFingerprintManager()

    def test_proc_version_generation(self):
        """Test /proc/version generation."""
        content = self.manager.get_proc_file("/proc/version")
        self.assertIsNotNone(content)
        self.assertIn("Linux version", content)
        self.assertIn("gcc", content.lower())

    def test_proc_cpuinfo_generation(self):
        """Test /proc/cpuinfo generation."""
        content = self.manager.get_proc_file("/proc/cpuinfo")
        self.assertIsNotNone(content)
        self.assertIn("processor", content)
        self.assertIn("model name", content)

    def test_proc_meminfo_generation(self):
        """Test /proc/meminfo generation."""
        content = self.manager.get_proc_file("/proc/meminfo")
        self.assertIsNotNone(content)
        self.assertIn("MemTotal", content)
        self.assertIn("MemFree", content)

    def test_proc_mounts_no_uml_signature(self):
        """Test that /proc/mounts doesn't contain UML honeypot signatures."""
        content = self.manager.get_proc_file("/proc/mounts")
        self.assertIsNotNone(content)
        # UML honeypots have distinct signatures - ensure they're not present
        self.assertNotIn("hostfs", content.lower())
        self.assertNotIn("uml", content.lower())

    def test_os_release_generation(self):
        """Test /etc/os-release generation."""
        content = self.manager.get_system_file("/etc/os-release")
        self.assertIsNotNone(content)
        self.assertIn("PRETTY_NAME", content)
        self.assertIn("VERSION_ID", content)


class TestAttackerBehaviorDetector(unittest.TestCase):
    """Test attacker behavior detection."""

    def setUp(self):
        from AntiFingerprint import AttackerBehaviorDetector
        self.detector = AttackerBehaviorDetector()

    def test_detect_cowrie_fingerprint(self):
        """Test detection of Cowrie fingerprinting attempts."""
        cmd = "busybox dd if=$SHELL bs=22 count=1"
        result = self.detector.analyze_command(cmd)
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "cowrie_detection")

    def test_detect_proc_self_exe(self):
        """Test detection of /proc/self/exe inspection."""
        cmd = "cat /proc/self/exe"
        result = self.detector.analyze_command(cmd)
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "binary_inspection")

    def test_normal_command_not_detected(self):
        """Test that normal commands are not flagged."""
        cmd = "ls -la /home/user"
        result = self.detector.analyze_command(cmd)
        self.assertIsNone(result)

    def test_threat_level_accumulation(self):
        """Test that threat level accumulates correctly."""
        self.assertEqual(self.detector.get_threat_level(), "none")

        # Add some detections
        self.detector.analyze_command("cat /proc/self/exe")
        self.detector.analyze_command("cat /proc/mounts")

        # Should now have elevated threat level
        self.assertNotEqual(self.detector.get_threat_level(), "none")


class TestBashHistoryManager(unittest.TestCase):
    """Test bash history management."""

    def setUp(self):
        from AntiFingerprint import BashHistoryManager
        self.temp_dir = tempfile.mkdtemp()
        self.manager = BashHistoryManager(
            "test_user",
            self.temp_dir,
            {"work_hours": [9, 17]}
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_command(self):
        """Test adding commands to history."""
        self.manager.add_command("ls -la")
        self.manager.add_command("cd /tmp")
        self.assertEqual(len(self.manager.history_buffer), 2)

    def test_flush_to_file(self):
        """Test flushing history to file."""
        self.manager.add_command("echo test")
        self.manager.flush_to_file()

        history_file = os.path.join(self.temp_dir, ".bash_history")
        self.assertTrue(os.path.exists(history_file))

        with open(history_file, 'r') as f:
            content = f.read()

        self.assertIn("echo test", content)
        # Should have timestamp line
        self.assertIn("#", content)

    def test_typo_generation(self):
        """Test typo generation for realism."""
        # Generate many typos to test probability
        typo_count = 0
        for _ in range(100):
            typo = self.manager._generate_typo("git status")
            if typo != "git status":
                typo_count += 1

        # Should have some typos (but not all)
        self.assertGreater(typo_count, 0)


class TestSPADEPromptEngine(unittest.TestCase):
    """Test SPADE-style prompt engine."""

    def setUp(self):
        from PromptEngine import SPADEPromptEngine, ContextState
        self.engine = SPADEPromptEngine()
        self.context = ContextState(
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

    def test_build_prompt_structure(self):
        """Test that prompts have all SPADE components."""
        prompt = self.engine.build_prompt("dev_alice", self.context)

        # Check all SPADE sections are present
        self.assertIn("IDENTITY & PERSONA", prompt)
        self.assertIn("GOAL & TASK", prompt)
        self.assertIn("THREAT CONTEXT", prompt)
        self.assertIn("STRATEGY & CONSTRAINTS", prompt)
        self.assertIn("OUTPUT EXAMPLES", prompt)
        self.assertIn("OUTPUT FORMAT", prompt)

    def test_persona_details_in_prompt(self):
        """Test that persona details are included."""
        prompt = self.engine.build_prompt("dev_alice", self.context)

        self.assertIn("Alice Chen", prompt)
        self.assertIn("Senior Backend Developer", prompt)
        self.assertIn("/home/dev_alice", prompt)

    def test_context_in_prompt(self):
        """Test that context is included in prompt."""
        prompt = self.engine.build_prompt("dev_alice", self.context)

        self.assertIn("Payment Gateway Integration", prompt)
        self.assertIn("Day: 5", prompt)

    def test_different_personas(self):
        """Test different persona prompts are distinct."""
        prompt_alice = self.engine.build_prompt("dev_alice", self.context)
        prompt_bob = self.engine.build_prompt("sys_bob", self.context)

        # Should have different role descriptions
        self.assertIn("Developer", prompt_alice)
        self.assertIn("Administrator", prompt_bob)


class TestUserArtifactGenerator(unittest.TestCase):
    """Test user artifact generation."""

    def setUp(self):
        from UserArtifactGenerator import UserArtifactGenerator
        self.temp_dir = tempfile.mkdtemp()
        self.personas = {
            "test_dev": {
                "home_dir": os.path.join(self.temp_dir, "home", "test_dev"),
                "work_hours": [9, 17],
                "role": "Developer"
            }
        }
        self.generator = UserArtifactGenerator(self.personas)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_artifacts(self):
        """Test artifact generation creates files."""
        self.generator.generate_all_artifacts("test_dev")

        home = self.personas["test_dev"]["home_dir"]

        # Check key files exist
        self.assertTrue(os.path.exists(os.path.join(home, ".bashrc")))
        self.assertTrue(os.path.exists(os.path.join(home, ".gitconfig")))
        self.assertTrue(os.path.exists(os.path.join(home, ".vimrc")))

    def test_bashrc_content(self):
        """Test .bashrc has realistic content."""
        self.generator.generate_all_artifacts("test_dev")

        bashrc_path = os.path.join(
            self.personas["test_dev"]["home_dir"],
            ".bashrc"
        )

        with open(bashrc_path, 'r') as f:
            content = f.read()

        # Should have common bash configurations
        self.assertIn("HISTSIZE", content)
        self.assertIn("HISTTIMEFORMAT", content)
        self.assertIn("alias", content)


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection."""

    def setUp(self):
        from UserArtifactGenerator import MetricsCollector
        self.temp_file = tempfile.mktemp(suffix=".json")
        self.collector = MetricsCollector(self.temp_file)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_record_commands(self):
        """Test command recording."""
        self.collector.record_session_start("session1")
        self.collector.record_command("session1")
        self.collector.record_command("session1", is_fingerprint=True)

        summary = self.collector.get_summary()
        self.assertEqual(summary['total_commands'], 2)
        self.assertEqual(summary['fingerprint_attempts'], 1)

    def test_persistence(self):
        """Test that metrics persist to file."""
        self.collector.record_session_start("session1")
        self.collector.record_command("session1")

        # Create new collector from same file
        from UserArtifactGenerator import MetricsCollector
        new_collector = MetricsCollector(self.temp_file)

        summary = new_collector.get_summary()
        self.assertEqual(summary['total_commands'], 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full system."""

    def test_module_imports(self):
        """Test all modules can be imported."""
        try:
            from AntiFingerprint import AntiFingerprintManager
            from UserArtifactGenerator import UserArtifactGenerator
            from PromptEngine import SPADEPromptEngine
            success = True
        except ImportError as e:
            success = False
            print(f"Import error: {e}")

        self.assertTrue(success)

    def test_json_configs_valid(self):
        """Test that all JSON config files are valid."""
        config_files = [
            "config.json",
            "worker-spec.json",
            "templates.json",
            "triggers.json",
            "monthly_plan.json"
        ]

        for filename in config_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    self.fail(f"Invalid JSON in {filename}")


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAntiFingerprintManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAttackerBehaviorDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestBashHistoryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSPADEPromptEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestUserArtifactGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
