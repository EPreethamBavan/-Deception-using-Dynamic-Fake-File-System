import subprocess
import os
import pwd
import time

class SilentOrchestrator:
    def __init__(self):
        self.work_dir = "/opt/deception"

    def execute_as_persona(self, username, command):
        """
        Executes commands silently to maintain full consistency and avoid detection.
        """
        try:
            user_info = pwd.getpwnam(username)
            home = user_info.pw_dir

            # Secretly update history 
            self._write_bash_history(username, home, command)

            # Deceptive Execution: No terminal, no jobs, no output 
            # Uses setsid to fully detach the process 
            subprocess.Popen(
                ["sudo", "-u", username, "bash", "-c", f"cd {home} && {command}"],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=self._get_persona_env(username, home)
            )
        except:
            pass # Fail silently to prevent attacker discovery [cite: 18]

    def _get_persona_env(self, username, home):
        env = os.environ.copy()
        env.update({
            'HOME': home,
            'USER': username,
            'LOGNAME': username,
            'SHELL': '/bin/bash',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        })
        return env

    def _write_bash_history(self, username, home_dir, command):
        history_path = os.path.join(home_dir, ".bash_history")
        try:
            with open(history_path, "a") as f:
                f.write(f"{command}\n")
            user_info = pwd.getpwnam(username)
            os.chown(history_path, user_info.pw_uid, user_info.pw_gid)
        except:
            pass

if __name__ == "__main__":
    orch = SilentOrchestrator()
    while True:
        # Example periodic heartbeat update [cite: 20]
        orch.execute_as_persona("dev_alice", "touch /tmp/.system_keepalive")
        time.sleep(3600) # One hour interval [cite: 31]