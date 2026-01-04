import os
import pwd
import time
import json
import random
import subprocess
import setproctitle
from datetime import datetime

setproctitle.setproctitle("[kworker/u2:1-events]")

class DeceptionEngine:
    def __init__(self):
        self.persona_file = "/etc/default/.sys-maint/worker-spec.json"
        self.state_file = "/etc/default/.sys-maint/state.json"
        self.category_weights = {
            "Routine": 0.70,
            "Variant": 0.20,
            "Anomaly": 0.10
        }
        self._init_state()

    def _init_state(self):
        """Initializes state persistence to track narrative flow."""
        if not os.path.exists(self.state_file):
            initial_state = {"global_events": [], "users": {}}
            self._save_state(initial_state)

    def _load_state(self):
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _save_state(self, state):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=4)

    def load_personas(self):
        try:
            with open(self.persona_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def is_active_window(self, persona):
        current_hour = datetime.now().hour
        start, end = persona['work_hours']
        is_in_shift = current_hour >= start or current_hour <= end if start > end else start <= current_hour <= end
        
        if is_in_shift:
            return random.random() < persona.get("probability", 0.7)
        return random.random() < 0.05 

    def _write_bash_history(self, username, home_dir, command):
        history_path = os.path.join(home_dir, ".bash_history")
        try:
            with open(history_path, "a") as f:
                # Add timestamp comment to mimic real bash history if configured
                f.write(f"{command}\n")
            user_info = pwd.getpwnam(username)
            os.chown(history_path, user_info.pw_uid, user_info.pw_gid)
        except:
            pass

    def select_weighted_scene(self, persona, state, username):
        """Weighted Category Selection (Layer 2)"""
        scenes = persona.get('scenes', [])
        if not scenes: return None

        # Filter scenes by weight/category
        r = random.random()
        if r < 0.70:
            target_cat = "Routine"
        elif r < 0.90:
            target_cat = "Variant"
        else:
            target_cat = "Anomaly"

        eligible = [s for s in scenes if s.get('category') == target_cat]
        
        # Narrative Constraint: Don't repeat the exact last scene
        user_state = state['users'].get(username, {})
        last_scene = user_state.get('last_scene')
        
        final_pool = [s for s in eligible if s['name'] != last_scene]
        return random.choice(final_pool if final_pool else eligible)

    def check_triggers(self, state, username):
        """Cross-User Narrative: Trigger Logic"""
        # If svc_ci is the current user, check if there's a pending build
        if username == "svc_ci" and "trigger_build" in state.get("global_events", []):
            # Consume the event
            state["global_events"].remove("trigger_build")
            self._save_state(state)
            return True
        return False

    def execute_activity(self, username, persona):
        state = self._load_state()
        
        # Trigger Check for svc_ci
        is_triggered = self.check_triggers(state, username)
        
        # Selection Logic
        if is_triggered and username == "svc_ci":
            scene = next((s for s in persona['scenes'] if "Build" in s['name']), persona['scenes'][0])
        else:
            scene = self.select_weighted_scene(persona, state, username)

        if not scene: return

        target_dir = scene['zone']
        home = persona.get('home_dir', f'/home/{username}')

        for cmd in scene['commands']:
            if random.random() < 0.10: continue 

            self._write_bash_history(username, home, cmd)
            
            # Narrative Persistence: If Alice pushes, trigger CI build
            if "git push" in cmd and username == "dev_alice":
                if "trigger_build" not in state["global_events"]:
                    state["global_events"].append("trigger_build")

            try:
                subprocess.Popen(
                    ["sudo", "-u", username, "bash", "-c", f"cd {target_dir} && {cmd}"],
                    preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception: pass

            time.sleep(random.uniform(2, 5))

        # Update State
        if username not in state['users']: state['users'][username] = {}
        state['users'][username]['last_scene'] = scene['name']
        state['users'][username]['last_run'] = time.time()
        self._save_state(state)

if __name__ == "__main__":
    engine = DeceptionEngine()
    while True:
        personas = engine.load_personas()
        for user, data in personas.items():
            if engine.is_active_window(data):
                engine.execute_activity(user, data)
        
        # Behavioral Rhythm: Non-linear distribution (10–25 mins)
        sleep_time = random.randint(600, 1500)
        time.sleep(sleep_time)