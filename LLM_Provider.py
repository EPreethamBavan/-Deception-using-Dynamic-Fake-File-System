import os
import json
import logging
import random
import google.generativeai as genai
from dataclasses import dataclass

# Configure Logging
logger = logging.getLogger(__name__)

@dataclass
class GeneratedScene:
    name: str
    category: str
    zone: str
    commands: list

class LLMProvider:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"LLM Provider initialized with model: {self.model_name}")
        else:
            self.model = None
            logger.warning("No API Key provided. LLM Provider in MOCK mode.")
            
    def generate_dynamic_paths(self, persona_name, persona_data, context=None):
        """
        Generate realistic, dynamic working paths for a persona.
        This creates a 'living' environment that evolves over time.
        
        Returns a dict with various path categories for the persona.
        """
        home = persona_data.get('home_dir', f'/home/{persona_name}')
        
        if "dev" in persona_name:
            prompt = f"""
            **TASK:** Generate realistic working directories and project paths for a senior backend developer named {persona_name}.
            
            **CONTEXT:**
            - Home directory: {home}
            - Current month: {context.get('monthly_arc', 'Backend API Migration') if context else 'Backend API Migration'}
            - Current task: {context.get('daily_task', 'API development') if context else 'API development'}
            
            **REQUIREMENTS:**
            Generate 5-8 realistic project directories and file paths that this developer would use.
            Include a mix of active projects, archived work, and personal directories.
            
            **OUTPUT FORMAT:**
            Return STRICT JSON:
            {{
                "active_projects": [
                    "{home}/repos/backend-api",
                    "{home}/repos/frontend-app", 
                    "{home}/repos/core-services"
                ],
                "archived_projects": [
                    "{home}/archive/old-api-v1",
                    "{home}/archive/legacy-system"
                ],
                "personal_dirs": [
                    "{home}/notes",
                    "{home}/scripts",
                    "{home}/experiments"
                ],
                "config_files": [
                    "{home}/.gitconfig",
                    "{home}/.ssh/config",
                    "{home}/.aws/credentials"
                ],
                "current_workspace": "{home}/repos/backend-api"
            }}
            """
        elif "sys" in persona_name or "admin" in persona_name:
            prompt = f"""
            **TASK:** Generate realistic system administration paths for {persona_name}.
            
            **CONTEXT:**
            - Home directory: {home}
            - Role: Senior Systems Administrator
            - Current focus: Infrastructure maintenance and monitoring
            
            **OUTPUT FORMAT:**
            Return STRICT JSON:
            {{
                "log_dirs": ["/var/log", "/var/log/nginx", "/var/log/postgresql"],
                "config_dirs": ["/etc/nginx", "/etc/postgresql", "/etc/ssh"],
                "backup_dirs": ["/mnt/backup", "/mnt/backup/logs", "/mnt/backup/config"],
                "monitoring_scripts": ["{home}/scripts/monitor.sh", "{home}/scripts/backup.sh"],
                "current_workspace": "/var/log"
            }}
            """
        elif "svc" in persona_name or "ci" in persona_name:
            prompt = f"""
            **TASK:** Generate realistic CI/CD workspace paths for {persona_name}.
            
            **OUTPUT FORMAT:**
            Return STRICT JSON:
            {{
                "workspaces": ["/var/lib/jenkins/workspace/backend-api", "/var/lib/jenkins/workspace/frontend"],
                "artifacts": ["/var/lib/jenkins/artifacts", "/var/lib/jenkins/artifacts/releases"],
                "scripts": ["/var/lib/jenkins/scripts/deploy.sh", "/var/lib/jenkins/scripts/build.sh"],
                "current_workspace": "/var/lib/jenkins/workspace/backend-api"
            }}
            """
        else:
            # Generic user
            prompt = f"""
            **TASK:** Generate realistic user directories for {persona_name}.
            
            **OUTPUT FORMAT:**
            Return STRICT JSON:
            {{
                "personal_dirs": ["{home}/documents", "{home}/downloads", "{home}/projects"],
                "config_files": ["{home}/.bashrc", "{home}/.vimrc"],
                "current_workspace": "{home}"
            }}
            """
        
        response = self._call_llm(prompt)
        if response and isinstance(response, dict):
            return response
        
        # Fallback to static paths if LLM fails
        logger.warning(f"LLM path generation failed for {persona_name}, using fallbacks")
        return self._get_fallback_paths(persona_name, home)
    
    def _get_fallback_paths(self, persona_name, home):
        """Fallback paths when LLM generation fails."""
        if "dev" in persona_name:
            return {
                "active_projects": [f"{home}/repos/backend-api", f"{home}/repos/frontend"],
                "archived_projects": [f"{home}/archive/old-projects"],
                "personal_dirs": [f"{home}/notes", f"{home}/scripts"],
                "config_files": [f"{home}/.gitconfig"],
                "current_workspace": f"{home}/repos/backend-api"
            }
        elif "sys" in persona_name or "admin" in persona_name:
            return {
                "log_dirs": ["/var/log", "/var/log/nginx"],
                "config_dirs": ["/etc/nginx", "/etc/ssh"],
                "backup_dirs": ["/mnt/backup"],
                "monitoring_scripts": [f"{home}/scripts/monitor.sh"],
                "current_workspace": "/var/log"
            }
        elif "svc" in persona_name or "ci" in persona_name:
            return {
                "workspaces": ["/var/lib/jenkins/workspace/backend-api"],
                "artifacts": ["/var/lib/jenkins/artifacts"],
                "scripts": ["/var/lib/jenkins/scripts/deploy.sh"],
                "current_workspace": "/var/lib/jenkins/workspace/backend-api"
            }
        else:
            return {
                "personal_dirs": [f"{home}/documents"],
                "config_files": [f"{home}/.bashrc"],
                "current_workspace": home
            }

    def _call_llm(self, prompt, retries=3):
        """
        Call the LLM with retry logic and robust JSON parsing.

        Args:
            prompt: The prompt to send to the LLM
            retries: Number of retry attempts for rate limiting

        Returns:
            Parsed JSON response or None on failure
        """
        if not self.model:
            logger.error("LLM Call Failed: No API Key configured.")
            return None

        import re
        import time

        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                text = response.text

                # Robust JSON extraction
                # 1. Remove markdown code blocks
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*', '', text)
                text = text.strip()

                # 2. Try to find JSON object or array boundaries
                json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
                if json_match:
                    text = json_match.group(1)

                # 3. Parse JSON
                parsed = json.loads(text)

                # 4. Basic validation for scene objects
                if isinstance(parsed, dict):
                    # Ensure required fields exist for scene objects
                    if 'commands' in parsed:
                        if not isinstance(parsed['commands'], list):
                            parsed['commands'] = [str(parsed['commands'])]
                        # Filter out empty commands
                        parsed['commands'] = [c for c in parsed['commands'] if c and str(c).strip()]

                    # Ensure zone is absolute path
                    if 'zone' in parsed and not parsed['zone'].startswith('/'):
                        parsed['zone'] = '/tmp'

                return parsed

            except json.JSONDecodeError as e:
                logger.warning(f"JSON Parse Error (attempt {attempt+1}): {e}")
                logger.debug(f"Raw response: {text[:500]}...")

                # Try one more extraction method - find first { to last }
                try:
                    start = text.find('{')
                    end = text.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        return json.loads(text[start:end+1])
                except:
                    pass

                if attempt < retries - 1:
                    continue
                return None

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20s
                    logger.warning(f"LLM Rate Limit Hit. Waiting {wait_time}s before retry {attempt+1}/{retries}...")
                    time.sleep(wait_time)
                    continue

                logger.error(f"LLM Error: {e}")
                return None

        return None

    def generate_scene(self, persona_name, persona_data, context):
        """Generates a single scene (Standard Mode)."""
        prompt = self._construct_prompt(persona_name, persona_data, context)
        return self._call_llm(prompt)

    def generate_batch_scenes(self, count=10):
        """Generates a batch of scenes for forecasting."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Cyber Deception Architect simulating a realistic company network traffic.
        
        **TASK:**
        Generate {count} unique command-line activity scenes for a mix of personas:
        - `dev_alice` (Backend Developer)
        - `sys_bob` (Sysadmin)
        - `svc_ci` (CI/CD Bot)
        
        **REQUIREMENTS:**
        - Create a coherent narrative (e.g., Alice commits code -> CI builds it -> Bob restarts service).
        - Use realistic file paths and tool arguments.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON list of objects:
        [
            {{
                "user": "dev_alice",
                "name": "Short Scene Description",
                "category": "Routine" | "Variant" | "Anomaly",
                "zone": "/absolute/path/to/workdir",
                "commands": ["cmd1", "cmd2"]
            }},
            ...
        ]
        """
        response = self._call_llm(prompt)
        # _call_llm might return a single dict if it parsed that way, force list expectation
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "scenes" in response:
            return response["scenes"]
        return [response] if response else []

    def generate_content_assets(self, asset_type):
        """Generates raw assets for ContentManager (vulnerabilities, honeytokens)."""
        if asset_type == "vuln":
            prompt = """
            **TASK:** Generate 10 realistic 'Human Errors' or 'Vulnerabilities' for a deception environment.
            **CONTEXT:** These will be planted to tempt attackers.
            **EXAMPLES:** `chmod 777`, exposing keys in `.bash_history`, disabling ufw.
            
            **OUTPUT format:**
            Return STRICT JSON List of strings (command sequences):
            ["chmod 777 /var/www/html", "echo 'AWS_KEY=AKIA...' >> ~/.bashrc", ...]
            """
        elif asset_type == "honeytoken":
            prompt = """
            **TASK:** Generate 10 sets of commands to create 'Honeytokens' (Fake Secrets).
            **CONTEXT:** These files should look valuable to an attacker but trigger alerts when read.
            **EXAMPLES:** `config.json` with fake DB creds, `id_rsa` keys, `aws_credentials`.
            
            **OUTPUT FORMAT:**
            Return STRICT JSON List of strings:
            ["echo 'DB_PASS=...' > config.json", "ssh-keygen -f id_rsa -N ''", ...]
            """
        else:
            return []



    def generate_monthly_plan(self):
        """Generates a cohesive narrative plan for the month."""
        prompt = """
        **SYSTEM ROLE:**
        You are the Chief Technical Architect for a medium-sized technology company. 
        Your goal is to define a month-long engineering initiative ("Narrative Arc") that provides context for 30 days of development activity.
        
        **CONTEXT:**
        - The "Deception Engine" uses this plan to generate realistic git commits and server logs.
        - The arc must be realistic (e.g., "Migration from AWS to Azure", "Major Refactor of Auth Service", "Security Compliance Sprint").
        
        **TASK:**
        Generate a 'Monthly Work Plan'.
        
        **INSTRUCTIONS:**
        1. Choose a realistic theme/arc.
        2. Define a clear goal description.
        3. Break it down into 4 high-level weekly goals.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON in the following format:
        {
            "month": "Current Month",
            "narrative_arc": "Title of the Initiative",
            "goal_description": "Brief description of the technical objectives.",
            "weekly_high_level_goals": [
                "Week 1: [Goal]",
                "Week 2: [Goal]",
                "Week 3: [Goal]",
                "Week 4: [Goal]"
            ]
        }
        """
        response = self._call_llm(prompt)
        if isinstance(response, dict): return response
        return None

    def generate_weekly_plan(self, monthly_context, week_num):
        """Breaks down the monthly goal into granular weekly objectives."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are an Engineering Manager planning the upcoming sprint (Week {week_num}).
        
        **CONTEXT:**
        - Monthly Initiative: "{monthly_context.get('narrative_arc')}"
        - Goal Description: "{monthly_context.get('goal_description')}"
        
        **TASK:**
        Create a detailed day-by-day plan for Week {week_num} (Days 1-7 of this week).
        
        **INSTRUCTIONS:**
        - Ensure logical progression (e.g., Setup -> Dev -> Test -> Deploy).
        - 'expected_files' should be realistic file paths that might be touched.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON with a single key "days" containing a list of objects:
        {{
            "days": [
                {{
                    "day": "1",
                    "focus": "Brief Task Title (e.g., Setup Repo)",
                    "expected_files": ["README.md", "requirements.txt"]
                }},
                ...
            ]
        }}
        """
        response = self._call_llm(prompt)
        if isinstance(response, dict) and "days" in response: return response["days"]
        return []

    def adapt_plan(self, current_day, progress_summary, remaining_goal):
        """Re-plans the strategy if falling behind (The 'Manager' Agent)."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Project Manager facing a delay.
        
        **SITUATION:**
        - Current Day: {current_day}/30
        - Remaining Goal: {remaining_goal}
        - Status: {progress_summary} (e.g., 'Behind schedule')
        
        **TASK:**
        Decide on a recovery strategy and revise the upcoming schedule.
        
        **STRATEGIES:**
        1. CRUNCH: Increase code volume/intensity. (Use this if close to goal).
        2. CUT_SCOPE: Remove non-essential features. (Use this if excessively behind).
        
        **OUTPUT FORMAT:**
        Return STRICT JSON:
        {{
            "strategy": "CRUNCH" or "CUT_SCOPE",
            "reasoning": "Brief explanation of choice",
            "revised_daily_tasks": {{
                "day_{current_day+1}": "New Task Description",
                "day_{current_day+2}": "New Task Description"
            }}
        }}
        """
        return self._call_llm(prompt)

    def generate_daily_plan(self, week_context, prev_day_outcome):
        """Generates specific sub-tasks for the day based on yesterday."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Senior Developer planning your specific tasks for the day.
        
        **CONTEXT:**
        - Weekly Goal: {week_context}
        - Yesterday's Outcome: {prev_day_outcome}
        
        **TASK:**
        Define the EXACT technical task for today. 
        It must be granular and actionable (something that results in code or config).
        
        **OUTPUT FORMAT:**
        Return STRICT JSON:
        {{
            "task_name": "Technical Task Title (e.g., Implement UserAuth Class)",
            "target_files": ["List", "of", "files", "to", "touch"],
            "complexity": "High" or "Medium" or "Low"
        }}
        """
        return self._call_llm(prompt)
    
    def fix_code(self, code_snippet, error_message, file_context=None):
        """Self-Correction Agent: Rewrites code to fix a reported error."""
        context_block = ""
        if file_context:
            context_block = f"\nRELEVANT FILE CONTENT:\n```\n{file_context}\n```"

        prompt = f"""
        **SYSTEM ROLE:**
        You are an intelligent Code Correction Agent.
        
        **INPUT:**
        BROKEN COMMAND/CODE:
        ```python
        {code_snippet}
        ```
        
        ERROR MESSAGE:
        {error_message}
        {context_block}
        
        **TASK:**
        Fix the error. You can either provide a corrected COMMAND to run, OR provide the content to write to a FILE to fix the root cause.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON with one of these structures:
        
        OPTION A (Command Fix):
        {{
            "type": "command",
            "content": "adjusted command here"
        }}
        
        OPTION B (File Fix):
        {{
            "type": "file",
            "path": "/absolute/path/to/file",
            "content": "full new file content here" 
        }}
        """
        
        response = self._call_llm(prompt)
        if isinstance(response, dict): return response
        # Fallback for legacy simple string return or failure
        return {"type": "command", "content": code_snippet}

    def generate_motd(self, username, daily_task, current_day):
        """Generates a dynamic Message of the Day for a user's login session."""
        prompt = f"""
        User: {username}
        Project Day: {current_day}/30
        Today's Task: {daily_task}
        
        System: Generate a strictly realistic SSH 'Message of the Day' (MOTD) or `.bash_profile` welcome message for this developer.
        
        Requirements:
        - Include standard Corporate/Linux login flair (e.g., 'Ubuntu 22.04 LTS', 'System load', etc.).
        - Crucially: INSERT A REMINDER about the specific daily task.
        - Tone: Professional, slightly urgent or routine depending on context.
        
        Example Output:
        ```
        Welcome to DevNode-04 (Ubuntu 22.04.1 LTS)
        System Load: 0.12, 0.08, 0.05
        
        *** PROJECT UPDATE: DAY {current_day} ***
        > REMINDER: {daily_task} must be committed by 5 PM.
        > Build Status: PASSING
        ```
        
        Return ONLY the raw MOTD text.
        """
        response = self._call_llm(prompt)
        # Clean up if LLM wraps in JSON or code blocks (fallback)
        if isinstance(response, str):
            return response.replace("```", "").strip()
        return f"Welcome {username}.\nTask: {daily_task}"

    def evolve_persona(self, current_data):
        """Evolves a persona's role, shift, or skills based on current state."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Human Resources Simulation Engine.
        
        **CONTEXT:**
        Current Persona Profile:
        {json.dumps(current_data, indent=2)}
        
        **TASK:**
        Simulate a realistic career or life evolution for this employee.
        - **Shift Change**: Change `work_hours`.
        - **Upskilling**: Add tools to `skills` (e.g., learning Rust or Kubernetes).
        - **Promotion**: Change `role` title.
        
        **CONSTRAINTS:**
        - Do NOT change `name` or `home_dir`.
        - Changes should be subtle (evolution, not replacement).
        
        **OUTPUT FORMAT:**
        Return STRICT JSON of the updated persona object ONLY.
        """
        response = self._call_llm(prompt)
        if isinstance(response, dict):
            return response
        return current_data

    def generate_breadcrumbs(self, crumb_type="logs"):
        """Generates fake artifacts (logs, chats) to mislead attackers."""
        if crumb_type == "logs":
            prompt = """
            **TASK:** Generate 5 realistic Log Entries for `auth.log` or `syslog`.
            **GOAL:** Hint at a vulnerability or hidden service to entice attackers.
            **EXAMPLE:** `Failed password for root from 192.168.1.50 port 2222 ssh2`
            
            **OUTPUT:** STRICT JSON List of strings.
            """
        elif crumb_type == "chat":
            prompt = """
            **TASK:** Generate 5 short Chat Snippets (Slack/Teams style).
            **GOAL:** Leak info about internal architecture or secrets.
            **EXAMPLE:** "Did you rotate the staging DB keys yet?"
            
            **OUTPUT:** STRICT JSON List of strings.
            """
        else:
            return []
            
        response = self._call_llm(prompt)
        if isinstance(response, list):
            return response
        return []



    def resolve_error(self, command, error_msg, user):
        """Analyzes a failure and decides how to fix or escalate it."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Senior Systems Engineer analyzing a failure.
        
        **CONTEXT:**
        User '{user}' executed `{command}` and failed.
        Error: "{error_msg}"
        
        **TASK:**
        Determine the resolution strategy.
        1. **RETRY**: If it's a transient error or syntax fixable by the user.
        2. **ESCALATE**: If it requires Admin privileges (Permission Denied) -> Switch to 'sys_bob'.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON:
        {{
            "action": "RETRY" or "ESCALATE",
            "target_user": "{user}" (or "sys_bob"),
            "fix_command": "Command to fix/bypass (e.g., 'sudo ...' or 'pip install ...')",
            "reason": "Brief explanation"
        }}
        """
        response = self._call_llm(prompt)
        if isinstance(response, dict):
            return response
        # Fallback
        return {
            "action": "RETRY",
            "target_user": user,
            "fix_command": f"echo 'Error resolving {command}'",
            "reason": "Fallback"
        }



    def evolve_triggers(self, current_triggers):
        """Evolves the causal logic of the system (who triggers what)."""
        prompt = f"""
        **SYSTEM ROLE:**
        You are a Chaos Engineering Architect designed to mutate system behaviors.
        
        **CONTEXT:**
        Current Causal Rules (Triggers):
        {json.dumps(current_triggers, indent=2)}
        
        **TASK:**
        Mutate the system's reactive logic to simulate changing operational procedures.
        - **Example**: Chante a rule so that `git push` triggers `deploy_service` instead of `run_tests`.
        - **Example**: Add a rule where `User=sys_bob` grepping for "error" triggers `incident_response`.
        
        **OUTPUT FORMAT:**
        Return STRICT JSON List of objects:
        [
            {{
                "source": "user_name",
                "pattern": "command_substring", 
                "event": "event_name", 
                "target": "target_user", 
                "scene_keyword": "SceneName" 
            }},
            ...
        ]
        """
        response = self._call_llm(prompt)
        if isinstance(response, list):
            return response
        return current_triggers

    def _construct_prompt(self, name, data, context=None):
        # 1. Generate dynamic paths for this persona (living environment)
        dynamic_paths = self.generate_dynamic_paths(name, data, context)
        home = data.get('home_dir', '/tmp')
        current_workspace = dynamic_paths.get('current_workspace', home)

        # Default Context
        ctx_arc = "General System Maintenance"
        ctx_day = "Unknown"
        ctx_task = "Routine checkups"
        recent_history = "None"

        if context:
            recent_history = context.get('recent_history', 'None')
            # Check if we have rich monthly context
            if isinstance(context.get('monthly_plan'), dict):
                m_plan = context['monthly_plan']
                ctx_arc = m_plan.get('narrative_arc', ctx_arc)
                ctx_day = m_plan.get('current_day', ctx_day)
                ctx_task = m_plan.get('daily_task', ctx_task)
            else:
                # Fallback to simple string if that's what was passed
                ctx_task = context.get('monthly_task', ctx_task)

        # 2. Define Persona Role & Voice with dynamic paths
        role_description = f"User: {name}\nHome Directory: {home}\nCurrent Workspace: {current_workspace}\nRole Type: "

        if "dev" in name:
            role_description += "Software Developer"
            active_projects = dynamic_paths.get('active_projects', [f"{home}/repos/backend-api"])
            archived_projects = dynamic_paths.get('archived_projects', [f"{home}/archive/old-projects"])
            personal_dirs = dynamic_paths.get('personal_dirs', [f"{home}/notes"])
            
            specific_instructions = f"""
            **BEHAVIOR**:
            - You are writing code, compiling, or debugging.
            - Use realistic tools: git, vim/nano, make, docker, kubectl, python, go.
            - If the task is 'Refactor', show `mv`, `sed`, or heavy git activity.
            - If the task is 'Feature', show `mkdir`, `touch`, and content injection.
            
            **DYNAMIC WORKING ENVIRONMENT**:
            - Active Projects: {', '.join(active_projects)}
            - Archived Work: {', '.join(archived_projects)}
            - Personal Space: {', '.join(personal_dirs)}
            - Current Focus: {current_workspace}
            
            **PATH USAGE RULES**:
            - Primary workspace: {current_workspace}
            - Create subdirectories if needed (mkdir -p)
            - Use project-specific paths from the active projects list
            - Reference archived projects for context/history
            - NEVER use generic paths like /tmp/test or /home/user/project
            """
        elif "sys" in name or "admin" in name:
            role_description += "System Administrator"
            log_dirs = dynamic_paths.get('log_dirs', ['/var/log'])
            config_dirs = dynamic_paths.get('config_dirs', ['/etc/nginx'])
            backup_dirs = dynamic_paths.get('backup_dirs', ['/mnt/backup'])
            monitoring_scripts = dynamic_paths.get('monitoring_scripts', [f"{home}/scripts/monitor.sh"])
            
            specific_instructions = f"""
            **BEHAVIOR**:
            - You are maintaining the infrastructure.
            - Use: systemctl, journalctl, grep, chown, chmod, vim /etc/..., apt/yum.
            - Focus on stability, logs, and configuration management.
            
            **DYNAMIC SYSTEM ENVIRONMENT**:
            - Log Directories: {', '.join(log_dirs)}
            - Config Locations: {', '.join(config_dirs)}
            - Backup Storage: {', '.join(backup_dirs)}
            - Monitoring Tools: {', '.join(monitoring_scripts)}
            - Current Focus: {current_workspace}
            
            **PATH USAGE RULES**:
            - Work in appropriate system directories
            - Create backup directories if they don't exist (mkdir -p)
            - Use log analysis commands on actual log files
            - Reference real system paths, not generic placeholders
            - NEVER use paths like /opt/sys_integrity/logs/ or /path/to/
            """
        elif "svc" in name or "ci" in name:
            role_description += "Automated Service / CI Bot"
            workspaces = dynamic_paths.get('workspaces', ['/var/lib/jenkins/workspace/backend-api'])
            artifacts = dynamic_paths.get('artifacts', ['/var/lib/jenkins/artifacts'])
            scripts = dynamic_paths.get('scripts', ['/var/lib/jenkins/scripts/deploy.sh'])
            
            specific_instructions = f"""
            **BEHAVIOR**:
            - You are a script or bot.
            - High speed, repetitive, precise commands.
            - Deploying artifacts, running tests, cleaning up tmp files.
            
            **DYNAMIC CI/CD ENVIRONMENT**:
            - Build Workspaces: {', '.join(workspaces)}
            - Artifact Storage: {', '.join(artifacts)}
            - Automation Scripts: {', '.join(scripts)}
            - Current Pipeline: {current_workspace}
            
            **PATH USAGE RULES**:
            - Work in designated workspace directories
            - Create artifact directories as needed
            - Use real repository URLs, not placeholders
            - Follow standard CI/CD directory structures
            """
        else:
            role_description += "Standard User"
            personal_dirs = dynamic_paths.get('personal_dirs', [f"{home}/documents"])
            config_files = dynamic_paths.get('config_files', [f"{home}/.bashrc"])
            
            specific_instructions = f"""
            **BEHAVIOR**: General command line usage.
            
            **DYNAMIC USER ENVIRONMENT**:
            - Personal Directories: {', '.join(personal_dirs)}
            - Config Files: {', '.join(config_files)}
            - Current Location: {current_workspace}
            
            **PATH USAGE RULES**:
            - Work in personal directory spaces
            - Create directories as needed for organization
            - Use realistic file paths, not generic placeholders
            """

        # 3. Define the Monthly Goal Context (The "Why")
        planning_context = f"""
        **CURRENT OBJECTIVE (Monthly Arc)**: "{ctx_arc}"
        **TODAY'S PROGRESS**: Day {ctx_day}
        **SPECIFIC TASK**: "{ctx_task}"

        *Your generated command history must DIRECTLY contribute to this specific task.*
        """

        # 4. Intensity & Realism modifiers
        intensity_cfg = self.config.get("llm", {})
        deep_coding_chance = intensity_cfg.get("deep_coding_chance", 0.2)

        is_deep_work = random.random() < deep_coding_chance

        if is_deep_work:
            work_instruction = """
            **MODE: DEEP WORK (High Detail)**
            - The user is doing substantial work.
            - GENERATE ACTUAL CONTENT: Use `cat <<EOF > filename` to create realistic code/config files.
            - The code/config should be syntactically correct and relevant to the Task.
            - Don't just `echo "code"`, write a small python function or valid json config.
            """
        else:
            work_instruction = """
            **MODE: STANDARD ACTIVITY**
            - Efficient command usage.
            - Navigation, checking status, short edits, git operations.
            """

        # 5. Final Assembly
        prompt = f"""
        # SYSTEM INSTRUCTION: CYBER DECEPTION ENGINE
        You are simulating a realistic human (or bot) interaction with a Linux shell to deceive an adversary watching the logs.

        ## 1. PERSONA PROFILE
        {role_description}
        {specific_instructions}

        ## 2. PLANNING CONTEXT
        {planning_context}

        ## 3. HISTORY
        Last Activity: {recent_history}

        ## 4. INSTRUCTIONS
        {work_instruction}

        **TASK**: Generate a structured 'Scene' object representing this user's next set of actions.
        - Ensure a logical flow (e.g., cd -> ls -> edit -> run).
        - Commands must be valid bash.
        - 'zone' is the absolute path where this happens.

        ## 5. OUTPUT FORMAT
        Return ONLY valid JSON. No markdown formatting.
        {{
            "name": "Short Descriptive Title of Scene",
            "category": "Routine" | "Variant" | "Anomaly",
            "zone": "/absolute/path/to/working/directory",
            "commands": [
                "command 1",
                "command 2",
                ...
            ]
        }}

        **CRITICAL PATH REQUIREMENTS**:
        - 'zone' MUST be an absolute path that actually exists or can be created
        - Commands MUST use specific, realistic paths (no placeholders like <FILENAME>)
        - NEVER use generic paths like "/tmp/test", "/path/to/", "/opt/sys_integrity/"
        - NEVER use placeholder URLs like "<REMOTE_REPOSITORY_URL_HERE>"
        - Use the specific paths listed in your persona profile above
        """

        return prompt
