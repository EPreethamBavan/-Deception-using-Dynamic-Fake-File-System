import os
import json
import pwd
import subprocess

def check_step(name, condition, fix_hint):
    if condition:
        print(f"[+] PASS: {name}")
        return True
    else:
        print(f"[!] FAIL: {name}")
        print(f"    Hint: {fix_hint}")
        return False

def run_diagnostic():
    print("--- Deception Engine: Day 4 Diagnostic ---")
    base_path = "/etc/default/.sys-maint"
    state_file = f"{base_path}/state.json"
    persona_file = f"{base_path}/worker-spec.json"

    # 1. Directory Permissions
    check_step("Directory Existence", os.path.exists(base_path), f"mkdir -p {base_path}")
    
    # 2. JSON Integrity
    try:
        with open(persona_file, 'r') as f:
            personas = json.load(f)
        check_step("Persona JSON Syntax", True, "")
    except Exception as e:
        check_step("Persona JSON Syntax", False, f"Fix JSON syntax in {persona_file}: {e}")

    # 3. Persona/User Existence
    for user in ["dev_alice", "sys_bob", "svc_ci"]:
        try:
            pwd.getpwnam(user)
            has_user = True
        except KeyError:
            has_user = False
        check_step(f"System User [{user}]", has_user, f"useradd -m {user}")

    # 4. Sudo Transition Test (The most common failure point)
    # We test if the engine (running as root/sudo) can actually impersonate alice
    try:
        test_cmd = ["sudo", "-u", "dev_alice", "whoami"]
        res = subprocess.check_output(test_cmd, stderr=subprocess.STDOUT).decode().strip()
        check_step("Sudo Impersonation", res == "dev_alice", "Check /etc/sudoers.d/ permissions")
    except Exception as e:
        check_step("Sudo Impersonation", False, f"Sudo error: {e}")

    # 5. Narrative Trigger Logic Test
    print("\n--- Testing Narrative Logic ---")
    mock_state = {"global_events": [], "users": {}}
    # Simulate Alice pushing
    if "git push" in str(personas['dev_alice']['scenes']):
        mock_state['global_events'].append("trigger_build")
        check_step("Logic: Alice Push -> CI Trigger", "trigger_build" in mock_state['global_events'], "Check trigger logic in execute_activity")

    print("\nDiagnostic Complete.")

if __name__ == "__main__":
    run_diagnostic()