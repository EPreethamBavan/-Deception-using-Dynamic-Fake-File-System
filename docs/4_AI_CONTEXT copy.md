# MIRAGE: Complete AI Context Document

> **Purpose**: This document provides comprehensive context for AI assistants to understand, analyze, and help improve the MIRAGE honeypot deception system or its associated research paper.

---

## 1. Executive Summary

**MIRAGE** (Multi-persona Interactive Realistic Activity Generation Engine) is a research honeypot deception framework that uses Google Gemini LLM to generate plausible, stochastic fake user activity on Linux systems.

### Core Innovation
Unlike traditional honeypots (Cowrie, Dionaea) that are empty or respond only reactively, MIRAGE **proactively generates realistic activity BEFORE attackers arrive**. This makes honeypots appear to be genuinely active development/operations servers.

### Key Research Claims
| Metric | MIRAGE | Static Honeypot | Cowrie |
|--------|--------|-----------------|--------|
| Content Quality | 95% | 78% | 45% |
| Fingerprint Resistance | 89.6% | N/A | 8% |
| Temporal Realism (KL Divergence) | 0.31 | Higher | Higher |
| Work-hour Compliance | 0.87 | N/A | N/A |

### Deployment Model
- Runs as `sys-integrity-daemon` systemd service on Linux (Ubuntu 20.04+, Debian 11+)
- Uses Google Gemini API (`gemini-1.5-flash`) for dynamic content generation
- Simulates 3 personas: developer, sysadmin, CI bot
- Stealth naming avoids detection (looks like a security service)

---

## 2. System Architecture

```
+------------------------------------------------------------------+
|                         MIRAGE SYSTEM                             |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+     +-----------------------------------+   |
|  |  PERSONA MANAGER |     |      BEHAVIORAL ENGINE            |   |
|  |                  |     |  +-------------+ +-------------+  |   |
|  |  - dev_alice     |---->|  | Smart Timer | |Script Picker|  |   |
|  |  - sys_bob       |     |  | (Layer 1)   | | (Layer 2)   |  |   |
|  |  - svc_ci        |     |  +-------------+ +-------------+  |   |
|  +------------------+     |       +------------------+        |   |
|          |                |       | Story Planner    |        |   |
|          |                |       | (Layer 3)        |        |   |
|          v                +-------+--------+---------+--------+   |
|  +------------------+              |                              |
|  |  SPADE PROMPT    |              v                              |
|  |  ENGINE          |     +------------------+                    |
|  |                  |---->| LLM PROVIDER     |                    |
|  |  - Identity      |     | (Gemini API)     |                    |
|  |  - Goal          |     +--------+---------+                    |
|  |  - Context       |              |                              |
|  |  - Strategy      |              v                              |
|  |  - Examples      |     +------------------+                    |
|  |  - Format        |     | STRATEGY MANAGER |                    |
|  +------------------+     |                  |                    |
|                           | - Monthly        |                    |
|                           | - Template       |                    |
|                           | - Cache          |                    |
|                           | - Forecast       |                    |
|                           | - Honeytoken     |                    |
|                           | - Vulnerability  |                    |
|                           | - Hybrid (rec.)  |                    |
|                           +--------+---------+                    |
|                                    |                              |
|                                    v                              |
|  +---------------------------------------------------------------+|
|  |              EXECUTION CORE (sys_core.py)                     ||
|  |  - Executes generated commands as personas                    ||
|  |  - Creates files, directories, git repos                      ||
|  |  - Updates bash_history with realistic timestamps             ||
|  |  - Handles errors with LLM-based self-correction              ||
|  +---------------------------------------------------------------+|
|          |                                                        |
|          v                                                        |
|  +---------------------------------------------------------------+|
|  |           ANTI-FINGERPRINTING SUBSYSTEM                       ||
|  |  - /proc file simulation (version, cpuinfo, mounts, etc.)     ||
|  |  - Attacker behavior detection (10+ fingerprint patterns)     ||
|  |  - Realistic timestamp generation (work-hour distribution)    ||
|  |  - Bash history with typos and natural gaps                   ||
|  +---------------------------------------------------------------+|
|          |                                                        |
|          v                                                        |
|  +---------------------------------------------------------------+|
|  |           OUTPUT: REALISTIC USER ENVIRONMENT                  ||
|  |  - /home/dev_alice (git repos, .bashrc, .vimrc, projects)     ||
|  |  - /home/sys_bob (monitoring scripts, logs, cron)             ||
|  |  - /var/lib/jenkins (CI workspace)                            ||
|  |  - Realistic /proc/* files                                    ||
|  +---------------------------------------------------------------+|
+------------------------------------------------------------------+
```

### Data Flow
1. **Planning Phase**: Monthly plan -> Weekly plan -> Daily tasks -> Individual commands
2. **Strategy Selection**: Hybrid mode probabilistically chooses generation method
3. **Command Generation**: LLM or cached templates produce command sequences
4. **Noise Injection**: Typos, status checks, navigation fluff added
5. **Execution**: Commands run as appropriate user, files created
6. **Recording**: Bash history updated with timestamps, metrics collected
7. **Adaptation**: Fingerprinting detected -> threat level increases -> behavior adapts

---

## 3. File Structure & Module Purposes

```
project/
├── sys_core.py              # Main orchestrator (900 lines)
├── LLM_Provider.py          # Gemini API wrapper (640 lines)
├── ContentManager.py        # State & cache management (377 lines)
├── StrategyManager.py       # Strategy selection (304 lines)
├── AntiFingerprint.py       # /proc simulation & detection (600+ lines)
├── PromptEngine.py          # SPADE prompt construction (400+ lines)
├── UserArtifactGenerator.py # Home directory artifacts (550+ lines)
├── ActiveDefense.py         # Honeyport listeners (46 lines)
├── test_deception.py        # Unit tests (22 tests)
├── setup_linux.sh           # Deployment script (350+ lines)
├── config.json              # System configuration
├── worker-spec.json         # Persona definitions & static scenes
├── templates.json           # Content templates
├── triggers.json            # Cross-user reactive rules
├── monthly_plan.json        # Generated narrative arc (LLM-created)
├── content_cache.json       # Runtime cache (forecast queue, assets)
├── project_state.json       # Virtual project metadata
└── docs/
    ├── 1_PAPER_GAPS.md      # Research paper completion checklist
    ├── 2_DEPLOYMENT_GUIDE.md # Installation instructions
    ├── 3_TESTING_GUIDE.md   # Testing methodology
    └── 4_AI_CONTEXT.md      # This document
```

---

## 4. Module Deep Dive

### 4.1 sys_core.py - Main Orchestrator

**Purpose**: Central coordination hub that runs the entire deception cycle.

**Key Responsibilities**:
- Initialize all subsystems (LLM, Content Manager, Anti-Fingerprinting, etc.)
- Manage persona scheduling and activity selection
- Execute command sequences ("scenes") with error recovery
- Handle graceful shutdown via signals
- Implement 3-layer behavioral control:
  - **Layer 1 (Smart Timer)**: Work hours + probability -> determines if persona active
  - **Layer 2 (Script Picker)**: Selects static scenes or delegates to LLM
  - **Layer 3 (Story Planner)**: Narrative injection from monthly/daily tasks

**Command-Line Modes**:
```bash
python sys_core.py --dry-run              # Simulation without executing
python sys_core.py --loop --llm           # Continuous operation with LLM
python sys_core.py --strategy-hybrid      # Professional mode (recommended)
python sys_core.py --generate-monthly     # Create new monthly narrative arc
python sys_core.py --refresh-content      # Update dynamic assets
```

**Key Functions**:
- `main_loop()`: Primary execution loop (every 5-30 seconds)
- `execute_scene()`: Runs command sequence with error handling
- `_run_command_raw()`: Actual command execution via subprocess
- `get_monthly_task()`: Retrieves current day's task from plan

### 4.2 LLM_Provider.py - Gemini API Wrapper

**Purpose**: All LLM interactions mediated through single interface.

**Core Methods**:
| Method | Purpose |
|--------|---------|
| `generate_scene()` | Create single activity scene for a persona |
| `generate_batch_scenes()` | Batch generation for forecasting (10+ scenes) |
| `generate_monthly_plan()` | Create 30-day narrative arc with weekly breakdowns |
| `generate_weekly_plan()` | Derive 7-day objectives from monthly plan |
| `adapt_plan()` | Manager agent - decide CRUNCH vs CUT_SCOPE if behind |
| `generate_daily_plan()` | Granular task definition for specific day |
| `fix_code()` | Self-correction agent - rewrite broken code/commands |
| `evolve_persona()` | Change work hours, skills, or role subtly |
| `generate_breadcrumbs()` | Create fake logs/chat snippets to leak false info |

**Error Handling**:
- Robust JSON parsing (extracts from markdown code blocks)
- Exponential backoff for rate limiting (429 errors)
- Retry logic with 3 attempts per API call
- Fallback responses when API fails

### 4.3 StrategyManager.py - Strategy Selection

**Purpose**: Decides WHICH strategy to use and executes it.

**7 Strategies**:

| Strategy | Probability (Hybrid) | Description |
|----------|---------------------|-------------|
| LLM | 25% | Live LLM generation for dynamic content |
| Forecast | 20% | Pop from batch-generated queue |
| Template | 25% | Randomize templates with fuzzing |
| Cache | 20% | Use pre-made cached scenarios |
| Honeytoken | 5% | Plant fake credentials (.aws, .ssh) |
| Vulnerability | 2% | Simulate bad security (chmod 777) |
| Auto-refresh | 2% | Content refresh, persona evolution, breadcrumbs |

**Sub-Factories**:
- `HoneytokenFactory`: Generates fake API keys (Google, GitHub, AWS style)
- `VulnerabilityFeint`: Creates vulnerable commands
- `ContextualNoise`: Injects realism (navigation fluff, status checks, typos)

### 4.4 AntiFingerprint.py - Honeypot Resistance

**Purpose**: Defend against attacker probing and make system appear genuinely Unix-like.

**Classes**:

**AntiFingerprintManager** - Generates realistic /proc files:
- `/proc/version`: Realistic kernel version with GCC info
- `/proc/cpuinfo`: Multi-core CPU (Intel/AMD, cache sizes)
- `/proc/meminfo`: Memory distribution patterns
- `/proc/uptime`: 1-90 day uptimes
- `/proc/loadavg`: Realistic system load
- `/proc/mounts`: Avoids honeypot signatures (no hostfs, no UML markers)
- `/proc/cmdline`: No "uml" boot parameter
- `/etc/os-release`: Ubuntu/Debian distro info

**AttackerBehaviorDetector** - Detects fingerprinting patterns:
| Pattern | Detection |
|---------|-----------|
| Cowrie detection | `busybox dd if=$SHELL bs=22 count=1` |
| Binary inspection | `cat /proc/self/exe` |
| UML detection | `/proc/mounts \| grep hostfs` |
| Shell fingerprinting | `echo $SHELL \| md5sum` |
| Init process check | `/proc/1/exe` |

Maintains threat level accumulation: none -> low -> medium -> high

**BashHistoryManager** - Maintains per-persona bash history:
- UNIX timestamps (HISTTIMEFORMAT style)
- Realistic command gaps
- Typo injection (10% probability)
- Proper file permissions (600)

**RealisticTimestampManager**:
- Work hours (9 AM - 5 PM typical)
- Gaussian distribution during work hours
- Occasional off-hours anomalies

### 4.5 PromptEngine.py - SPADE-Based Prompting

**Purpose**: Construct superior LLM prompts using academic SPADE framework.

**SPADE Framework (6 Components)**:
1. **Identity/Persona**: Detailed role (Senior Dev, SysAdmin, CI Bot)
2. **Goal/Task**: Explicit outcome definition
3. **Threat Context**: Current day, narrative arc, threat level
4. **Strategy Outline**: Work hours, tools, behavior style
5. **Output Examples**: Few-shot templates for consistency
6. **Output Format**: Exact JSON schema expected

**PersonaProfile** (Dataclass):
```python
@dataclass
class PersonaProfile:
    name: str                    # "dev_alice"
    full_name: str               # "Alice Chen"
    title: str                   # "Senior Backend Developer"
    seniority: str               # "senior"
    department: str              # "Engineering"
    communication_style: str     # "technical, concise"
    skills: List[str]            # ["Python", "FastAPI", "PostgreSQL", ...]
    tools: List[str]             # ["vim", "git", "docker", ...]
    common_tasks: List[str]      # ["API development", "code review", ...]
    work_hours: Tuple[int, int]  # (9, 17)
```

**ContextState** (Dataclass):
```python
@dataclass
class ContextState:
    current_day: int             # 1-30
    narrative_arc: str           # "API Security Hardening"
    daily_task: str              # "Implement OAuth2 flow"
    recent_commands: List[str]   # Last 10 executed
    files_modified: List[str]    # Recent code changes
    current_project: str         # "backend-api"
    build_status: str            # "passing", "failing"
    threat_level: str            # "none", "low", "medium", "high"
    fingerprint_detected: bool   # Adapt if True
```

### 4.6 UserArtifactGenerator.py - Home Directory Artifacts

**Purpose**: Create convincing user home directory artifacts.

**Generated Artifacts**:
- `.bashrc` / `.bash_profile`: Custom aliases, history settings, PATH
- `.bash_history`: Complete command history with timestamps
- `.gitconfig`: Git user configuration
- `.vimrc`: Vim editor customization
- `.ssh/`: SSH directory with known_hosts, config
- Cron jobs: Scheduled tasks relevant to persona
- Project artifacts: README.md, requirements.txt, configs
- Shell aliases: Role-specific shortcuts

**Persona-Specific Content**:
| Persona | Artifacts |
|---------|-----------|
| dev_alice | Python/Node.js setup, docker aliases, project structure |
| sys_bob | System monitoring aliases, safety-conscious (rm -i) |
| svc_ci | Jenkins-style workspace, minimal customization |

### 4.7 ContentManager.py - State Management

**Purpose**: Persistent storage of generated content, personas, and project state.

**Key Features**:
- **Forecast Queue**: Pre-generated scenes for quick replay
- **Asset Cache**: Vulnerability patterns and honeytoken templates
- **Project State Brain**: Tracks virtual project (files, build status)
- **Persona Evolution**: 6-month cooldown for skill/role changes
- **Dynamic Triggers**: Cross-user reactive rules

**State Files**:
| File | Purpose |
|------|---------|
| `content_cache.json` | Forecast queue, assets, personas, breadcrumbs |
| `project_state.json` | Virtual project metadata |
| `config.json` | System configuration |
| `worker-spec.json` | Static persona definitions |

### 4.8 ActiveDefense.py - Honeyport Detection

**Purpose**: Detect network scanners and log alerts.

**Implementation**:
- Spawns daemon threads on configured ports (8080, 2222, 2121)
- Responds with fake banner: "Internal Service Error 500"
- Logs connection attempts with source IP
- Non-blocking, asynchronous

---

## 5. Personas

| Persona | Role | Home Directory | Work Hours | Typical Commands |
|---------|------|----------------|------------|------------------|
| dev_alice | Senior Backend Developer | /home/dev_alice | 9-17 | git, vim, python, npm, docker |
| sys_bob | System Administrator | /home/sys_bob | 8-16 | systemctl, journalctl, htop, iptables |
| svc_ci | CI/CD Service | /var/lib/jenkins | 0-23 | build, test, deploy scripts |

---

## 6. Configuration Reference

### Environment Variables (.env)
```bash
GEMINI_API_KEY=AIzaSy...           # Required
GEMINI_MODEL=gemini-1.5-flash      # Optional, default shown
CONFIG_DIR=/opt/sys_integrity/config
```

### config.json
```json
{
  "active_defense": {
    "ports": [8080, 2222, 2121],
    "banner": "Internal Service Error 500: Check Logs\n"
  },
  "simulation": {
    "promotion_cooldown_days": 180,
    "promotion_chance": 0.10,
    "loop_sleep_min": 5,
    "loop_sleep_max": 20
  },
  "llm": {
    "default_model": "gemini-1.5-flash",
    "deep_coding_chance": 0.2,
    "high_volume_chance": 0.3
  }
}
```

### worker-spec.json (Persona Definitions)
```json
{
  "dev_alice": {
    "home_dir": "/home/dev_alice",
    "work_hours": [9, 17],
    "scenes": [
      {
        "name": "Routine Coding",
        "category": "Routine",
        "zone": "/home/dev_alice/projects/api",
        "commands": ["git pull", "vim src/main.py", "pytest"]
      }
    ]
  }
}
```

### monthly_plan.json (LLM-Generated)
```json
{
  "month": "January",
  "narrative_arc": "API Security Hardening Initiative",
  "goal_description": "Implement OAuth2, rate limiting, WAF",
  "weekly_high_level_goals": [
    "Week 1: Planning & Threat Modeling",
    "Week 2: OAuth2 Implementation",
    "Week 3: Testing & Integration",
    "Week 4: Deployment & Monitoring"
  ],
  "daily_tasks": {
    "1": "Design OAuth2 flow",
    "2": "Implement token service",
    "3": "Add refresh token logic"
  }
}
```

### triggers.json (Cross-User Events)
```json
[
  {
    "source": "dev_alice",
    "pattern": "git push",
    "event": "code_deployed",
    "target": "sys_bob",
    "scene_keyword": "restart_service"
  }
]
```

---

## 7. Execution Flow

### Main Loop (Every 5-30 seconds)
```
1. HIERARCHICAL PLANNING
   ├─ Ensure monthly_plan.json exists
   ├─ Ensure project_state.json exists
   ├─ Calculate current_day, current_week
   └─ Check if adaptive replanning needed (every 5 days)

2. PER-PERSONA EXECUTION
   FOR EACH persona (dev_alice, sys_bob, svc_ci):
     a. Check triggers -> forced scene if matched
     b. Schedule filter -> skip if outside work hours
     c. Strategy selection -> choose generation method
     d. Noise injection -> add typos, status checks
     e. Execution with feedback loop:
        ├─ Execute each command
        ├─ On failure: ask LLM to fix
        ├─ Retry up to 3 times
        ├─ Update bash history
        └─ Record metrics

3. TIME ADVANCEMENT
   └─ Sleep 5-30 seconds (with jitter)
```

### Attack Detection Flow
```
Attacker runs: cat /proc/self/exe

1. Command executed by sys_core
2. AttackerBehaviorDetector.analyze_command()
   └─ Pattern match: "binary_inspection"
   └─ threat_level: "none" -> "low"
3. Metrics recorded (fingerprint=True)
4. Next LLM prompt includes threat_level="low"
5. Behavior adapts to be more defensive
6. Log: "[SECURITY] Fingerprinting detected"
```

---

## 8. Testing

### Unit Tests (test_deception.py)
| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestAntiFingerprintManager | 5 | /proc file generation |
| TestAttackerBehaviorDetector | 4 | Fingerprint detection |
| TestBashHistoryManager | 3 | History management |
| TestSPADEPromptEngine | 3 | Prompt construction |
| TestUserArtifactGenerator | 3 | Artifact creation |
| TestMetricsCollector | 2 | Metrics recording |
| TestIntegration | 2 | Module integration |

**Run**: `python test_deception.py` (expect 22 PASS)

### Manual Verification
```bash
# Check generated files
cat /home/dev_alice/.bash_history | tail -20
cat /home/dev_alice/.bashrc
ls -la /home/sys_bob/

# Check /proc simulation
cat /proc/version
cat /proc/cpuinfo | head -20

# Test dry run
python sys_core.py --dry-run --llm --strategy-hybrid
```

---

## 9. API Reference

### LLMProvider
```python
provider = LLMProvider()
scene = provider.generate_scene(persona_name, persona_data, context)
plan = provider.generate_monthly_plan(project_context)
fixed = provider.fix_code(command, error_message, file_context)
```

### AntiFingerprintManager
```python
manager = AntiFingerprintManager()
content = manager.get_proc_file("/proc/version")
content = manager.get_system_file("/etc/os-release")
```

### AttackerBehaviorDetector
```python
detector = AttackerBehaviorDetector()
result = detector.analyze_command("cat /proc/self/exe")
# Returns: {"pattern": "binary_inspection", ...} or None
threat = detector.get_threat_level()  # "none"|"low"|"medium"|"high"
```

### SPADEPromptEngine
```python
engine = SPADEPromptEngine()
context = ContextState(current_day=15, narrative_arc="Security Audit", ...)
prompt = engine.build_prompt("dev_alice", context)
```

### BashHistoryManager
```python
manager = BashHistoryManager("dev_alice", "/home/dev_alice", config)
manager.add_command("git status")
manager.flush_to_file()
```

### ContentManager
```python
cm = ContentManager(config_dir="/opt/sys_integrity/config")
scene = cm.get_next_forecast_scene()
asset = cm.get_random_asset("honeytoken")
cm.update_file_index("/home/dev_alice/src/api.py", "REST endpoints")
```

### StrategyManager
```python
sm = StrategyManager(orchestrator)
result = sm.select_strategy("hybrid")
# Returns: ("LLM_DELEGATE", "dev_alice") or ("dev_alice", scene_dict)
commands = sm.apply_noise(original_commands)
```

---

## 10. Research Paper Context

### Paper Title
"MIRAGE: LLM-Driven Deception Through Dynamic Persona Simulation" (working title)

### Key Research Contributions
1. **Proactive Generation**: Creates activity before attackers arrive (vs reactive)
2. **SPADE Prompting**: Structured prompt framework for consistent output
3. **Multi-Persona Simulation**: 3 distinct behavioral profiles
4. **Anti-Fingerprinting**: Comprehensive /proc simulation, detection evasion
5. **Adaptive Behavior**: Threat detection triggers behavioral changes

### Evaluation Metrics
| Metric | How Measured |
|--------|--------------|
| Content Quality | Expert ratings (1-5 Likert scale) |
| Fingerprint Resistance | % of fingerprint techniques evaded |
| Temporal Realism | KL divergence from real user patterns |
| Work-hour Compliance | % of activity during expected hours |

### Paper Gaps (Need to Fill)
1. **HIGH**: Expert assessment study (8-15 security professionals)
2. **HIGH**: Deployment duration [M] weeks (actual runtime data)
3. **MEDIUM**: Overhead measurements (API calls, storage, CPU)
4. **MEDIUM**: Architecture figure (visual diagram)
5. **LOW**: Author information, acknowledgments

See `docs/1_PAPER_GAPS.md` for detailed checklist.

---

## 11. Known Issues & Limitations

### Current Limitations
1. **Linux Only**: No Windows/macOS support
2. **Single LLM**: Only Google Gemini supported
3. **English Only**: Commands and content in English
4. **3 Personas**: Fixed persona count (dev, admin, CI)
5. **Rate Limits**: Gemini API has quotas that may throttle generation

### Known Bugs
- Occasional JSON parsing failures from LLM (handled with retry)
- Forecast queue can deplete under heavy usage
- Some /proc files may not match very new kernel versions

### Security Considerations
- API key stored in .env file (permissions 600)
- Honeytokens are fake but look real - don't leak them
- System runs with persona user permissions, not root for commands

---

## 12. Extension Points

### Adding a New Persona
1. Add definition to `worker-spec.json`
2. Create home directory in `setup_linux.sh`
3. Add `PersonaProfile` in `PromptEngine.py`
4. Update persona list in `config.json`

### Adding New /proc Files
1. Add method in `AntiFingerprintManager` class
2. Add to `get_proc_file()` dispatcher
3. Test with fingerprinting tools

### Adding New Fingerprint Detection
1. Add pattern to `AttackerBehaviorDetector.PATTERNS`
2. Assign threat level increment
3. Add test case

### Changing LLM Provider
1. Implement new provider class with same interface
2. Key methods: `generate_scene()`, `generate_monthly_plan()`, `fix_code()`
3. Update environment variable handling

### Adding New Strategy
1. Add method in `StrategyManager`
2. Add to `select_strategy()` dispatcher
3. Update hybrid probabilities if needed

---

## 13. Quick Command Reference

### Development
```bash
# Test dry run
python sys_core.py --dry-run --llm --strategy-hybrid

# Generate new monthly plan
python sys_core.py --generate-monthly

# Run unit tests
python test_deception.py

# Manual LLM test
python -c "from LLM_Provider import LLMProvider; p = LLMProvider(); print(p.generate_scene('dev_alice', {'home_dir': '/home/dev_alice'}, {}))"
```

### Production
```bash
# Install
sudo ./setup_linux.sh install

# Configure
sudo nano /opt/sys_integrity/config/.env

# Start service
sudo systemctl enable --now sys-integrity-daemon

# Check status
sudo systemctl status sys-integrity-daemon

# View logs
tail -f /opt/sys_integrity/logs/sys_monitor.log

# Refresh content
sudo /opt/sys_integrity/refresh-content.sh
```

### Debugging
```bash
# Check generated artifacts
cat /home/dev_alice/.bash_history | tail -30
ls -la /home/dev_alice/
cat /home/sys_bob/.bashrc

# Check /proc simulation
cat /proc/version
cat /proc/cpuinfo | head -30

# Service logs
sudo journalctl -u sys-integrity-daemon -n 100
```

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Scene** | A sequence of commands representing a unit of activity |
| **Persona** | Simulated user identity with defined behavior profile |
| **Narrative Arc** | Month-long project story (e.g., "API Migration") |
| **SPADE** | Prompt framework: Situation, Persona, Action, Details, Examples |
| **Forecast Queue** | Pre-generated scenes for quick retrieval |
| **Honeytoken** | Fake credential designed to alert on use |
| **Fingerprinting** | Attacker technique to detect honeypots |
| **Threat Level** | Accumulated suspicion score from detected attacks |
| **Hybrid Strategy** | Probabilistic mix of all generation methods |

---

## 15. Version Information

- **Python**: 3.8+
- **LLM**: Google Gemini (gemini-1.5-flash)
- **OS**: Linux (Ubuntu 20.04+ / Debian 11+)
- **Service**: systemd (sys-integrity-daemon)
- **Dependencies**: google-generativeai

---

## 16. For AI Assistants: Improvement Areas

When asked to help improve this system, consider:

### Code Quality
- Type hints are incomplete in several modules
- Some functions exceed 50 lines and could be refactored
- Error handling could be more consistent across modules

### Security
- Add input validation for LLM-generated commands before execution
- Consider sandboxing command execution
- Add audit logging for sensitive operations

### Testing
- Integration tests for full pipeline are minimal
- No performance/load testing
- Mock tests for LLM responses would improve CI speed

### Features
- Multi-LLM support (OpenAI, Claude, local models)
- Windows/macOS support
- Web dashboard for monitoring
- Real-time metrics visualization
- Automated persona profile generation

### Research Paper
- Complete expert assessment study
- Add deployment case study
- Measure actual overhead metrics
- Create publication-quality architecture diagram
- Document failure modes and edge cases

---

*Document last updated: January 2026*
*For the latest code, refer to the actual source files.*
