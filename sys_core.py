import os
import json
import random
import time
import argparse
import logging
from datetime import datetime
from LLM_Provider import LLMProvider
from StrategyManager import StrategyManager
from ContentManager import ContentManager
from ActiveDefense import ActiveDefense

# Configure logging - Stealth Mode (Log to file only)
# We avoid console output to prevent alerting attackers reading syslog/journalctl
log_dir = os.getenv("CONFIG_DIR", ".") 
if os.getenv("CONFIG_DIR"):
    pass

logging.basicConfig(
    filename='monitor_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Load .env manually if python-dotenv not present
def load_env():
    config_dir = os.getenv("CONFIG_DIR", ".")
    env_path = os.path.join(config_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
    elif os.path.exists(".env"): 
         with open(".env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v

class SystemMonitor:
    def __init__(self, spec_file="worker-spec.json", plan_file="monthly_plan.json", state_file="state.json", dry_run=False, use_llm=False):
        self.config_dir = os.getenv("CONFIG_DIR", ".")
        
        # Adjust paths
        self.spec_file = os.path.join(self.config_dir, spec_file)
        self.plan_file = os.path.join(self.config_dir, plan_file)
        self.state_file = os.path.join(self.config_dir, state_file)
        
        self.dry_run = dry_run
        self.use_llm = use_llm
        
        self.llm_provider = LLMProvider() if self.use_llm else None
        
        # Initialize Content Manager (Modular Asset Storage)
        self.content_manager = ContentManager(self.llm_provider) if self.use_llm else None
        
        # Dynamic Personas via ContentManager if available, else static
        if self.content_manager:
            self.personas = self.content_manager.load_personas(self.spec_file)
        else:
            self.personas = self._load_json(self.spec_file)

        self.monthly_plan = self._load_json(self.plan_file)
        self.state = self._init_state()
        
        self.strategy_manager = StrategyManager(self)
        
        # Active Defense (Honeyports)
        ad_ports = [8080, 2222, 2121]
        ad_banner = b"Internal Service Error 500: Check Logs\n"
        
        if self.content_manager and hasattr(self.content_manager, 'config'):
            ad_config = self.content_manager.config.get("active_defense", {})
            ad_ports = ad_config.get("ports", ad_ports)
            banner_str = ad_config.get("banner", "Internal Error\n")
            ad_banner = banner_str.encode('utf-8')

        self.active_defense = ActiveDefense(ports=ad_ports, banner=ad_banner)
        if not self.dry_run:
            self.active_defense.start()

    def _load_json(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in: {filepath}")
            return {}

    def _init_state(self):
        if os.path.exists(self.state_file):
            return self._load_json(self.state_file)
        return {"global_events": [], "users": {}, "last_run": 0}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    # --- Feature: Content Management ---
    def generate_forecast(self, count):
        """Wraps content manager's forecast generation."""
        if self.content_manager:
            self.content_manager.generate_forecast(count)
        else:
            logger.error("LLM Provider or Content Manager not initialized.")

    def refresh_content(self):
        """Wraps content manager's refresh assets."""
        if self.content_manager:
            self.content_manager.refresh_assets()
        else:
            logger.error("LLM Provider or Content Manager not initialized.")

    def generate_monthly_plan(self):
        """Generates a new monthly plan via LLM and saves it."""
        if not self.llm_provider:
             logger.error("LLM Provider not initialized.")
             return

        logger.info("Generating new Monthly Narrative Arc...")
        new_plan = self.llm_provider.generate_monthly_plan()
        
        if new_plan:
             with open(self.plan_file, 'w') as f:
                 json.dump(new_plan, f, indent=4)
             logger.info(f"New Monthly Plan Generated: {new_plan.get('narrative_arc', 'Unknown')}")
        else:
             logger.error("Failed to generate monthly plan.")

    # --- Layer 1: Smart Timer ---
    def is_active_window(self, persona_name, persona_data):
        """Determines if the persona should be active based on time and probability."""
        start_hour, end_hour = persona_data.get('work_hours', [9, 17])
        probability = persona_data.get('probability', 0.5)
        
        current_hour = datetime.now().hour
        
        if start_hour > end_hour:
             is_working_hours = current_hour >= start_hour or current_hour <= end_hour
        else:
            is_working_hours = start_hour <= current_hour <= end_hour

        if is_working_hours:
            return random.random() < probability
        else:
            return random.random() < 0.05

    # --- Layer 2: Script Picker (Hybrid Static/LLM) ---
    def select_scene(self, persona_name, persona_data, context=None, force_llm=False):
        """Selects a scene based on weighted categories or Calls LLM."""
        
        # 1. Decide whether to use LLM (Contextual Injection)
        should_use_llm = self.use_llm and (force_llm or random.random() < 0.5 or not persona_data.get('scenes'))
        
        if should_use_llm:
            logger.info(f"[LLM] Generating dynamic scene for {persona_name} (Forced: {force_llm})...")
            
            # Construct rich context for the new prompt engine
            if not context:
                 # Minimal fallback context if none provided
                 current_day = str(datetime.now().day)
                 daily_task = self.monthly_plan.get('daily_tasks', {}).get(current_day, "General Maintenance")
                 narrative_arc = self.monthly_plan.get('narrative_arc', "Routine Operations")
                 
                 context = {
                    "monthly_plan": {
                        "narrative_arc": narrative_arc,
                        "current_day": current_day,
                        "daily_task": daily_task
                    },
                    "recent_history": self.state.get('users', {}).get(persona_name, {}).get('last_scene', "None")
                 }
                 
            return self.llm_provider.generate_scene(persona_name, persona_data, context)

        # 2. Fallback to Static Selection
        scenes = persona_data.get('scenes', [])
        if not scenes:
            return None

        last_scene = self.state.get('users', {}).get(persona_name, {}).get('last_scene')
        
        r = random.random()
        if r < 0.70:
            target_cat = "Routine"
        elif r < 0.90:
            target_cat = "Variant"
        else:
            target_cat = "Anomaly"

        eligible = [s for s in scenes if s.get('category') == target_cat]
        if not eligible:
            eligible = scenes

        pool = [s for s in eligible if s['name'] != last_scene]
        if not pool:
            pool = eligible
            
        return random.choice(pool)

    # --- Layer 3: Story Planner (Narrative Injection) ---
    def get_monthly_task(self):
        day = str(datetime.now().day)
        return self.monthly_plan.get('daily_tasks', {}).get(day, "General Maintenance")

    def inject_narrative(self, persona_name, daily_task_info=None):
        task = daily_task_info.get('focus') if daily_task_info else self.get_monthly_task()
        
        # Only inject if we have a task and we are NOT using the LLM (fallback mode)
        if task and not self.use_llm:
             if self.content_manager:
                 template = self.content_manager.get_template("narrative")
                 if template:
                     # Deep copy to avoid modifying cache
                     scene = json.loads(json.dumps(template))
                     # dynamic injection
                     scene["name"] = scene["name"].format(task=task)
                     scene["commands"] = [cmd.format(task=task) for cmd in scene["commands"]]
                     return scene
        return None

    # --- Cross-User Context ---
    def check_triggers(self, persona_name):
        """Checks for global events that trigger specific actions."""
        # Check against global event queue
        triggered_events = self.state.get("global_events", [])
        
        # Access Dynamic Triggers
        if self.content_manager:
            triggers = self.content_manager.get_triggers()
            for rule in triggers:
                # If I am the target of an active event
                if rule["target"] == persona_name and rule["event"] in triggered_events:
                    # Return True implies "Force Run", we attach data for scene selection
                    # Ideally we returns the specific scene type
                    return rule["scene_keyword"] 
        return None

    def process_triggers(self, persona_name, commands):
        """Scans executed commands against Dynamic Rules."""
        if not self.content_manager: return

        triggers = self.content_manager.get_triggers()
        for rule in triggers:
            # If I am the source
            if rule["source"] == persona_name:
                # Check if my command matches pattern
                for cmd in commands:
                    if rule["pattern"] in cmd:
                         if rule["event"] not in self.state["global_events"]:
                             logger.info(f"DYNAMIC TRIGGER: {persona_name} matched [{rule['pattern']}] -> Firing [{rule['event']}]")
                             self.state["global_events"].append(rule["event"])

    # --- Execution Core ---
    def run(self, strategy_flag=None):
        logger.info("--- Deception Engine Cycle Start ---")
        
        # --- 1. HIERARCHICAL PLANNING CHECK ---
        # Ensure we have a valid Monthly Plan
        if not self.monthly_plan or "narrative_arc" not in self.monthly_plan:
            self.generate_monthly_plan()
            
        # Ensure we have a valid Project State
        if self.content_manager and not getattr(self.content_manager, 'project_state', None):
            self.content_manager.load_project_state()
            
        if self.content_manager:
            current_day = self.content_manager.project_state.get('current_day', 1)
        else:
            current_day = 1
        
        # --- 2. ADAPTIVE PLANNING (Manager Agent) ---
        # Every 5 days, check if we need to CRUNCH
        # Enabled for 'hybrid' (Professional Mode) or explicit 'adaptive' flag (future proofing)
        if current_day % 5 == 0 and strategy_flag in ["adaptive", "hybrid"]:
            self._run_adaptive_check(current_day)

        # --- 3. WEEKLY & DAILY PLANNING ---
        # Determine current week (1-4)
        current_week = (current_day - 1) // 7 + 1
        
        # Ensure Weekly Plan Exists
        # (Stored in project_state context or separate file, illustrating generic key here)
        weekly_plan = None
        if self.content_manager:
            weekly_plan = self.content_manager.project_state.get(f"week_{current_week}_plan")

        if not weekly_plan and self.llm_provider and self.content_manager:
             logger.info(f"Generating Plan for Week {current_week}...")
             new_week_plan = self.llm_provider.generate_weekly_plan(self.monthly_plan, current_week)
             self.content_manager.project_state[f"week_{current_week}_plan"] = new_week_plan
             self.content_manager.save_project_state()
             weekly_plan = new_week_plan

        # Get/Generate Daily Task
        # Look up specific day task from weekly plan
        daily_task_info = next((d for d in (weekly_plan or []) if str(d.get("day")) == str(current_day)), None)
        
        # Fallback if specific planning fails
        if not daily_task_info:
            daily_task_info = {"focus": "General Work", "day": str(current_day)}

        logger.info(f"Day {current_day} Focus: {daily_task_info.get('focus')}")

        targets = list(self.personas.items())
        
        for name, data in targets:
            # ==========================================
            # STEP 1: CHECK TRIGGERS (Highest Priority)
            # ==========================================
            forced_run = False
            scene = None
            trigger_keyword = self.check_triggers(name)
            
            if trigger_keyword:
                logger.info(f"TRIGGER ACTIVATED for {name}: {trigger_keyword}")
                # Try to find a scene matching the keyword
                scene = next((s for s in data.get('scenes', []) if trigger_keyword in s['name']), None)
                if not scene:
                     # Generate ad-hoc from template
                     if self.content_manager:
                         tpl = self.content_manager.get_template("triggered_response")
                         if tpl:
                             scene = json.loads(json.dumps(tpl))
                             scene["name"] = scene["name"].format(keyword=trigger_keyword)
                             scene["commands"] = [c.format(keyword=trigger_keyword) for c in scene["commands"]]
                         else:
                             # Ultimate fallback if template missing
                             scene = {"name": "Response", "category": "Responsive", "zone": "/tmp", "commands": ["echo ok"]}

                forced_run = True
                # Optimistic event cleanup: remove first event that matches any rule for this user
                triggers = self.content_manager.get_triggers()
                for rule in triggers:
                    if rule["target"] == name and rule["scene_keyword"] == trigger_keyword:
                         if rule["event"] in self.state["global_events"]:
                             self.state["global_events"].remove(rule["event"])
                             break 
            
            # ==========================================
            # STEP 2: SCHEDULE FILTER (The Gatekeeper)
            # ==========================================
            # If NOT forced by a trigger, we must respect working hours
            if not forced_run and not self.is_active_window(name, data):
                continue

            # ==========================================
            # STEP 3: STRATEGY INTERCEPTION (The Manager)
            # ==========================================
            if not scene and strategy_flag:
                 # Ask Manager for a scene
                result = self.strategy_manager.select_strategy(strategy_flag)
                
                # Hybrid might return ("LLM_DELEGATE", "user") or (user, scene) or None
                if result:
                    if isinstance(result, tuple) and result[0] == "LLM_DELEGATE":
                        if result[1] == name: # Only if this user was chosen
                            # Force LLM generation for this specific chosen user
                            # Construct explicit context
                            context = {
                                "monthly_plan": {
                                    "narrative_arc": self.monthly_plan.get('narrative_arc', "Routine Operations"),
                                    "current_day": daily_task_info.get("day", 1),
                                    "daily_task": daily_task_info.get("focus", "General Maintenance")
                                },
                                "recent_history": self.state.get('users', {}).get(name, {}).get('last_scene', "None")
                            }
                            scene = self.select_scene(name, data, context=context, force_llm=True) 
                    elif isinstance(result, tuple):
                        if result[0] == name:
                            scene = result[1]
                    else:
                         # Strategy returned a generic scene (e.g. broadcast), potentially applicable to all?
                         # Usually strategy returns specific user actions. 
                         # If generic, we might apply it.
                         scene = result

            # ==========================================
            # STEP 4: STANDARD SELECTION (Default)
            # ==========================================
            if not scene:
                scene = self.inject_narrative(name, daily_task_info) 
                if not scene:
                     # Construct explicit context for fallback select
                     context = {
                        "monthly_plan": {
                            "narrative_arc": self.monthly_plan.get('narrative_arc', "Routine Operations"),
                            "current_day": daily_task_info.get("day", 1),
                            "daily_task": daily_task_info.get("focus", "General Maintenance")
                        },
                        "recent_history": self.state.get('users', {}).get(name, {}).get('last_scene', "None")
                     }
                     scene = self.select_scene(name, data, context=context)

            if not scene:
                continue

            # ==========================================
            # STEP 5: NOISE INJECTION (The Humanizer)
            # ==========================================
            if strategy_flag == "hybrid" or strategy_flag == "noise":
                 scene['commands'] = self.strategy_manager.apply_noise(scene['commands'])

            # ==========================================
            # STEP 6: EXECUTION (With Feedback Loop)
            # ==========================================
            self.execute_scene_with_feedback(name, scene)
            
            if forced_run:
                 pass
        
        # Increment Day at end of full cycle? OR handle externally.
        # For simulation speed, we might increment day every N cycles.
        # For now, let's just log progress.
        self._save_state()
        self._advance_simulation_time()
        logger.info("--- Cycle Complete ---")

    def _advance_simulation_time(self):
        """Simulates passage of time."""
        logger.info("[SIMULATION] Advancing time (Simulated)...")

    def _run_adaptive_check(self, current_day):
        """Checks if we are on track to finish the monthly goal."""
        logger.info("[ADAPTIVE AGENT] Checking progress...")
        # Simple heuristic: Do we have enough created files?
        file_count = len(self.content_manager.project_state.get('created_files', {}))
        status = "On Track"
        if file_count < (current_day // 2): 
            status = "Behind Schedule"
            
        if status == "Behind Schedule" and self.llm_provider:
             logger.warning("[ADAPTIVE WARNING] Project falling behind. triggering Re-Plan.")
             adaptation = self.llm_provider.adapt_plan(current_day, status, self.monthly_plan.get('narrative_arc'))
             
             if adaptation:
                 strategy = adaptation.get('strategy')
                 revised_tasks = adaptation.get('revised_daily_tasks')
                 logger.info(f"[MANAGER DECISION] {strategy}: {json.dumps(revised_tasks)}")
                 
                 # Apply revision to Monthly Plan in memory
                 if revised_tasks:
                     days_updated = 0
                     for day_key, task_desc in revised_tasks.items():
                         # day_key format "day_N" -> "N" or just "N"
                         d_str = day_key.replace("day_", "")
                         self.monthly_plan['daily_tasks'][d_str] = task_desc
                         days_updated += 1
                     
                     # Persist changes
                     with open(self.plan_file, 'w') as f:
                         json.dump(self.monthly_plan, f, indent=4)
                     logger.info(f"[PLAN UPDATED] Adjusted {days_updated} days based on Manager Decision.")

    def _run_command_raw(self, username, cmd, cwd):
        """Executes a shell command for a specific user in a specific directory."""
        import subprocess
        
        logger.info(f"[{username}] $ {cmd} (cwd={cwd})")
        
        if self.dry_run:
            # Simulation Mode
            return "Simulated Output", None
            
        # Real Execution
        try:
            # Ensure directory exists
            if not os.path.exists(cwd):
                os.makedirs(cwd, exist_ok=True)
            
            # PERSISTENCE: Append to .bash_history for realism
            try:
                # Simple heuristic: if we know the home dir from personas, use it
                # otherwise guess /home/{username}
                history_file = f"/home/{username}/.bash_history"
                if username == "root": history_file = "/root/.bash_history"
                
                # Force create the home directory if it doesn't exist (Fake FS)
                os.makedirs(os.path.dirname(history_file), exist_ok=True)
                
                # Format: Just the command (Clean, default style)
                with open(history_file, "a") as hf:
                    hf.write(f"{cmd}\n")
            except Exception as e:
                logger.warning(f"Failed to update bash_history: {e}")

            # TODO: Switch user context via 'sudo -u' if running as root
            # For this implementation, we run as current user but log appropriately
            
            result = subprocess.run(
                f"cd {cwd} && {cmd}", 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode != 0:
                return result.stdout, result.stderr
            return result.stdout, None
            
        except subprocess.TimeoutExpired:
            return None, "Command Timed Out"
        except Exception as e:
            return None, str(e)

    def execute_scene_with_feedback(self, username, scene):
        """Executes commands and handles simulated errors via LLM feedback."""
        logger.info(f"Executing Scene [{scene['name']}] for User [{username}]")
        
        if username not in self.state['users']:
            self.state['users'][username] = {}
        self.state['users'][username]['last_scene'] = scene['name']
        self.state['users'][username]['last_run'] = time.time()
        
        home_dir = self.personas[username].get('home_dir', '/tmp')
        target_dir = scene.get('zone', home_dir)

        MAX_RETRIES = 3

        for cmd in scene['commands']:
            # Run Safely with Retry Loop
            success = False
            retries = 0
            current_cmd = cmd
            
            while not success and retries < MAX_RETRIES:
                output, error = self._run_command_raw(username, current_cmd, target_dir)
                
                if not error:
                    success = True
                    break
                
                # --- AGENTIC ERROR LOOP ---
                if self.llm_provider:
                     logger.warning(f"[AGENT ERROR] Command '{current_cmd}' failed (Attempt {retries+1}/{MAX_RETRIES}).")
                     
                     # 1. READ CONTEXT (If file related)
                     file_context = None
                     # Heuristic: Extract filename from command if possible (e.g. "python script.py")
                     parts = current_cmd.split()
                     possible_files = [p for p in parts if "." in p or "/" in p]
                     if possible_files:
                         # Try to read the last likely file argument
                         fpath = possible_files[-1]
                         if not fpath.startswith("/"): fpath = os.path.join(target_dir, fpath)
                         if os.path.exists(fpath):
                              with open(fpath, 'r') as f: file_context = f.read(2000) # Cap context size

                     # 2. ASK FOR FIX
                     fix_response = self.llm_provider.fix_code(current_cmd, error, file_context)
                     
                     if fix_response.get("type") == "file":
                         # Agent wants to rewrite a file to fix the issue
                         fix_path = fix_response.get("path")
                         fix_content = fix_response.get("content")
                         logger.info(f"[AGENT FIX] Rewriting file: {fix_path}")
                         try:
                             with open(fix_path, 'w') as f: f.write(fix_content)
                             # Retry ORIGINAL command now that file is fixed
                             success = False # Force another loop iteration to run command
                         except Exception as e:
                             logger.error(f"[AGENT FIX FAILED] Could not write file: {e}")
                             break 
                     else:
                         # Agent provided a new command
                         fixed_command = fix_response.get("content", current_cmd)
                         if fixed_command != current_cmd:
                             logger.info(f"[AGENT FIX] Retrying with new command: {fixed_command}")
                             current_cmd = fixed_command
                         else:
                             # LLM couldn't help
                             break
                             
                retries += 1
            
            # --- SIMULATED TOOL USE ---
            # If the output contains a request to read a file?
            # (Note: Usually LLM does this in generation phase, effectively 'select_scene' loop.
            #  But if we implement REPL here, we would capture standard out.)
            
        self._update_project_state(scene.get('commands', []), target_dir)
        self.process_triggers(username, scene['commands'])
        time.sleep(1)

    def _update_project_state(self, commands, cwd):
        """Heuristic to track creation of new files for Project State."""
        # Simple heuristic: look for 'touch', '>', 'mkdir'
        if not self.content_manager: return
        
        for cmd in commands:
            parts = cmd.split()
            created_file = None
            
            if "touch" in parts:
                idx = parts.index("touch")
                if idx + 1 < len(parts): created_file = parts[idx+1]
            elif ">" in parts:
                idx = parts.index(">")
                if idx + 1 < len(parts): created_file = parts[idx+1]
                
            if created_file:
                # Resolve path
                if not created_file.startswith("/"):
                    created_file = os.path.join(cwd, created_file)
                
                # Update Content Manager
                logger.info(f"[PROJECT TRACKER] Detected new file: {created_file}")
                self.content_manager.update_file_index(created_file, "Auto-generated file")





if __name__ == "__main__":
    load_env()
    parser = argparse.ArgumentParser(description="Deception Engine Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode (no system changes)")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--llm", action="store_true", help="Enable LLM dynamic scene generation")
    
    # Management Flags
    parser.add_argument("--generate-forecast", type=int, help="Generate N batch scenes for forecasting")
    parser.add_argument("--generate-monthly", action="store_true", help="Generate a new dynamic monthly narrative plan")
    parser.add_argument("--refresh-content", action="store_true", help="Refresh dynamic content assets (vulns/tokens)")

    # Strategy Flags
    parser.add_argument("--strategy-monthly", action="store_true", help="Force Monthly Plan Strategy")
    parser.add_argument("--strategy-template", action="store_true", help="Force Template Randomization Strategy")
    parser.add_argument("--strategy-cache", action="store_true", help="Force Cache Usage Strategy")
    parser.add_argument("--strategy-honeytoken", action="store_true", help="Force Honeytoken Generation")
    parser.add_argument("--strategy-vuln", action="store_true", help="Force Vulnerability Simulation")
    parser.add_argument("--strategy-hybrid", action="store_true", help="Enable Hybrid Mode (Professional)")
    parser.add_argument("--strategy-noise", action="store_true", help="Enable Noise Mode")
    
    args = parser.parse_args()
    
    # Init Engine
    engine = SystemMonitor(dry_run=args.dry_run, use_llm=args.llm or args.generate_forecast or args.refresh_content or args.generate_monthly or args.strategy_hybrid)

    # 1. Handle Management Tasks
    if args.refresh_content:
        engine.refresh_content()
        exit(0)
    
    if args.generate_monthly:
        engine.generate_monthly_plan()
        exit(0)
    
    if args.generate_forecast:
        engine.generate_forecast(args.generate_forecast)
        exit(0)

    # 2. Handle Runtime
    active_strategy = None
    if args.strategy_monthly: active_strategy = "monthly"
    elif args.strategy_template: active_strategy = "template"
    elif args.strategy_cache: active_strategy = "cache"
    elif args.strategy_honeytoken: active_strategy = "honeytoken"
    elif args.strategy_vuln: active_strategy = "vuln"
    # elif args.strategy_forecast: active_strategy = "forecast" # Removed
    elif args.strategy_hybrid: active_strategy = "hybrid"

    if args.loop:
        try:
            while True:
                engine.run(strategy_flag=active_strategy)
                sleep_time = random.randint(5, 10) 
                logger.info(f"Sleeping for {sleep_time}s...")
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            logger.info("Engine stopped.")
            if engine.active_defense: engine.active_defense.stop()
    else:
        engine.run(strategy_flag=active_strategy)
        if engine.active_defense: engine.active_defense.stop()
