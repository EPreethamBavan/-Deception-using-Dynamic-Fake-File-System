import os
import pwd
import time
import json
import random
import subprocess
import setproctitle
from datetime import datetime

# Stealth 2.0: Mask the process name to look like a kernel thread
setproctitle.setproctitle("[kworker/u2:1-events]")

class DeceptionEngine:
    def __init__(self):
        self.persona_file = "/opt/deception/personas.json"

    def load_personas(self):
        try:
            with open(self.persona_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def is_active_window(self, persona):
        """Layer 1: Smart Timer - Probability check based on work hours """
        current_hour = datetime.now().hour
        start, end = persona['work_hours']
        
        # Handle overnight shifts (e.g., 22:00 to 02:00)
        if start > end:
            is_in_shift = current_hour >= start or current_hour <= end
        else:
            is_in_shift = start <= current_hour <= end

        if is_in_shift:
            return random.random() < persona.get("probability", 0.7)
        return random.random() < 0.05 # Small chance for off-hour activity [cite: 43, 46]

    def _write_bash_history(self, username, home_dir, command):
        """Updates .bash_history with correct ownership for transparency """
        history_path = os.path.join(home_dir, ".bash_history")
        try:
            with open(history_path, "a") as f:
                f.write(f"{command}\n")
            user_info = pwd.getpwnam(username)
            os.chown(history_path, user_info.pw_uid, user_info.pw_gid)
        except:
            pass

    def execute_activity(self, username, persona):
        """Step 3: Direct the Performance [cite: 39]"""
        # Pick a directory and a command valid for that specific directory
        zones = persona.get('activity_zones', {})
        if not zones: return

        target_dir = random.choice(list(zones.keys()))
        cmd = random.choice(zones[target_dir])
        home = persona.get('home_dir', f'/home/{username}')

        # Log the command in the fake user's history
        self._write_bash_history(username, home, cmd)

        # Execute as target user, detached from any TTY [cite: 39, 77]
        try:
            subprocess.Popen(
                ["sudo", "-u", username, "bash", "-c", f"cd {target_dir} && {cmd}"],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except:
            pass

if __name__ == "__main__":
    engine = DeceptionEngine()
    while True:
        personas = engine.load_personas()
        for user, data in personas.items():
            if engine.is_active_window(data):
                engine.execute_activity(user, data)
        
        # Random sleep to avoid the Predictability Trap (10-25 mins) [cite: 45, 99]
        time.sleep(random.randint(600, 1500))