# Deception Engine - Dynamic Fake File System

A research implementation for creating plausible, stochastic honeypot behavior using dynamic fake file systems.

## Directory Structure

```
.
├── config/                 # Configuration files
│   ├── config.json        # Active defense ports, simulation parameters
│   ├── worker-spec.json   # Persona definitions (users, schedules, scenes)
│   ├── templates.json     # Command templates for different scenarios
│   ├── triggers.json      # Cross-user trigger rules
│   ├── monthly_plan.json  # Long-term narrative arc
│   ├── project_state.json # Project state (runtime)
│   ├── content_cache.json # Content cache (runtime)
│   └── state.json         # System state (runtime)
├── logs/                  # Log files
│   └── sys_monitor.log    # Main system log
├── src/                   # Source code (future)
├── docs/                  # Documentation
├── legacy_archive/        # Legacy code (old modules)
├── legacy_archive_2/      # Archived test scripts/zips
├── paper/                 # Research paper
├── sys_core.py           # Main orchestrator
├── LLM_Provider.py       # Gemini API integration
├── ContentManager.py     # Asset/state management
├── StrategyManager.py    # Strategy selection logic
├── ActiveDefense.py      # Honeyport listeners
├── PromptEngine.py       # Prompt engineering framework
├── UserArtifactGenerator.py # User artifact generation
├── AntiFingerprint.py    # Anti-fingerprinting measures
├── requirements.txt      # Python dependencies
├── setup_linux.sh        # Linux deployment script
├── create_bundle.sh      # Bundle creation script
├── DEPLOYMENT.md         # Deployment guide
├── set_dev_env.bat       # Development environment setup (Windows)
└── tests/                # Test suite
```

## Development Setup

### Windows Development

1. Set the CONFIG_DIR environment variable:
   ```batch
   call set_dev_env.bat
   ```

2. Install dependencies:
   ```batch
   pip install -r requirements.txt
   ```

3. Run tests:
   ```batch
   python test_deception.py
   ```

### Linux Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

## Configuration

All configuration files are stored in the `config/` directory. The system uses the `CONFIG_DIR` environment variable to locate configuration files, allowing flexible deployment.

## Research Paper

This implementation supports the research paper:
**"Deception using Dynamic Fake File System: A Framework for Plausible, Stochastic, and Adaptive Honeypot Behavior"**

## Key Features

- **Proactive Defense Agent**: OODA-loop powered decision engine (`DefenderAgent`) that adapts strategy based on observations
- **Persona Skill System**: Real tool execution (Git, Docker) via specialized skills (`skills/`) for high-fidelity deception
- **Persistent Memory**: Long-term story arc tracking for consistent multi-session narratives
- **Dynamic Path Generation**: LLM-powered generation of realistic, persona-specific directory structures
- **Intelligent Directory Creation**: Automatic creation of necessary directories based on command analysis
- **Modular Architecture**: Clean separation of concerns with configurable components
- **Stealth Deployment**: Systemd service with obfuscated naming
- **Cross-Platform**: Windows development, Linux deployment

## Usage

```python
from sys_core import SystemMonitor

# Set config directory
import os
os.environ['CONFIG_DIR'] = 'config'

# Initialize system
monitor = SystemMonitor(use_llm=True)

# Run simulation
monitor.run_simulation_loop()
```</content>
<parameter name="filePath">c:\Users\preet\Desktop\Research Paper\ADUD\Deception using Dynamic Fake File System\README.md