# MIRAGE Project Context Document

## Purpose
Feed this document to any AI assistant when you need help with the MIRAGE project.

---

## Project Overview

**MIRAGE** = Multi-persona Interactive Realistic Activity Generation Engine

A honeypot deception system that uses LLMs (Google Gemini) to generate realistic fake user activity. Unlike traditional honeypots that are empty or static, MIRAGE proactively creates believable file system artifacts, bash histories, and ongoing "work" from simulated users.

**Key Innovation**: Proactive generation (creates activity before attackers arrive) rather than reactive (responding to attacker commands).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MIRAGE System                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────────────────────┐    │
│  │   Persona   │    │      Behavioral Engine               │    │
│  │   Manager   │    │  ┌───────────┐ ┌──────────────┐     │    │
│  │             │───▶│  │Smart Timer│ │ Script Picker│     │    │
│  │ dev_alice   │    │  └───────────┘ └──────────────┘     │    │
│  │ sys_bob     │    │         ┌──────────────┐            │    │
│  │ svc_ci      │    │         │Story Planner │            │    │
│  └─────────────┘    │         └──────────────┘            │    │
│         │           └──────────────────┬──────────────────┘    │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌─────────────┐              ┌─────────────────┐              │
│  │   SPADE     │              │   LLM Provider  │              │
│  │   Prompt    │─────────────▶│   (Gemini API)  │              │
│  │   Engine    │              └────────┬────────┘              │
│  └─────────────┘                       │                        │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Execution Core (sys_core.py)                │   │
│  │  - Executes generated commands                           │   │
│  │  - Creates files, directories                            │   │
│  │  - Updates bash_history with timestamps                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Anti-Fingerprinting Subsystem                  │   │
│  │  - /proc file simulation (version, cpuinfo, mounts)     │   │
│  │  - Timing normalization                                  │   │
│  │  - Attacker behavior detection                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
project/
├── sys_core.py              # Main orchestrator, entry point
├── LLM_Provider.py          # Gemini API wrapper
├── ContentManager.py        # File read/write operations
├── StrategyManager.py       # Timing and scheduling logic
├── ActiveDefense.py         # Active response to threats
├── AntiFingerprint.py       # /proc simulation, attacker detection
├── UserArtifactGenerator.py # Creates .bashrc, .gitconfig, etc.
├── PromptEngine.py          # SPADE-style prompt construction
├── test_deception.py        # Unit tests (22 tests)
├── setup_linux.sh           # Linux deployment script
├── config.json              # Main configuration
├── worker-spec.json         # Persona definitions
├── templates.json           # Content templates
├── triggers.json            # Event triggers
└── monthly_plan.json        # Generated activity plan
```

---

## Key Modules

### 1. sys_core.py
Main entry point. Runs as daemon. Coordinates all other modules.
```bash
python sys_core.py --loop --strategy-hybrid --llm  # Production
python sys_core.py --dry-run --llm                 # Testing
```

### 2. AntiFingerprint.py
Three main classes:
- `AntiFingerprintManager`: Generates realistic /proc files
- `AttackerBehaviorDetector`: Detects fingerprinting commands
- `BashHistoryManager`: Manages history with timestamps and typos

### 3. PromptEngine.py
- `SPADEPromptEngine`: Builds structured prompts
- `ContextState`: Dataclass holding current state

SPADE = 6 sections: Identity, Goal, Threat Context, Strategy, Examples, Output Format

### 4. UserArtifactGenerator.py
- `UserArtifactGenerator`: Creates user home directory files
- `MetricsCollector`: Records activity metrics

### 5. LLM_Provider.py
Wrapper for Google Gemini API. Uses `gemini-1.5-flash` model.

---

## Personas

| Persona | Role | Home Directory | Typical Activity |
|---------|------|----------------|------------------|
| dev_alice | Senior Backend Developer | /home/dev_alice | git, vim, python, npm |
| sys_bob | System Administrator | /home/sys_bob | systemctl, logs, scripts |
| svc_ci | CI/CD Service | /var/lib/jenkins | builds, deploys, tests |

---

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-1.5-flash
CONFIG_DIR=/opt/sys_integrity/config
```

### config.json Key Settings
```json
{
  "personas": ["dev_alice", "sys_bob", "svc_ci"],
  "min_interval": 300,
  "max_interval": 1800,
  "work_hours": {"start": 9, "end": 18}
}
```

---

## Running Tests

```bash
# All unit tests
python test_deception.py

# Expected: 22 tests, all pass
```

Test classes:
- TestAntiFingerprintManager
- TestAttackerBehaviorDetector
- TestBashHistoryManager
- TestSPADEPromptEngine
- TestUserArtifactGenerator
- TestMetricsCollector
- TestIntegration

---

## Deployment

```bash
# Install on Linux
sudo ./setup_linux.sh install

# Configure API key
sudo nano /opt/sys_integrity/config/.env

# Test
sudo /opt/sys_integrity/test-dry-run.sh

# Start service
sudo systemctl enable --now sys-integrity-daemon

# Check status
sudo systemctl status sys-integrity-daemon
```

---

## Common Issues & Fixes

### Issue: Import errors
```bash
pip install google-generativeai
```

### Issue: API key invalid
Check `/opt/sys_integrity/config/.env` - no extra spaces

### Issue: Service won't start
```bash
sudo journalctl -u sys-integrity-daemon -n 50
```

### Issue: No files generated
```bash
sudo mkdir -p /home/dev_alice /home/sys_bob /var/lib/jenkins
```

### Issue: Tests fail
```bash
# Check Python version
python --version  # Need 3.8+

# Check you're in right directory
ls *.py | grep sys_core
```

---

## Research Paper Context

Paper title: "MIRAGE: LLM-Driven Deception Through Dynamic Persona Simulation"

Key claims:
- 95% content quality (vs 78% static honeypots)
- 89.6% fingerprint resistance (vs 8% for Cowrie)
- 0.31 KL divergence for temporal patterns (close to real users)

Placeholders still needed (in paper/deception_paper.tex):
- Expert assessment data (Table 4)
- Deployment duration [M] weeks
- Overhead measurements

---

## Modification Guide

### To add a new persona:
1. Add to `worker-spec.json`
2. Create home directory in `setup_linux.sh`
3. Add persona details in `PromptEngine.py` PERSONAS dict

### To change LLM model:
Edit `LLM_Provider.py` - change model name in constructor

### To add new /proc files:
Edit `AntiFingerprint.py` - add method in `AntiFingerprintManager`

### To modify prompt structure:
Edit `PromptEngine.py` - modify `build_prompt()` method

### To add new fingerprint detection:
Edit `AntiFingerprint.py` - add pattern in `AttackerBehaviorDetector.PATTERNS`

---

## Quick Debug Commands

```bash
# Check if service running
systemctl status sys-integrity-daemon

# View live logs
tail -f /opt/sys_integrity/logs/sys_monitor.log

# Check generated files
cat /home/dev_alice/.bash_history | tail -20

# Test LLM manually
python -c "
from LLM_Provider import LLMProvider
p = LLMProvider()
print(p.generate('Generate a git command'))
"

# Run single iteration
python sys_core.py --dry-run --llm --once
```

---

## API Reference

### LLMProvider
```python
provider = LLMProvider()
response = provider.generate(prompt_string)  # Returns string
```

### AntiFingerprintManager
```python
manager = AntiFingerprintManager()
content = manager.get_proc_file("/proc/version")  # Returns string
content = manager.get_system_file("/etc/os-release")  # Returns string
```

### AttackerBehaviorDetector
```python
detector = AttackerBehaviorDetector()
result = detector.analyze_command("cat /proc/self/exe")
# Returns dict with 'pattern' key if detected, None otherwise
threat = detector.get_threat_level()  # "none", "low", "medium", "high"
```

### SPADEPromptEngine
```python
engine = SPADEPromptEngine()
context = ContextState(...)  # See PromptEngine.py for fields
prompt = engine.build_prompt("dev_alice", context)
```

### BashHistoryManager
```python
manager = BashHistoryManager(username, home_dir, persona_config)
manager.add_command("git status")
manager.flush_to_file()  # Writes to ~/.bash_history
```

---

## Version Info
- Python: 3.8+
- LLM: Google Gemini (gemini-1.5-flash)
- OS: Linux (Ubuntu 20.04+ / Debian 11+)
- Service: systemd (sys-integrity-daemon)
