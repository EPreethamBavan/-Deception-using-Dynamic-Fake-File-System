import os
import json
import random
import time
import argparse
import logging
from datetime import datetime
from LLM_Provider import LLMProvider
from StrategyEngine import StrategyEngine
from ContentManager import ContentManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env manually if python-dotenv not present
def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v

class DeceptionEngine:
    def __init__(self, spec_file="worker-spec.json", plan_file="monthly_plan.json", state_file="state.json", dry_run=False, use_llm=False):
        self.spec_file = spec_file
        self.plan_file = plan_file
        self.state_file = state_file
        self.dry_run = dry_run
        self.use_llm = use_llm
        
        self.personas = self._load_json(self.spec_file)
        self.monthly_plan = self._load_json(self.plan_file)
        self.state = self._init_state()
        
        self.llm_provider = LLMProvider() if self.use_llm else None
        
        # Initialize Content Manager (Modular Asset Storage)
        self.content_manager = ContentManager(self.llm_provider) if self.use_llm else None
        
        self.strategy_manager = StrategyEngine(self)

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
    def select_scene(self, persona_name, persona_data):
        """Selects a scene based on weighted categories or Calls LLM."""
        
        # 1. Decide whether to use LLM (Contextual Injection)
        should_use_llm = self.use_llm and (random.random() < 0.5 or not persona_data.get('scenes'))
        
        if should_use_llm:
            logger.info(f"[LLM] Generating dynamic scene for {persona_name}...")
            context = {
                "monthly_task": self.get_monthly_task(),
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

    def inject_narrative(self, persona_name):
        task = self.get_monthly_task()
        
        if task and persona_name == "dev_alice" and not self.use_llm:
             return {
                 "name": f"Narrative Task: {task}",
                 "category": "Narrative",
                 "zone": "/var/www/project",
                 "commands": [
                     f"echo 'Working on: {task}' >> work_log.txt",
                     "git commit -m 'Progress on narrative task'"
                 ]
             }
        return None

    # --- Cross-User Context ---
    def check_triggers(self, persona_name):
        """Checks for global events that trigger specific actions."""
        if persona_name == "svc_ci":
            if "trigger_build" in self.state.get("global_events", []):
                return True
        return False

    def process_triggers(self, persona_name, commands):
        """Scans executed commands to set triggers for OTHER users."""
        for cmd in commands:
            if persona_name == "dev_alice" and ("git push" in cmd or "commit" in cmd):
                if "trigger_build" not in self.state["global_events"]:
                    logger.info(f"Event Triggered: {persona_name} performed git push -> Queuing Build")
                    self.state["global_events"].append("trigger_build")

    # --- Execution Core ---
    def run(self, strategy_flag=None):
        logger.info("--- Deception Engine Cycle Start ---")
        
        targets = list(self.personas.items())
        
        for name, data in targets:
            # 1. Strategy Interception
            scene = None
            if strategy_flag:
                # Ask Manager for a scene
                result = self.strategy_manager.select_strategy(strategy_flag)
                
                # Hybrid might return ("LLM_DELEGATE", "user") or (user, scene) or None
                if result:
                    if isinstance(result, tuple) and result[0] == "LLM_DELEGATE":
                        if result[1] != name: continue 
                        pass 
                    elif isinstance(result, tuple):
                        if result[0] != name: continue
                        scene = result[1]
                    else:
                         scene = result

            # 2. Check Triggers (Highest Priority)
            forced_run = False
            if not scene and self.check_triggers(name):
                logger.info(f"TRIGGER ACTIVATED for {name}")
                scene = next((s for s in data['scenes'] if "Build" in s['name']), data['scenes'][0])
                forced_run = True
                self.state["global_events"].remove("trigger_build")
            
            # 3. Check Schedule (if not forced and not strategy-forced)
            elif not scene and not self.is_active_window(name, data):
                continue
            
            # 4. Standard Selection
            if not scene:
                scene = self.inject_narrative(name) 
                if not scene:
                     scene = self.select_scene(name, data)

            if not scene:
                continue

            # 5. NOISE INJECTION
            if strategy_flag == "hybrid" or strategy_flag == "noise":
                 scene['commands'] = self.strategy_manager.apply_noise(scene['commands'])

            # Execute
            self.execute_scene(name, scene)
            
            if forced_run:
                 pass

        self._save_state()
        logger.info("--- Cycle Complete ---")

    def execute_scene(self, username, scene):
        logger.info(f"Executing Scene [{scene['name']}] for User [{username}]")
        
        home_dir = self.personas[username].get('home_dir', '/tmp')
        target_dir = scene.get('zone', home_dir)

        if username not in self.state['users']:
            self.state['users'][username] = {}
        self.state['users'][username]['last_scene'] = scene['name']
        self.state['users'][username]['last_run'] = time.time()

        for cmd in scene['commands']:
            full_cmd = f"cd {target_dir} && {cmd}"
            
            if self.dry_run:
                logger.info(f"[SIMULATION] [{username}] $ {full_cmd}")
            else:
                logger.info(f"[EXECUTE] [{username}] $ {full_cmd}")
        
        self.process_triggers(username, scene['commands'])
        time.sleep(1)

if __name__ == "__main__":
    load_env()
    parser = argparse.ArgumentParser(description="Deception Engine Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode (no system changes)")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--llm", action="store_true", help="Enable LLM dynamic scene generation")
    
    # Management Flags
    parser.add_argument("--generate-forecast", type=int, help="Generate N batch scenes for forecasting")
    parser.add_argument("--refresh-content", action="store_true", help="Refresh dynamic content assets (vulns/tokens)")

    # Strategy Flags
    parser.add_argument("--strategy-monthly", action="store_true", help="Force Monthly Plan Strategy")
    parser.add_argument("--strategy-template", action="store_true", help="Force Template Randomization Strategy")
    parser.add_argument("--strategy-cache", action="store_true", help="Force Cache Usage Strategy")
    parser.add_argument("--strategy-honeytoken", action="store_true", help="Force Honeytoken Generation")
    parser.add_argument("--strategy-vuln", action="store_true", help="Force Vulnerability Simulation")
    parser.add_argument("--strategy-forecast", action="store_true", help="Force Forecast Usage Strategy")
    parser.add_argument("--strategy-hybrid", action="store_true", help="Enable Hybrid 'Professional' Mode")

    args = parser.parse_args()
    
    # Init Engine
    engine = DeceptionEngine(dry_run=args.dry_run, use_llm=args.llm or args.generate_forecast or args.refresh_content or args.strategy_hybrid)

    # 1. Handle Management Tasks
    if args.refresh_content:
        engine.refresh_content()
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
    elif args.strategy_forecast: active_strategy = "forecast"
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
    else:
        engine.run(strategy_flag=active_strategy)
