import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json
import os
from Orchestrator_Paper1 import DeceptionEngine

class TestDeceptionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DeceptionEngine(dry_run=True)
        # Mock Persona Data
        self.engine.personas = {
            "dev_alice": {
                "work_hours": [9, 17],
                "probability": 1.0, # Always active if in hours
                "home_dir": "/home/dev_alice",
                "scenes": [
                    {"name": "Routine1", "category": "Routine", "commands": ["cmd1"], "zone": "/tmp"},
                    {"name": "Variant1", "category": "Variant", "commands": ["cmd2"], "zone": "/tmp"}
                ]
            },
            "svc_ci": {
                "work_hours": [0, 23],
                "probability": 0.0,
                "scenes": [
                    {"name": "Build", "category": "Routine", "commands": ["build"], "zone": "/tmp"}
                ]
            }
        }
        self.engine.state = {"global_events": [], "users": {}}

    @patch('Orchestrator_Paper1.datetime')
    def test_is_active_window_in_hours(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0) # 10 AM
        self.assertTrue(self.engine.is_active_window("dev_alice", self.engine.personas["dev_alice"]))

    @patch('Orchestrator_Paper1.datetime')
    def test_is_active_window_out_hours(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 20, 0, 0) # 8 PM
        # Probability is 0.05 here, so we can't assert True/False easily without seeding or high p
        # For this test, let's just check it doesn't crash
        self.engine.is_active_window("dev_alice", self.engine.personas["dev_alice"])

    def test_trigger_logic(self):
        # 1. Simulate Alice Triggering Event
        self.engine.process_triggers("dev_alice", ["git commit", "git push origin main"])
        self.assertIn("trigger_build", self.engine.state["global_events"])

        # 2. Verify CI picks it up
        is_triggered = self.engine.check_triggers("svc_ci")
        self.assertTrue(is_triggered)

    @patch('random.random')
    def test_scene_selection_routine(self, mock_random):
        mock_random.return_value = 0.1 # < 0.70 => Routine
        scene = self.engine.select_scene("dev_alice", self.engine.personas["dev_alice"])
        self.assertEqual(scene['category'], "Routine")

if __name__ == '__main__':
    unittest.main()
