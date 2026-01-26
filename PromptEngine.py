"""
PromptEngine.py - SPADE-Style Structured Prompt Engineering

Based on the SPADE framework from:
"SPADE: Enhancing Adaptive Cyber Deception Strategies with Generative AI
 and Structured Prompt Engineering" (arXiv 2501.00940)

The SPADE framework uses six components for structured prompts:
1. Identity/Persona - Domain-specific role assignment
2. Goal/Task - Explicit outcome definition
3. Threat Context - Environmental and threat intelligence
4. Strategy Outline - Operational constraints and tactics
5. Output Examples - Few-shot prompting templates
6. Output Format - Deployment-ready specifications

This module provides superior prompt construction for realistic deception.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PersonaProfile:
    """Detailed persona profile for prompt construction."""
    name: str
    full_name: str
    role: str
    department: str
    seniority: str
    skills: List[str]
    work_hours: tuple
    communication_style: str
    common_tasks: List[str]
    tools: List[str]
    home_dir: str


@dataclass
class ContextState:
    """Current context state for the deception system."""
    current_day: int
    narrative_arc: str
    daily_task: str
    recent_commands: List[str]
    files_modified: List[str]
    current_project: str
    build_status: str
    threat_level: str = "none"
    fingerprint_detected: bool = False


@dataclass
class SPADEPrompt:
    """SPADE-style structured prompt."""
    identity: str
    goal: str
    threat_context: str
    strategy: str
    examples: str
    output_format: str

    def render(self) -> str:
        """Render the complete prompt."""
        return f"""# SYSTEM INSTRUCTION: CYBER DECEPTION ENGINE

## 1. IDENTITY & PERSONA
{self.identity}

## 2. GOAL & TASK
{self.goal}

## 3. THREAT CONTEXT
{self.threat_context}

## 4. STRATEGY & CONSTRAINTS
{self.strategy}

## 5. OUTPUT EXAMPLES
{self.examples}

## 6. OUTPUT FORMAT
{self.output_format}
"""


class SPADEPromptEngine:
    """
    Advanced prompt engine using SPADE framework.

    Key improvements over basic prompts:
    - Structured six-component format
    - Context-aware generation
    - Few-shot examples for consistency
    - Threat-adaptive behavior
    """

    # Detailed persona profiles
    PERSONA_PROFILES = {
        "dev_alice": PersonaProfile(
            name="dev_alice",
            full_name="Alice Chen",
            role="Senior Backend Developer",
            department="Engineering",
            seniority="Senior (5+ years)",
            skills=["Python", "Go", "Docker", "Kubernetes", "PostgreSQL", "Redis", "Git"],
            work_hours=(9, 17),
            communication_style="Concise, technical, uses abbreviated commands",
            common_tasks=[
                "Feature development",
                "Code review",
                "Bug fixes",
                "API development",
                "Database optimization",
                "Testing",
                "Documentation"
            ],
            tools=["vim", "git", "docker", "kubectl", "python", "pytest", "make"],
            home_dir="/home/dev_alice"
        ),
        "sys_bob": PersonaProfile(
            name="sys_bob",
            full_name="Robert Martinez",
            role="Senior Systems Administrator",
            department="Infrastructure",
            seniority="Senior (8+ years)",
            skills=["Linux", "Bash", "Ansible", "Terraform", "AWS", "Monitoring", "Security"],
            work_hours=(8, 16),
            communication_style="Methodical, checks status frequently, safety-conscious",
            common_tasks=[
                "System monitoring",
                "Log analysis",
                "Backup management",
                "Security updates",
                "User management",
                "Incident response",
                "Capacity planning"
            ],
            tools=["systemctl", "journalctl", "ansible", "terraform", "vim", "grep", "awk"],
            home_dir="/home/sys_bob"
        ),
        "svc_ci": PersonaProfile(
            name="svc_ci",
            full_name="Jenkins CI Bot",
            role="Automated CI/CD Pipeline",
            department="DevOps",
            seniority="N/A (Automated)",
            skills=["Build", "Test", "Deploy", "Docker", "Notifications"],
            work_hours=(0, 23),  # 24/7
            communication_style="Automated, structured output, log-heavy",
            common_tasks=[
                "Build artifacts",
                "Run test suites",
                "Deploy to staging",
                "Deploy to production",
                "Send notifications",
                "Cleanup old artifacts"
            ],
            tools=["mvn", "gradle", "docker", "kubectl", "make", "npm", "pytest"],
            home_dir="/var/lib/jenkins"
        )
    }

    # Few-shot examples for consistent output
    FEW_SHOT_EXAMPLES = {
        "developer": [
            {
                "name": "Feature Development - Add User Authentication",
                "category": "Routine",
                "zone": "/home/dev_alice/repos/backend-api",
                "commands": [
                    "cd /home/dev_alice/repos/backend-api",
                    "git status",
                    "git checkout -b feature/user-auth",
                    "vim src/auth/handlers.py",
                    "python -m pytest tests/auth/ -v",
                    "git add src/auth/",
                    "git commit -m 'feat: implement JWT authentication handler'"
                ]
            },
            {
                "name": "Bug Fix - Database Connection Pool",
                "category": "Variant",
                "zone": "/home/dev_alice/repos/backend-api",
                "commands": [
                    "cd /home/dev_alice/repos/backend-api",
                    "git log --oneline -5",
                    "grep -r 'connection_pool' src/",
                    "vim src/db/pool.py",
                    "python -m pytest tests/db/ -v",
                    "git diff",
                    "git add -p",
                    "git commit -m 'fix: increase connection pool timeout to 30s'"
                ]
            },
            {
                "name": "Emergency Hotfix - Auth Bypass",
                "category": "Anomaly",
                "zone": "/home/dev_alice/repos/backend-api",
                "commands": [
                    "cd /home/dev_alice/repos/backend-api",
                    "git stash",
                    "git checkout main",
                    "git pull origin main",
                    "git checkout -b hotfix/auth-bypass-CVE-2024-1234",
                    "vim src/auth/middleware.py",
                    "python -m pytest tests/auth/test_security.py -v",
                    "git add .",
                    "git commit -m 'security: fix authentication bypass vulnerability'",
                    "git push origin hotfix/auth-bypass-CVE-2024-1234"
                ]
            }
        ],
        "sysadmin": [
            {
                "name": "Daily System Health Check",
                "category": "Routine",
                "zone": "/home/sys_bob",
                "commands": [
                    "uptime",
                    "df -h",
                    "free -h",
                    "systemctl status nginx",
                    "systemctl status postgresql",
                    "tail -20 /var/log/nginx/error.log",
                    "journalctl -u nginx --since '1 hour ago' --no-pager"
                ]
            },
            {
                "name": "Log Rotation and Backup",
                "category": "Variant",
                "zone": "/var/log",
                "commands": [
                    "cd /var/log",
                    "ls -lh *.log",
                    "sudo logrotate -f /etc/logrotate.conf",
                    "tar -czf /backup/logs-$(date +%Y%m%d).tar.gz *.log.1",
                    "find /backup -name 'logs-*.tar.gz' -mtime +30 -delete",
                    "ls -lh /backup/"
                ]
            },
            {
                "name": "Security Incident - Unauthorized Access Attempt",
                "category": "Anomaly",
                "zone": "/home/sys_bob",
                "commands": [
                    "sudo grep 'Failed password' /var/log/auth.log | tail -50",
                    "sudo fail2ban-client status sshd",
                    "sudo iptables -L -n | head -30",
                    "last -20",
                    "who",
                    "ps aux | grep -E 'ssh|nc|ncat'",
                    "sudo netstat -tulpn | grep LISTEN"
                ]
            }
        ],
        "cicd": [
            {
                "name": "Build Pipeline - Main Branch",
                "category": "Routine",
                "zone": "/var/lib/jenkins/workspace/backend-api",
                "commands": [
                    "cd /var/lib/jenkins/workspace/backend-api",
                    "git fetch origin",
                    "git checkout main",
                    "git pull",
                    "make clean",
                    "make build",
                    "make test",
                    "docker build -t backend-api:${BUILD_NUMBER} .",
                    "docker push registry.internal/backend-api:${BUILD_NUMBER}"
                ]
            }
        ]
    }

    def __init__(self, personas: Dict = None, llm_provider=None):
        """Initialize the prompt engine."""
        self.personas = personas or {}
        self.llm_provider = llm_provider
        self._load_custom_profiles()

    def _load_custom_profiles(self):
        """Load custom persona profiles from configuration."""
        for name, data in self.personas.items():
            if name not in self.PERSONA_PROFILES:
                # Create a basic profile from config
                self.PERSONA_PROFILES[name] = PersonaProfile(
                    name=name,
                    full_name=name.replace('_', ' ').title(),
                    role=data.get('role', 'User'),
                    department="General",
                    seniority="Unknown",
                    skills=data.get('skills', []),
                    work_hours=tuple(data.get('work_hours', [9, 17])),
                    communication_style="Standard",
                    common_tasks=["General work"],
                    tools=["bash"],
                    home_dir=data.get('home_dir', f'/home/{name}')
                )

    def build_prompt(
        self,
        persona_name: str,
        context: ContextState,
        mode: str = "normal"
    ) -> str:
        """
        Build a SPADE-style structured prompt.

        Args:
            persona_name: The persona to generate commands for
            context: Current context state
            mode: Generation mode (normal, deep_work, quick, anomaly)

        Returns:
            Complete structured prompt string
        """
        profile = self.PERSONA_PROFILES.get(
            persona_name,
            self._create_default_profile(persona_name)
        )

        prompt = SPADEPrompt(
            identity=self._build_identity(profile),
            goal=self._build_goal(profile, context, mode),
            threat_context=self._build_threat_context(context),
            strategy=self._build_strategy(profile, context, mode),
            examples=self._build_examples(profile),
            output_format=self._build_output_format()
        )

        return prompt.render()

    def _create_default_profile(self, name: str) -> PersonaProfile:
        """Create a default profile for unknown personas."""
        return PersonaProfile(
            name=name,
            full_name=name.replace('_', ' ').title(),
            role="User",
            department="General",
            seniority="Unknown",
            skills=["bash"],
            work_hours=(9, 17),
            communication_style="Standard",
            common_tasks=["General tasks"],
            tools=["bash", "vim"],
            home_dir=f"/home/{name}"
        )

    def _build_identity(self, profile: PersonaProfile) -> str:
        """Build the identity/persona section."""
        return f"""You are simulating **{profile.full_name}**, a {profile.seniority} {profile.role} at a technology company.

**Profile:**
- Username: `{profile.name}`
- Department: {profile.department}
- Home Directory: `{profile.home_dir}`
- Work Hours: {profile.work_hours[0]}:00 - {profile.work_hours[1]}:00

**Technical Skills:** {', '.join(profile.skills)}

**Communication Style:** {profile.communication_style}

**Primary Tools:** {', '.join(profile.tools)}

**CRITICAL:** You must behave EXACTLY like this person. Your commands should reflect their expertise level, habits, and role-specific tasks. An attacker analyzing the logs should believe this is a real person."""

    def _build_goal(self, profile: PersonaProfile, context: ContextState, mode: str) -> str:
        """Build the goal/task section with dynamic paths."""
        # Generate dynamic paths for this persona
        dynamic_paths = {}
        if self.llm_provider:
            try:
                dynamic_paths = self.llm_provider.generate_dynamic_paths(
                    profile.name, 
                    {"home_dir": profile.home_dir}, 
                    {"monthly_arc": context.narrative_arc, "daily_task": context.daily_task}
                )
            except Exception as e:
                logger.warning(f"Failed to generate dynamic paths for {profile.name}: {e}")
                dynamic_paths = self._get_fallback_paths(profile)

        base_goal = f"""Generate a realistic sequence of shell commands that {profile.full_name} would execute right now.

**Current Context:**
- Project Day: {context.current_day}/30
- Monthly Initiative: "{context.narrative_arc}"
- Today's Focus: "{context.daily_task}"
- Build Status: {context.build_status}
- Current Project: {context.current_project}"""

        # Add dynamic environment information
        if dynamic_paths:
            base_goal += f"""

**WORKING ENVIRONMENT:**
- Current Workspace: {dynamic_paths.get('current_workspace', profile.home_dir)}"""
            
            if 'active_projects' in dynamic_paths:
                base_goal += f"""
- Active Projects: {', '.join(dynamic_paths['active_projects'])}"""
            
            if 'log_dirs' in dynamic_paths:
                base_goal += f"""
- System Logs: {', '.join(dynamic_paths['log_dirs'])}"""
            
            if 'workspaces' in dynamic_paths:
                base_goal += f"""
- Build Workspaces: {', '.join(dynamic_paths['workspaces'])}"""

        if context.recent_commands:
            base_goal += f"""

**Recent Activity (last session):**
```
{chr(10).join(context.recent_commands[-5:])}
```
Continue from where the user left off logically."""

        # Mode-specific goals
        mode_instructions = {
            "normal": """

Generate 4-7 commands representing a typical work segment (15-30 minutes of activity).""",

            "deep_work": """

**MODE: DEEP WORK SESSION**
Generate 8-15 commands representing intensive development work.
- Include actual file content creation using `cat <<EOF > filename`
- Show debugging steps, test runs, and commits
- The code you generate must be syntactically correct and relevant to the task""",

            "quick": """

**MODE: QUICK CHECK**
Generate 2-4 commands for a quick status check or small task.
- Brief session, checking status or making minor changes""",

            "anomaly": """

**MODE: INCIDENT RESPONSE**
Generate 5-10 commands responding to an anomaly or incident.
- Show investigation steps
- Include log analysis
- May include escalation or remediation"""
        }

        return base_goal + mode_instructions.get(mode, mode_instructions["normal"])

    def _build_threat_context(self, context: ContextState) -> str:
        """Build the threat context section."""
        base_context = """**Deception Objective:**
This system is a honeypot designed to deceive attackers. The commands you generate will be logged to `~/.bash_history` and executed to create realistic file system artifacts.

**Anti-Detection Requirements:**
1. Commands must be valid bash that will execute successfully
2. Use realistic file paths (avoid generic `/tmp/test.txt`)
3. Include natural variations (occasional typos corrected, status checks)
4. Time-appropriate activity (respect work hours patterns)
5. Maintain consistency with previous sessions"""

        if context.fingerprint_detected:
            base_context += """

**ALERT: Fingerprinting Attempt Detected**
Threat Level: {context.threat_level}
Adjust behavior to appear more realistic. Avoid patterns that reveal simulation."""

        return base_context

    def _build_strategy(self, profile: PersonaProfile, context: ContextState, mode: str) -> str:
        """Build the strategy/constraints section."""
        return f"""**Operational Constraints:**
1. All paths must be absolute or relative to `{profile.home_dir}`
2. Commands must be executable on Ubuntu 22.04 LTS
3. Avoid commands requiring sudo unless the persona is an admin
4. Include realistic command patterns:
   - Navigation before action (`cd`, `ls`, `pwd`)
   - Status checks (`git status`, `docker ps`)
   - Occasional corrections (typo -> correct command)
   - Comments in complex pipelines

**Realism Tactics:**
- 70% Routine tasks (status checks, builds, edits)
- 20% Variant tasks (debugging, investigation)
- 10% Anomalies (incidents, urgent fixes)

**Forbidden Patterns (honeypot tells):**
- Do NOT use generic paths like `/tmp/test` or `/home/user`
- Do NOT use placeholder text like `<filename>` or `[YOUR_NAME]`
- Do NOT generate commands that would obviously fail
- Do NOT reference the honeypot, deception, or simulation"""

    def _build_examples(self, profile: PersonaProfile) -> str:
        """Build the few-shot examples section."""
        # Select appropriate examples based on role
        if "dev" in profile.name.lower():
            examples = self.FEW_SHOT_EXAMPLES["developer"]
        elif "sys" in profile.name.lower() or "admin" in profile.name.lower():
            examples = self.FEW_SHOT_EXAMPLES["sysadmin"]
        elif "svc" in profile.name.lower() or "ci" in profile.name.lower():
            examples = self.FEW_SHOT_EXAMPLES["cicd"]
        else:
            examples = self.FEW_SHOT_EXAMPLES["developer"]

        # Select 1-2 random examples
        selected = random.sample(examples, min(2, len(examples)))

        examples_str = "Here are examples of correctly formatted output:\n\n"
        for i, ex in enumerate(selected, 1):
            examples_str += f"""**Example {i}: {ex['name']}**
```json
{json.dumps(ex, indent=2)}
```

"""
        return examples_str

    def _build_output_format(self) -> str:
        """Build the output format specification."""
        return """**Required Output Format:**
Return ONLY valid JSON. No markdown, no explanation, no commentary.

```json
{
    "name": "Brief descriptive title (e.g., 'Implement User Authentication')",
    "category": "Routine" | "Variant" | "Anomaly",
    "zone": "/absolute/path/to/working/directory",
    "commands": [
        "command 1",
        "command 2",
        "command 3"
    ]
}
```

**Validation Rules:**
- `name`: 3-10 words describing the activity
- `category`: Must be one of the three options
- `zone`: Must be an absolute path that exists or can be created
- `commands`: Array of 3-15 valid bash commands"""

    def _get_fallback_paths(self, profile: PersonaProfile):
        """Fallback paths when LLM generation fails."""
        if "dev" in profile.name.lower():
            return {
                "active_projects": [f"{profile.home_dir}/repos/backend-api", f"{profile.home_dir}/repos/frontend"],
                "archived_projects": [f"{profile.home_dir}/archive/old-projects"],
                "personal_dirs": [f"{profile.home_dir}/notes", f"{profile.home_dir}/scripts"],
                "config_files": [f"{profile.home_dir}/.gitconfig"],
                "current_workspace": f"{profile.home_dir}/repos/backend-api"
            }
        elif "sys" in profile.name.lower() or "admin" in profile.name.lower():
            return {
                "log_dirs": ["/var/log", "/var/log/nginx"],
                "config_dirs": ["/etc/nginx", "/etc/ssh"],
                "backup_dirs": ["/mnt/backup"],
                "monitoring_scripts": [f"{profile.home_dir}/scripts/monitor.sh"],
                "current_workspace": "/var/log"
            }
        elif "svc" in profile.name.lower() or "ci" in profile.name.lower():
            return {
                "workspaces": ["/var/lib/jenkins/workspace/backend-api"],
                "artifacts": ["/var/lib/jenkins/artifacts"],
                "scripts": ["/var/lib/jenkins/scripts/deploy.sh"],
                "current_workspace": "/var/lib/jenkins/workspace/backend-api"
            }
        else:
            return {
                "personal_dirs": [f"{profile.home_dir}/documents"],
                "config_files": [f"{profile.home_dir}/.bashrc"],
                "current_workspace": profile.home_dir
            }


class AdaptivePromptSelector:
    """
    Selects and adapts prompts based on threat context.

    Implements adaptive behavior from the research:
    "If attacker reads logs → Simulate panic cleanup"
    "If attacker modifies code → Trigger bug discovery narrative"
    """

    def __init__(self, prompt_engine: SPADEPromptEngine):
        self.engine = prompt_engine
        self.threat_history = []

    def select_mode(self, context: ContextState) -> str:
        """Select generation mode based on context."""
        # Threat-adaptive selection
        if context.threat_level == "critical":
            return "anomaly"  # Simulate incident response
        elif context.threat_level == "high":
            return random.choice(["normal", "anomaly"])
        elif context.fingerprint_detected:
            return "deep_work"  # Generate more realistic, complex commands

        # Normal probability distribution
        roll = random.random()
        if roll < 0.60:
            return "normal"
        elif roll < 0.85:
            return "quick"
        elif roll < 0.95:
            return "deep_work"
        else:
            return "anomaly"

    def generate_adaptive_prompt(
        self,
        persona_name: str,
        context: ContextState
    ) -> str:
        """Generate a prompt adapted to current threat context."""
        mode = self.select_mode(context)

        # Record for analysis
        self.threat_history.append({
            "timestamp": datetime.now().isoformat(),
            "threat_level": context.threat_level,
            "mode_selected": mode,
            "fingerprint_detected": context.fingerprint_detected
        })

        return self.engine.build_prompt(persona_name, context, mode)
