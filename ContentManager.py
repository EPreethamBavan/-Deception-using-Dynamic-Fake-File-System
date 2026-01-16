import json
import os
import random
import logging

logger = logging.getLogger(__name__)

class ContentManager:
    """
    Central repository for dynamic deception assets.
    Manages:
    1. Forecast Queue (Batch generated scenes)
    2. Asset Cache (Vulnerabilities, Honeytokens)
    """
    def __init__(self, llm_provider, cache_file="content_cache.json"):
        self.llm = llm_provider
        self.config_dir = os.getenv("CONFIG_DIR", ".")
        self.cache_file = os.path.join(self.config_dir, cache_file)
        self.cache = self._load_cache()
        self.config = {} # Init before load
        self.project_state_file = os.path.join(self.config_dir, "project_state.json")
        self.load_dynamic_files()
        self.load_project_state()
        self._ensure_git_environment()

    def _ensure_git_environment(self):
        """Creates dummy git repositories for personas to avoid 'not a git repo' errors."""
        personas = self.load_personas(os.path.join(self.config_dir, "worker_spec.json"))
        for user, data in personas.items():
            # Heuristic: If they are a dev, give them a repo
            if "dev" in user or "skills" in data and "git" in data["skills"]:
                home = data.get("home_dir", f"/home/{user}")
                # Create a typical repo path that the LLM might hallucinate
                # We see queries like /home/dev_alice/repos/core-services-migration
                common_repos = ["core-services-migration", "backend-api", "frontend-app"]
                
                base_repo_dir = os.path.join(home, "repos")
                # Since we are operating on the REAL file system (or fake one depending on implementation),
                # we should try to physically create these folders if we can.
                # NOTE: This runs as the service user (root).
                if not os.path.exists(base_repo_dir):
                    try:
                        os.makedirs(base_repo_dir)
                    except:
                        pass # Permission issues or non-existent parent

                for repo in common_repos:
                    repo_path = os.path.join(base_repo_dir, repo)
                    if not os.path.exists(repo_path):
                        try:
                            os.makedirs(repo_path)
                            # Init git
                            import subprocess
                            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
                            subprocess.run(["git", "config", "user.email", f"{user}@company.com"], cwd=repo_path, capture_output=True)
                            subprocess.run(["git", "config", "user.name", user], cwd=repo_path, capture_output=True)
                            logger.info(f"Initialized fake git repo at {repo_path}")
                        except Exception as e:
                            logger.warning(f"Failed to init git repo {repo_path}: {e}")

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return self._init_empty_cache()
        return self._init_empty_cache()
        
    def _init_empty_cache(self):
        return {
            "forecast_queue": [],
            "assets": {
                "vuln_commands": [],
                "honeytoken_commands": []
            }
        }

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    # --- Feature: Project State Management (The "Brain") ---
    def load_project_state(self):
        """Loads the persistent state of the virtual project (codebase)."""
        # project_state_file path is set in __init__
        if os.path.exists(self.project_state_file):
            with open(self.project_state_file, 'r') as f:
                self.project_state = json.load(f)
        else:
            self.project_state = {
                "project_name": "Core_App_V1",
                "current_day": 1,
                "created_files": {}, # logical_path -> {summary, last_modified}
                "knowledge_graph": {}, # symbol -> file_path
                "build_status": "passing"
            }
            self.save_project_state()
            
    def save_project_state(self):
        with open(self.project_state_file, 'w') as f:
            json.dump(self.project_state, f, indent=4)

    def update_file_index(self, file_path, summary):
        """Updates the index of what code exists."""
        self.project_state["created_files"][file_path] = {
            "summary": summary,
            "last_modified": self.project_state["current_day"]
        }
        self.save_project_state()

    def get_file_content(self, file_path):
        """'Reads' a file from the fake file system (Context Tool)."""
        # In this simulation, we assume the file actually exists on disk if it was 'created'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        return "[FILE NOT FOUND]"

    # --- Forecast Features ---
    def generate_forecast(self, count=20):
        """Generates a batch of future scenes and adds them to the queue."""
        logger.info(f"Generating forecast of {count} scenes...")
        scenes = self.llm.generate_batch_scenes(count)
        if scenes:
            self.cache["forecast_queue"].extend(scenes)
            self.save_cache()
            logger.info(f"Forecast updated. Queue size: {len(self.cache['forecast_queue'])}")
        else:
            logger.error("Failed to generate forecast.")

    def get_next_forecast_scene(self):
        """Pops the next scene from the forecast queue."""
        if self.cache["forecast_queue"]:
            scene = self.cache["forecast_queue"].pop(0)
            self.save_cache()
            return scene
        return None

    # --- Dynamic Persona Features ---
    def load_personas(self, default_spec_file):
        """Loads personas from cache (dynamic) or falls back to spec (static)."""
        if "personas" in self.cache and self.cache["personas"]:
            logger.info("Loaded Dynamic Personas from Cache")
            return self.cache["personas"]
        
        # Adjust path if relative
        if not os.path.isabs(default_spec_file):
            default_spec_file = os.path.join(self.config_dir, default_spec_file)

        # Fallback
        if os.path.exists(default_spec_file):
             with open(default_spec_file) as f:
                 data = json.load(f)
                 self.cache["personas"] = data
                 self.save_cache()
                 return data
                 
        # 3. Last Resort: Self-seed defaults
        defaults = {
            "dev_alice": {"home_dir": "/home/dev_alice", "role": "Senior Developer", "skills": ["python", "docker"]},
            "sys_bob": {"home_dir": "/home/sys_bob", "role": "SysAdmin", "skills": ["bash", "ansible"]},
            "svc_ci": {"home_dir": "/var/lib/jenkins", "role": "CI Bot", "skills": ["git", "make"]}
        }
        self.cache["personas"] = defaults
        self.save_cache()
        return defaults

    def evolve_personas(self):
        """Triggers evolution for all managed personas (Strict 6-month cycle)."""
        logger.info("Checking for Persona Evolution candidates...")
        current_time = time.time()
        # Get config values
        cooldown_days = self.config.get("simulation", {}).get("promotion_cooldown_days", 180)
        promo_chance = self.config.get("simulation", {}).get("promotion_chance", 0.10)
        
        SIX_MONTHS = cooldown_days * 24 * 60 * 60 # Seconds
        
        current = self.cache.get("personas", {})
        promoted_count = 0
        
        for name, data in current.items():
            last_evo = data.get("last_evolution", 0)
            
            # Check cooldown
            if (current_time - last_evo) > SIX_MONTHS:
                # Probabilistic chance per run ONCE eligible
                if random.random() < promo_chance: 
                    logger.info(f"Promoting user {name} (Eligible)...")
                    new_data = self.llm.evolve_persona(data)
                    new_data["last_evolution"] = current_time
                    self.cache["personas"][name] = new_data
                    promoted_count += 1
        
        if promoted_count > 0:
            self.save_cache()
            logger.info(f"Evolution Complete: {promoted_count} users promoted.")

    # --- Breadcrumbs ---
    def generate_breadcrumbs(self):
        """Generates and caches new breadcrumbs."""
        logs = self.llm.generate_breadcrumbs("logs")
        chats = self.llm.generate_breadcrumbs("chat")
        
        if "breadcrumbs" not in self.cache:
            self.cache["breadcrumbs"] = []
            
        self.cache["breadcrumbs"].extend(logs)
        self.cache["breadcrumbs"].extend(chats)
        self.save_cache()
        logger.info(f"Generated {len(logs) + len(chats)} new breadcrumbs.")

    def get_breadcrumb(self):
        """Retrieves and removes a breadcrumb to plant."""
        if "breadcrumbs" in self.cache and self.cache["breadcrumbs"]:
            crumb = self.cache["breadcrumbs"].pop(0)
            self.save_cache()
            return crumb
        return None

    # --- Dynamic Asset Features ---
    def refresh_assets(self):
        """Refreshes the pool of vulnerability and honeytoken templates."""
        logger.info("Refreshing Content Assets via LLM...")
        
        # Also evolve triggers
        if random.random() < 0.2:
             self.evolve_triggers()
        
        new_vulns = self.llm.generate_content_assets("vuln")
        if new_vulns:
            self.cache["assets"]["vuln_commands"] = new_vulns # Replace old with new
        
        new_tokens = self.llm.generate_content_assets("honeytoken")
        if new_tokens:
            self.cache["assets"]["honeytoken_commands"] = new_tokens
            
        self.save_cache()
        logger.info("Content Assets Refreshed.")

    def get_random_asset(self, asset_type):
        """Retrieves a random asset from cache, falling back to defaults."""
        files = self.cache.get("assets", {}).get(f"{asset_type}_commands", [])
        if files:
            return random.choice(files)
        # Fallback to templates.json if cache empty
        if self.templates:
            return random.choice(self.templates.get(asset_type, []))
        return None

    # --- Phase 4: Dynamic Triggers & Templates ---
    def load_dynamic_files(self):
        """Loads external JSONs for full dynamism, seeding defaults if missing."""
        self.triggers = []
        self.templates = {}
        
        # Paths
        triggers_path = os.path.join(self.config_dir, "triggers.json")
        templates_path = os.path.join(self.config_dir, "templates.json")
        config_path = os.path.join(self.config_dir, "config.json")

        # 1. Triggers
        if os.path.exists(triggers_path):
            with open(triggers_path) as f:
                self.triggers = json.load(f)
        else:
            self.triggers = [
                {
                    "target": "sys_bob",
                    "scene_keyword": "restart_service",
                    "event": "server_down",
                    "source": "any",
                    "pattern": "500 Internal Server Error"
                },
                {
                    "target": "dev_alice",
                    "scene_keyword": "check_logs",
                    "event": "anomaly_alert",
                    "source": "any",
                    "pattern": "Unauthorized Access"
                }
            ]
            self.save_triggers()
        
        # 2. Templates
        if os.path.exists(templates_path):
            with open(templates_path) as f:
                self.templates = json.load(f)
        else:
            self.templates = {
                "triggered_response": {
                    "name": "Response to {keyword}",
                    "category": "Responsive",
                    "zone": "/tmp", 
                    "commands": ["echo 'Handling trigger: {keyword}'", "date"]
                },
                "narrative": {
                    "name": "Narrative Task: {task}",
                    "category": "Routine",
                    "zone": "/home/dev_alice",
                    "commands": ["echo 'Starting task: {task}'", "ls -la"]
                },
                "maintenance_refresh": {
                    "name": "System Maintenance (Asset Refresh)",
                    "category": "Maintenance",
                    "zone": "/var/log",
                    "commands": ["echo 'Maintenance Complete'", "Truncating logs..."]
                },
                "breadcrumb_leak": {
                    "name": "Accidental Leak (Breadcrumb)",
                    "category": "Anomaly",
                    "zone": "/tmp",
                    "commands": ["echo '{crumb}' >> debug.log"]
                },
                "cache": {
                    "name": "Cached Maintenance", 
                    "category": "Routine", 
                    "zone": "/var/log", 
                    "commands": ["tail -f syslog"]
                },
                "fuzzing": {
                    "files": ["utils.py", "config.yaml", "main.go"],
                    "commit_messages": ["Fix typo", "Update config", "Refactor"]
                },
                "typos": {
                    "git": ["gti", "got", "gut"],
                    "docker": ["dockr", "docekr"]
                },
                "vuln": ["chmod 777 -R /var/www"],
                "honeytoken": ["echo 'aws_key=AKIA...' > ~/.aws/credentials"]
            }
            with open(templates_path, "w") as f:
                json.dump(self.templates, f, indent=4)

        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_triggers(self):
        with open(os.path.join(self.config_dir, "triggers.json"), "w") as f:
            json.dump(self.triggers, f, indent=4)

    def evolve_triggers(self):
        """Uses LLM to rewrite the system rules."""
        logger.info("Evolving System Triggers (Rules of the Game)...")
        if self.triggers:
            try:
                 new_triggers = self.llm.evolve_triggers(self.triggers)
                 if new_triggers:
                     self.triggers = new_triggers
                     self.save_triggers()
            except Exception as e:
                logger.error(f"Failed to evolve triggers: {e}")

    def get_triggers(self):
        if not hasattr(self, 'triggers'): self.load_dynamic_files()
        return self.triggers
        
    def get_template(self, category="cache"):
        if not hasattr(self, 'templates'): self.load_dynamic_files()
        pool = self.templates.get(category, None)
        
        if not pool: return None
        
        # If it's a configuration dict (e.g., fuzzing rules), return as is
        if isinstance(pool, dict):
            return pool
            
        # If it's a list (scenes), return a random choice
        if isinstance(pool, list):
            return random.choice(pool)
            
        return pool
