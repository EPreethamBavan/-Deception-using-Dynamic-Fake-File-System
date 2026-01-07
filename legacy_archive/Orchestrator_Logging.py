import subprocess
import os
import pwd
import time
import logging

# Configure logging to look like a standard system service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/var/log/syslog-refactor.log'
)

class GhostOrchestrator:
    def __init__(self):
        self.work_dir = "/opt/deception"

    def execute_as_persona(self, username, command):
        """
        Executes a command as a target user to ensure technical consistency[cite: 76, 77].
        """
        try:
            # Get user-specific IDs and home directory
            user_info = pwd.getpwnam(username)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
            home = user_info.pw_dir

            # Requirement: Process hiding and environment alignment [cite: 77]
            # We set the environment variables to match the persona exactly
            persona_env = os.environ.copy()
            persona_env.update({
                'HOME': home,
                'USER': username,
                'LOGNAME': username,
                'SHELL': '/bin/bash',
                'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
            })

            # Requirement: Update .bash_history for consistency [cite: 77]
            self._write_bash_history(home, command)

            # Step 3: Direct the Performance [cite: 39]
            # Use setsid to detach from the orchestrator's process group
            process = subprocess.Popen(
                ["sudo", "-u", username, "bash", "-c", f"cd {home} && {command}"],
                preexec_fn=os.setsid,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=persona_env,
                text=True
            )

            # We don't wait for long-running processes to avoid blocking the orchestrator
            # This mimics real background user activity [cite: 25]
            stdout, stderr = process.communicate(timeout=30)
            
            logging.info(f"Executed for {username}: {command} | Result: Success")
            return stdout

        except pwd.KeyError:
            logging.error(f"User {username} does not exist.")
        except Exception as e:
            logging.error(f"Execution failed: {str(e)}")

    def _write_bash_history(self, home_dir, command):
        """Manually appends to history to ensure visibility for attackers[cite: 77]."""
        history_path = os.path.join(home_dir, ".bash_history")
        try:
            with open(history_path, "a") as f:
                f.write(f"{command}\n")
            # Ensure the persona still owns their history file
            os.chown(history_path, pwd.getpwnam(os.path.basename(home_dir)).pw_uid, -1)
        except Exception as e:
            logging.error(f"History update failed: {e}")

if __name__ == "__main__":
    orchestrator = GhostOrchestrator()
    
    # Test Block: Mimicking 'dev_alice' behavior [cite: 42]
    # In Day 3, this will be replaced by your Layer 1/2 logic
    test_commands = [
        ("dev_alice", "touch /var/www/html/new_feature.php"),
        ("dev_alice", "git init"),
        ("sys_bob", "tail -n 20 /var/log/syslog > ~/log_excerpt.txt")
    ]

    for user, cmd in test_commands:
        print(f"Orchestrating {user}: {cmd}")
        orchestrator.execute_as_persona(user, cmd)
        time.sleep(2) # Natural delay between actions [cite: 31]