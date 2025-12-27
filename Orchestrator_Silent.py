import os, pwd, time, json, random, setproctitle, subprocess
from datetime import datetime

# Stealth 2.0: Mask the process name as a kernel worker 
setproctitle.setproctitle("[kworker/u2:1-events]")

class MultiUserEngine:
    def __init__(self):
        self.persona_path = "/opt/deception/personas.json"

    def get_persona_data(self):
        with open(self.persona_path, 'r') as f:
            return json.load(f)

    def is_active_window(self, persona):
        """Checks Temporal Consistency (e.g., 9-5 work) """
        current_hour = datetime.now().hour
        start, end = persona['work_hours']
        
        # Stochastic Modeling: Probability-based activity 
        if start <= current_hour <= end:
            return random.random() < persona.get("probability", 0.7)
        return random.random() < 0.05 # 5% chance of 'off-hours' work

    def execute_activity(self, username, persona):
        """Step 3: Direct the Performance [cite: 39]"""
        cmd = random.choice(persona['commands'])
        target_dir = random.choice(persona['activity_zones'])
        home = persona['home_dir']

        # Update .bash_history to match acting user 
        history_path = os.path.join(home, ".bash_history")
        try:
            with open(history_path, "a") as f:
                f.write(f"{cmd}\n")
            user_info = pwd.getpwnam(username)
            os.chown(history_path, user_info.pw_uid, user_info.pw_gid)
        except: pass

        # Process Orphaning using setsid 
        subprocess.Popen(
            ["sudo", "-u", username, "bash", "-c", f"cd {target_dir} && {cmd}"],
            preexec_fn=os.setsid,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

if __name__ == "__main__":
    engine = MultiUserEngine()
    while True:
        personas = engine.get_persona_data()
        for user, data in personas.items():
            if engine.is_active_window(data):
                engine.execute_activity(user, data)
        
        # Random sleep between 10-30 mins to avoid 'Predictability Trap' [cite: 45]
        time.sleep(random.randint(600, 1800))