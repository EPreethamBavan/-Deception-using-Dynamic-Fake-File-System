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
        """Loads the narrative-driven persona schema [cite: 30, 92]"""
        try:
            with open(self.persona_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def is_active_window(self, persona):
        """Layer 1: Smart Timer - Temporal Modeling [cite: 31, 55]"""
        current_hour = datetime.now().hour
        start, end = persona['work_hours']
        
        # Handle overnight shifts for sys_bob [cite: 31]
        if start > end:
            is_in_shift = current_hour >= start or current_hour <= end
        else:
            is_in_shift = start <= current_hour <= end

        if is_in_shift:
            return random.random() < persona.get("probability", 0.7)
        return random.random() < 0.05 # 5% chance for off-hour anomalies [cite: 43]

    def _write_bash_history(self, username, home_dir, command):
        """Updates .bash_history with correct permissions for transparency """
        history_path = os.path.join(home_dir, ".bash_history")
        try:
            with open(history_path, "a") as f:
                f.write(f"{command}\n")
            user_info = pwd.getpwnam(username)
            os.chown(history_path, user_info.pw_uid, user_info.pw_gid)
        except:
            pass

    def execute_activity(self, username, persona):
        """
        Layer 2: Script Picker (Scenes) 
        Step 3: Direct the Performance (Execution) 
        """
        scenes = persona.get('scenes', [])
        if not scenes: return

        # Picker logic: Select a narrative block
        scene = random.choice(scenes)
        target_dir = scene['zone']
        home = persona.get('home_dir', f'/home/{username}')

        print(f"[*] {username} starting scene: {scene['name']}")

        for cmd in scene['commands']:
            # Stochastic Dropout: 10% chance to skip a command to avoid repetitive patterns [cite: 45, 99]
            if random.random() < 0.10:
                continue 

            self._write_bash_history(username, home, cmd)

            # Execution: Detached from TTY, masked as target user [cite: 39, 77]
            try:
                subprocess.Popen(
                    ["sudo", "-u", username, "bash", "-c", f"cd {target_dir} && {cmd}"],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"[!] Execution failed: {e}")

            # Inter-Command Jitter: 2-5 second delay to simulate human typing speed [cite: 93]
            time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    engine = DeceptionEngine()
    while True:
        personas = engine.load_personas()
        for user, data in personas.items():
            if engine.is_active_window(data):
                engine.execute_activity(user, data)
        
        # Random sleep between activity bursts to mimic behavioral rhythm [cite: 46, 99]
        # Range: 10 to 25 minutes
        sleep_time = random.randint(600, 1500)
        time.sleep(sleep_time)