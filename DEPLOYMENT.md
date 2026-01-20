# Deception Engine - Deployment Guide

## Overview

This is the deployment guide for the **Dynamic Fake File System Deception Engine**, a research implementation for creating plausible, stochastic honeypot behavior.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Root/sudo access
- Google Gemini API key

## Quick Deployment

### 1. Transfer Files to Server

```bash
# On your local machine, create deployment bundle
tar -czvf deception-engine.tar.gz \
    sys_core.py \
    LLM_Provider.py \
    ContentManager.py \
    StrategyManager.py \
    ActiveDefense.py \
    setup_linux.sh \
    requirements.txt \
    worker-spec.json \
    config.json \
    templates.json \
    triggers.json \
    monthly_plan.json

# Transfer to server
scp deception-engine.tar.gz user@server:/tmp/
```

### 2. Install on Server

```bash
# SSH to server
ssh user@server

# Extract and install
cd /tmp
tar -xzvf deception-engine.tar.gz
sudo bash setup_linux.sh install
```

### 3. Configure API Key

```bash
sudo nano /opt/sys_integrity/config/.env
```

Add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 4. Test Installation

```bash
# Run dry-run test (no system changes)
sudo /opt/sys_integrity/test-dry-run.sh
```

### 5. Start Service

```bash
# Enable and start
sudo systemctl enable --now sys-integrity-daemon

# Check status
sudo systemctl status sys-integrity-daemon
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.env` | API keys and secrets |
| `config.json` | Active defense ports, simulation parameters |
| `worker-spec.json` | Persona definitions (users, schedules, scenes) |
| `templates.json` | Command templates for different scenarios |
| `triggers.json` | Cross-user trigger rules |
| `monthly_plan.json` | Long-term narrative arc |

## Management Commands

```bash
# Check status
deception-status

# Generate new monthly plan
sudo /opt/sys_integrity/generate-plan.sh

# Refresh honeytokens/vulnerabilities
sudo /opt/sys_integrity/refresh-content.sh

# View logs
sudo tail -f /opt/sys_integrity/logs/sys_monitor.log

# Restart service
sudo systemctl restart sys-integrity-daemon

# Stop service
sudo systemctl stop sys-integrity-daemon
```

## Customization

### Adding New Personas

Edit `/opt/sys_integrity/config/worker-spec.json`:

```json
{
    "new_user": {
        "work_hours": [9, 17],
        "probability": 0.7,
        "home_dir": "/home/new_user",
        "scenes": [
            {
                "name": "Daily Task",
                "category": "Routine",
                "zone": "/var/www/project",
                "commands": ["ls -la", "git status"]
            }
        ]
    }
}
```

### Adjusting Timing

Edit `/opt/sys_integrity/config/config.json`:

```json
{
    "simulation": {
        "loop_sleep_min": 5,
        "loop_sleep_max": 20
    }
}
```

## Uninstallation

```bash
sudo bash setup_linux.sh uninstall
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u sys-integrity-daemon -f

# Check error log
sudo cat /opt/sys_integrity/logs/sys_error.log
```

### API Rate Limiting
The engine includes exponential backoff. If you see rate limit errors:
1. Reduce activity by increasing sleep times in config.json
2. Consider using a higher-tier API plan

### Permission Errors
Ensure the service runs as root or has appropriate permissions:
```bash
sudo chown -R root:root /opt/sys_integrity
```

## Security Notes

1. The `.env` file contains your API key - keep it secure (mode 600)
2. Honeyports listen on configured ports - ensure firewall allows access if needed
3. Commands are executed as root - review templates before deployment
4. Logs may contain sensitive information - configure log rotation

## Architecture

```
sys_core.py         - Main orchestrator (execution loop)
LLM_Provider.py     - Gemini API integration
ContentManager.py   - Asset/state management
StrategyManager.py  - Strategy selection logic
ActiveDefense.py    - Honeyport listeners
```

## Research Paper Reference

This implementation supports the research paper:
**"Deception using Dynamic Fake File System: A Framework for Plausible, Stochastic, and Adaptive Honeypot Behavior"**
