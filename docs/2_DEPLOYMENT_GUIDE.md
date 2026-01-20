# MIRAGE Deployment Guide

## Overview
This guide walks you through deploying MIRAGE (Multi-persona Interactive Realistic Activity Generation Engine) on a Linux server. The system creates realistic fake user activity to deceive attackers who compromise your honeypot.

---

## Prerequisites

### Hardware Requirements
- Linux server (Ubuntu 20.04+ or Debian 11+ recommended)
- Minimum 2GB RAM
- 10GB free disk space
- Network connectivity for API calls

### Software Requirements
- Python 3.8 or higher
- Git
- Root/sudo access

### API Requirements
- Google Gemini API key (get one at https://makersuite.google.com/app/apikey)

---

## Step 1: Transfer Files to Server

### Option A: Using SCP
```bash
# From your local machine (where you have the project files)
scp -r "Deception using Dynamic Fake File System" user@your-server:/tmp/mirage-source
```

### Option B: Using Git
If you've pushed to a private repo:
```bash
ssh user@your-server
git clone https://github.com/yourusername/mirage.git /tmp/mirage-source
```

### Option C: Using the Deployment Bundle
If you have the `deception_deploy.zip`:
```bash
scp deception_deploy.zip user@your-server:/tmp/
ssh user@your-server
cd /tmp
unzip deception_deploy.zip
```

---

## Step 2: Run the Installer

```bash
# SSH into your server
ssh user@your-server

# Navigate to source directory
cd /tmp/mirage-source

# Make installer executable
chmod +x setup_linux.sh

# Run as root
sudo ./setup_linux.sh install
```

### What the Installer Does
1. Creates `/opt/sys_integrity/` directory structure
2. Copies Python source files to `/opt/sys_integrity/src/`
3. Copies config files to `/opt/sys_integrity/config/`
4. Creates Python virtual environment
5. Installs dependencies (google-generativeai)
6. Creates systemd service `sys-integrity-daemon`
7. Sets up log rotation
8. Creates management scripts

---

## Step 3: Configure API Key

```bash
# Edit the environment file
sudo nano /opt/sys_integrity/config/.env
```

Change this line:
```
GEMINI_API_KEY=your_api_key_here
```

To your actual API key:
```
GEMINI_API_KEY=AIzaSy...your-actual-key...
```

Save and exit (Ctrl+X, Y, Enter).

### Verify API Key Works
```bash
# Quick test
cd /opt/sys_integrity
source venv/bin/activate
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Say hello')
print('API working:', response.text[:50])
"
```

---

## Step 4: Generate Initial Content

Before starting the daemon, generate the monthly plan and initial artifacts:

```bash
# Generate monthly activity plan
sudo /opt/sys_integrity/generate-plan.sh

# This creates monthly_plan.json with:
# - 30-day narrative arcs for each persona
# - Daily tasks
# - Project milestones
```

Check the generated plan:
```bash
cat /opt/sys_integrity/config/monthly_plan.json | python -m json.tool | head -50
```

---

## Step 5: Test with Dry Run

Before going live, test that everything works:

```bash
sudo /opt/sys_integrity/test-dry-run.sh
```

### What to Look For
- No Python errors
- LLM responses are generated
- Commands are printed (not executed in dry-run)
- Each persona shows activity

Example good output:
```
[2024-01-15 10:30:00] Running in DRY-RUN mode
[2024-01-15 10:30:01] Persona: dev_alice
[2024-01-15 10:30:02] Generated: cd ~/projects/backend-api && git pull origin main
[2024-01-15 10:30:02] [DRY-RUN] Would execute command
...
```

---

## Step 6: Start the Service

```bash
# Enable and start the service
sudo systemctl enable --now sys-integrity-daemon

# Check status
sudo systemctl status sys-integrity-daemon
```

### Expected Status Output
```
● sys-integrity-daemon.service - System Integrity Verification Service
     Loaded: loaded (/etc/systemd/system/sys-integrity-daemon.service; enabled)
     Active: active (running) since Mon 2024-01-15 10:35:00 UTC
   Main PID: 12345 (python)
```

---

## Step 7: Verify It's Working

### Check Logs
```bash
# View recent activity
tail -f /opt/sys_integrity/logs/sys_monitor.log

# Check for errors
tail -f /opt/sys_integrity/logs/sys_error.log
```

### Check Generated Files
```bash
# Developer persona
ls -la /home/dev_alice/
cat /home/dev_alice/.bash_history

# Sysadmin persona
ls -la /home/sys_bob/
cat /home/sys_bob/.bash_history

# CI/CD persona
ls -la /var/lib/jenkins/
```

### Check /proc Files
```bash
# These should look like real system files
cat /proc/version
cat /proc/cpuinfo
cat /proc/meminfo
```

---

## Directory Structure After Installation

```
/opt/sys_integrity/
├── src/
│   ├── sys_core.py           # Main orchestrator
│   ├── LLM_Provider.py       # Gemini API wrapper
│   ├── ContentManager.py     # File operations
│   ├── StrategyManager.py    # Timing logic
│   ├── ActiveDefense.py      # Defense responses
│   ├── AntiFingerprint.py    # /proc simulation
│   ├── UserArtifactGenerator.py  # User files
│   └── PromptEngine.py       # SPADE prompts
├── config/
│   ├── .env                  # API key (permissions 600)
│   ├── config.json           # Main config
│   ├── worker-spec.json      # Persona definitions
│   ├── templates.json        # Content templates
│   ├── triggers.json         # Event triggers
│   └── monthly_plan.json     # Generated plan
├── logs/
│   ├── sys_monitor.log       # Activity log
│   └── sys_error.log         # Error log
├── venv/                     # Python environment
├── status.sh                 # Quick status check
├── generate-plan.sh          # Regenerate monthly plan
├── refresh-content.sh        # Refresh artifacts
└── test-dry-run.sh          # Test without executing

/home/dev_alice/              # Developer persona
├── .bash_history
├── .bashrc
├── .gitconfig
├── .vimrc
├── .ssh/
└── projects/

/home/sys_bob/                # Sysadmin persona
├── .bash_history
├── .bashrc
├── scripts/
└── logs/

/var/lib/jenkins/             # CI/CD persona
├── .bash_history
├── workspace/
└── jobs/
```

---

## Common Operations

### Restart Service
```bash
sudo systemctl restart sys-integrity-daemon
```

### Stop Service
```bash
sudo systemctl stop sys-integrity-daemon
```

### View Live Logs
```bash
sudo journalctl -u sys-integrity-daemon -f
```

### Regenerate Monthly Plan
```bash
sudo /opt/sys_integrity/generate-plan.sh
sudo systemctl restart sys-integrity-daemon
```

### Update Configuration
```bash
sudo nano /opt/sys_integrity/config/config.json
sudo systemctl restart sys-integrity-daemon
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u sys-integrity-daemon -n 50
```

**Common issues:**
1. API key not set: Edit `/opt/sys_integrity/config/.env`
2. Missing dependencies: `sudo /opt/sys_integrity/venv/bin/pip install google-generativeai`
3. Permission issues: `sudo chown -R root:root /opt/sys_integrity`

### API Errors

**"API key not valid":**
- Verify key at https://makersuite.google.com/app/apikey
- Check for extra spaces in .env file

**"Quota exceeded":**
- Gemini has rate limits
- Reduce activity frequency in config.json
- Consider upgrading API tier

### No Files Being Generated

**Check persona directories exist:**
```bash
ls -la /home/dev_alice
ls -la /home/sys_bob
ls -la /var/lib/jenkins
```

**If missing, create them:**
```bash
sudo mkdir -p /home/dev_alice /home/sys_bob /var/lib/jenkins
```

### High CPU/Memory

**Check process:**
```bash
top -p $(pgrep -f sys_core.py)
```

**Reduce frequency:**
Edit `/opt/sys_integrity/config/config.json` and increase `min_interval` values.

---

## Uninstallation

To completely remove MIRAGE:

```bash
sudo ./setup_linux.sh uninstall
```

This removes:
- `/opt/sys_integrity/` directory
- Systemd service
- Log rotation config

**Note:** Persona home directories (`/home/dev_alice`, etc.) are NOT removed. Delete them manually if needed:
```bash
sudo rm -rf /home/dev_alice /home/sys_bob
```

---

## Security Considerations

1. **API Key Protection**: The .env file has 600 permissions. Never commit it to git.

2. **Network Isolation**: Consider running on an isolated network segment.

3. **Log Monitoring**: Logs may contain attacker commands. Monitor them.

4. **Updates**: Periodically regenerate the monthly plan to keep content fresh.

5. **Firewall**: Only allow necessary inbound connections (SSH from your IP).

---

## Quick Reference Commands

```bash
# Status
sudo systemctl status sys-integrity-daemon

# Start
sudo systemctl start sys-integrity-daemon

# Stop
sudo systemctl stop sys-integrity-daemon

# Restart
sudo systemctl restart sys-integrity-daemon

# Logs
tail -f /opt/sys_integrity/logs/sys_monitor.log

# Errors
tail -f /opt/sys_integrity/logs/sys_error.log

# Regenerate plan
sudo /opt/sys_integrity/generate-plan.sh

# Dry run test
sudo /opt/sys_integrity/test-dry-run.sh
```
