# MIRAGE Testing Guide

## Overview
This guide explains how to verify that MIRAGE is working correctly. It covers unit tests, integration tests, and manual verification procedures.

---

## Part 1: Unit Tests

### Running the Test Suite

```bash
cd /opt/sys_integrity/src
# Or if testing locally:
cd "Deception using Dynamic Fake File System"

# Activate virtual environment
source /opt/sys_integrity/venv/bin/activate
# Or locally: python -m venv venv && source venv/bin/activate

# Run all tests
python test_deception.py
```

### Expected Output (All 22 Tests)

```
test_proc_version_generation ... ok
test_proc_cpuinfo_generation ... ok
test_proc_meminfo_generation ... ok
test_proc_mounts_no_uml_signature ... ok
test_os_release_generation ... ok
test_detect_cowrie_fingerprint ... ok
test_detect_proc_self_exe ... ok
test_normal_command_not_detected ... ok
test_threat_level_accumulation ... ok
test_add_command ... ok
test_flush_to_file ... ok
test_typo_generation ... ok
test_build_prompt_structure ... ok
test_persona_details_in_prompt ... ok
test_context_in_prompt ... ok
test_different_personas ... ok
test_generate_artifacts ... ok
test_bashrc_content ... ok
test_record_commands ... ok
test_persistence ... ok
test_module_imports ... ok
test_json_configs_valid ... ok

----------------------------------------------------------------------
Ran 22 tests in X.XXXs

OK
```

### If Tests Fail

**Import errors:**
```bash
# Install missing dependencies
pip install google-generativeai
```

**File not found errors:**
```bash
# Ensure you're in the correct directory
pwd  # Should show the project directory
ls *.py  # Should show sys_core.py, AntiFingerprint.py, etc.
```

---

## Part 2: Module-by-Module Testing

### 2.1 Testing Anti-Fingerprinting

```python
# test_antifingerprint_manual.py
from AntiFingerprint import AntiFingerprintManager, AttackerBehaviorDetector

# Test /proc file generation
manager = AntiFingerprintManager()

print("=== /proc/version ===")
print(manager.get_proc_file("/proc/version"))
print()

print("=== /proc/cpuinfo (first 500 chars) ===")
print(manager.get_proc_file("/proc/cpuinfo")[:500])
print()

print("=== /proc/meminfo ===")
print(manager.get_proc_file("/proc/meminfo"))
print()

print("=== /proc/mounts ===")
mounts = manager.get_proc_file("/proc/mounts")
print(mounts)
# Verify no honeypot signatures
assert "hostfs" not in mounts.lower(), "FAIL: hostfs found (UML signature)"
assert "uml" not in mounts.lower(), "FAIL: UML signature found"
print("PASS: No honeypot signatures detected")
```

Run it:
```bash
python test_antifingerprint_manual.py
```

### 2.2 Testing Attacker Detection

```python
# test_attacker_detection.py
from AntiFingerprint import AttackerBehaviorDetector

detector = AttackerBehaviorDetector()

# These should be detected as fingerprinting attempts
fingerprint_commands = [
    "busybox dd if=$SHELL bs=22 count=1",  # Cowrie detection
    "cat /proc/self/exe",                   # Binary inspection
    "cat /proc/mounts | grep hostfs",       # UML detection
    "echo $SHELL | md5sum",                 # Shell fingerprint
    "ls -la /proc/1/exe",                   # Init process check
]

print("=== Testing Fingerprint Detection ===")
for cmd in fingerprint_commands:
    result = detector.analyze_command(cmd)
    if result:
        print(f"DETECTED: {cmd}")
        print(f"  Pattern: {result['pattern']}")
    else:
        print(f"MISSED: {cmd}")
print()

# These should NOT be detected
normal_commands = [
    "ls -la /home/user",
    "cd /tmp",
    "git status",
    "vim main.py",
]

print("=== Testing Normal Commands (should not trigger) ===")
for cmd in normal_commands:
    result = detector.analyze_command(cmd)
    if result:
        print(f"FALSE POSITIVE: {cmd}")
    else:
        print(f"OK: {cmd}")
```

### 2.3 Testing Bash History Generation

```python
# test_bash_history.py
import tempfile
import os
from AntiFingerprint import BashHistoryManager

# Create temp directory
temp_dir = tempfile.mkdtemp()
print(f"Test directory: {temp_dir}")

# Initialize manager
manager = BashHistoryManager(
    username="test_user",
    home_dir=temp_dir,
    persona_config={"work_hours": [9, 17]}
)

# Add commands
commands = [
    "cd ~/projects",
    "git pull origin main",
    "npm install",
    "npm run build",
    "git status",
]

for cmd in commands:
    manager.add_command(cmd)

# Flush to file
manager.flush_to_file()

# Read and verify
history_file = os.path.join(temp_dir, ".bash_history")
with open(history_file, 'r') as f:
    content = f.read()

print("=== Generated .bash_history ===")
print(content)
print()

# Verify timestamps are present
lines = content.strip().split('\n')
timestamp_count = sum(1 for line in lines if line.startswith('#'))
print(f"Commands: {len(commands)}")
print(f"Timestamp lines: {timestamp_count}")
assert timestamp_count >= len(commands), "Missing timestamps!"
print("PASS: Timestamps present")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
```

### 2.4 Testing SPADE Prompt Engine

```python
# test_prompt_engine.py
from PromptEngine import SPADEPromptEngine, ContextState

engine = SPADEPromptEngine()

# Create test context
context = ContextState(
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

# Generate prompt for each persona
for persona in ["dev_alice", "sys_bob", "svc_ci"]:
    prompt = engine.build_prompt(persona, context)
    print(f"=== Prompt for {persona} ===")
    print(f"Length: {len(prompt)} characters")

    # Verify SPADE sections
    sections = [
        "IDENTITY & PERSONA",
        "GOAL & TASK",
        "THREAT CONTEXT",
        "STRATEGY & CONSTRAINTS",
        "OUTPUT EXAMPLES",
        "OUTPUT FORMAT"
    ]

    for section in sections:
        if section in prompt:
            print(f"  [OK] {section}")
        else:
            print(f"  [MISSING] {section}")
    print()
```

### 2.5 Testing User Artifact Generation

```python
# test_artifact_generation.py
import tempfile
import os
from UserArtifactGenerator import UserArtifactGenerator

# Create temp directory
temp_dir = tempfile.mkdtemp()
home_dir = os.path.join(temp_dir, "home", "test_dev")
os.makedirs(home_dir)

print(f"Test home directory: {home_dir}")

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

print("=== Generated Files ===")
for filename in expected_files:
    filepath = os.path.join(home_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"[OK] {filename} ({size} bytes)")
    else:
        print(f"[MISSING] {filename}")

# Show .bashrc content
bashrc_path = os.path.join(home_dir, ".bashrc")
if os.path.exists(bashrc_path):
    print("\n=== .bashrc Content ===")
    with open(bashrc_path, 'r') as f:
        print(f.read()[:500])

# Cleanup
import shutil
shutil.rmtree(temp_dir)
```

---

## Part 3: Integration Testing

### 3.1 Dry Run Test

The most important integration test - runs the full system without executing commands:

```bash
sudo /opt/sys_integrity/test-dry-run.sh
```

Or manually:
```bash
cd /opt/sys_integrity
source venv/bin/activate
export CONFIG_DIR=/opt/sys_integrity/config
python src/sys_core.py --dry-run --llm --strategy-hybrid
```

**What to verify:**
1. No Python exceptions
2. LLM responses are generated for each persona
3. Commands look realistic (git commands, file operations, etc.)
4. Timing between activities

### 3.2 LLM Connection Test

```python
# test_llm_connection.py
import os
os.environ['GEMINI_API_KEY'] = 'your-api-key-here'  # Or read from .env

from LLM_Provider import LLMProvider

provider = LLMProvider()

# Test simple generation
prompt = """You are a senior developer. Generate a single realistic bash command
that you would run while working on a Python backend project.
Output only the command, nothing else."""

response = provider.generate(prompt)
print(f"LLM Response: {response}")

# Verify response looks like a command
assert response, "Empty response from LLM"
assert len(response) < 500, "Response too long (not a command)"
print("PASS: LLM connection working")
```

### 3.3 Full Pipeline Test

```python
# test_full_pipeline.py
"""Test the complete generation pipeline."""
import os
import sys

# Setup environment
os.environ['CONFIG_DIR'] = '/opt/sys_integrity/config'
sys.path.insert(0, '/opt/sys_integrity/src')

from PromptEngine import SPADEPromptEngine, ContextState
from LLM_Provider import LLMProvider
from AntiFingerprint import AntiFingerprintManager, AttackerBehaviorDetector

print("=== Full Pipeline Test ===\n")

# 1. Initialize components
print("1. Initializing components...")
prompt_engine = SPADEPromptEngine()
llm_provider = LLMProvider()
anti_fp = AntiFingerprintManager()
detector = AttackerBehaviorDetector()
print("   Components initialized\n")

# 2. Create context
print("2. Creating context...")
context = ContextState(
    current_day=10,
    narrative_arc="API Development Sprint",
    daily_task="Add error handling to endpoints",
    recent_commands=["git status", "pytest tests/"],
    files_modified=["src/api.py"],
    current_project="backend-api",
    build_status="passing",
    threat_level="none",
    fingerprint_detected=False
)
print("   Context created\n")

# 3. Generate prompt
print("3. Generating SPADE prompt for dev_alice...")
prompt = prompt_engine.build_prompt("dev_alice", context)
print(f"   Prompt length: {len(prompt)} characters\n")

# 4. Call LLM
print("4. Calling LLM...")
response = llm_provider.generate(prompt)
print(f"   LLM Response: {response[:200]}...\n")

# 5. Check for fingerprinting in response
print("5. Analyzing response for safety...")
detection = detector.analyze_command(response)
if detection:
    print(f"   WARNING: Response triggered fingerprint detection: {detection}")
else:
    print("   Response appears safe\n")

# 6. Generate /proc content
print("6. Testing anti-fingerprinting /proc generation...")
proc_version = anti_fp.get_proc_file("/proc/version")
print(f"   /proc/version: {proc_version[:80]}...\n")

print("=== Pipeline Test Complete ===")
```

---

## Part 4: Manual Verification Checklist

After MIRAGE has been running for a few hours, manually verify:

### 4.1 Check Bash History Files

```bash
# Developer persona
echo "=== dev_alice .bash_history ==="
cat /home/dev_alice/.bash_history | tail -20

# Verify:
# - Contains timestamps (lines starting with #)
# - Commands are realistic (git, vim, npm, python)
# - Has some typos (realistic)
# - Time gaps between commands make sense
```

### 4.2 Check Generated Config Files

```bash
# .bashrc should have realistic content
echo "=== dev_alice .bashrc ==="
cat /home/dev_alice/.bashrc

# Verify:
# - HISTSIZE is set
# - HISTTIMEFORMAT is set
# - Has aliases
# - Looks like a real developer's bashrc
```

### 4.3 Check .gitconfig

```bash
echo "=== dev_alice .gitconfig ==="
cat /home/dev_alice/.gitconfig

# Verify:
# - Has [user] section with name and email
# - Has [core] settings
# - Looks realistic
```

### 4.4 Verify No Honeypot Signatures

```bash
# These commands should return realistic output, NOT honeypot signatures

# Check /proc/version
cat /proc/version
# Should look like: Linux version 5.x.x-xxx-generic (builder@host) (gcc version...)
# Should NOT contain: UML, User-Mode-Linux, honeypot

# Check /proc/mounts
cat /proc/mounts
# Should NOT contain: hostfs, hppfs, uml

# Check /proc/cpuinfo
cat /proc/cpuinfo
# Should have realistic CPU info
```

### 4.5 Activity Timing Verification

```bash
# Extract timestamps from bash history
grep "^#" /home/dev_alice/.bash_history | tail -20

# Convert to readable format
grep "^#" /home/dev_alice/.bash_history | while read line; do
    ts=$(echo $line | cut -c2-)
    date -d "@$ts" "+%Y-%m-%d %H:%M:%S"
done | tail -20

# Verify:
# - Most activity during work hours (9 AM - 6 PM)
# - Some occasional off-hours activity
# - Gaps between commands (not machine-gun rapid)
```

---

## Part 5: Metrics Collection Test

### 5.1 Test Metrics Recording

```python
# test_metrics.py
import tempfile
from UserArtifactGenerator import MetricsCollector

# Create temp file for metrics
metrics_file = tempfile.mktemp(suffix=".json")
collector = MetricsCollector(metrics_file)

# Simulate a session
collector.record_session_start("test_session_001")
collector.record_command("test_session_001")
collector.record_command("test_session_001")
collector.record_command("test_session_001", is_fingerprint=True)
collector.record_command("test_session_001")
collector.record_session_end("test_session_001")

# Get summary
summary = collector.get_summary()
print("=== Metrics Summary ===")
print(f"Total sessions: {summary.get('total_sessions', 0)}")
print(f"Total commands: {summary.get('total_commands', 0)}")
print(f"Fingerprint attempts: {summary.get('fingerprint_attempts', 0)}")

# Verify
assert summary['total_commands'] == 4, "Command count mismatch"
assert summary['fingerprint_attempts'] == 1, "Fingerprint count mismatch"
print("\nPASS: Metrics collection working")

# Cleanup
import os
os.remove(metrics_file)
```

---

## Part 6: Stress Testing

### 6.1 Multiple Persona Concurrent Test

```python
# test_concurrent_personas.py
import threading
import time
from PromptEngine import SPADEPromptEngine, ContextState

engine = SPADEPromptEngine()
results = {}

def test_persona(persona_name):
    context = ContextState(
        current_day=1,
        narrative_arc="Test",
        daily_task="Test task",
        recent_commands=[],
        files_modified=[],
        current_project="test",
        build_status="passing",
        threat_level="none",
        fingerprint_detected=False
    )

    start = time.time()
    prompt = engine.build_prompt(persona_name, context)
    elapsed = time.time() - start

    results[persona_name] = {
        'prompt_length': len(prompt),
        'generation_time': elapsed
    }

# Run for all personas concurrently
threads = []
for persona in ["dev_alice", "sys_bob", "svc_ci"]:
    t = threading.Thread(target=test_persona, args=(persona,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("=== Concurrent Persona Test ===")
for persona, data in results.items():
    print(f"{persona}: {data['prompt_length']} chars in {data['generation_time']:.3f}s")
```

---

## Part 7: Troubleshooting Test Failures

### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify all modules exist
ls -la *.py

# Check for syntax errors
python -m py_compile AntiFingerprint.py
python -m py_compile PromptEngine.py
python -m py_compile UserArtifactGenerator.py
```

### API Errors
```bash
# Test API key directly
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY_HERE')
model = genai.GenerativeModel('gemini-1.5-flash')
print(model.generate_content('test').text)
"
```

### Permission Errors
```bash
# Check directory permissions
ls -la /home/dev_alice
ls -la /opt/sys_integrity/

# Fix if needed
sudo chown -R root:root /opt/sys_integrity
sudo chmod -R 755 /opt/sys_integrity
sudo chmod 600 /opt/sys_integrity/config/.env
```

---

## Quick Test Commands Reference

```bash
# Run unit tests
python test_deception.py

# Dry run (no file changes)
python sys_core.py --dry-run --llm

# Test LLM connection
python -c "from LLM_Provider import LLMProvider; p=LLMProvider(); print(p.generate('Say hello'))"

# Check generated files
ls -la /home/dev_alice/
cat /home/dev_alice/.bash_history | tail -10

# Check service status
systemctl status sys-integrity-daemon

# View logs
tail -f /opt/sys_integrity/logs/sys_monitor.log
```
