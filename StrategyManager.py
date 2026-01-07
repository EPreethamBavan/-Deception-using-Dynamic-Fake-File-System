import random
import re
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.llm = orchestrator.llm_provider
        self.content_manager = getattr(orchestrator, 'content_manager', None)
        
        # Initialize dynamic factories
        self.contextual_noise = ContextualNoise(self.content_manager)
        self.honeytoken_factory = HoneytokenFactory(self.content_manager)
        self.vuln_feint = VulnerabilityFeint(self.content_manager)

    def select_strategy(self, strategy_flag):
        """
        Determines which strategy to use based on flags or Hybrid logic.
        """
        if strategy_flag == "monthly":
            return self.execute_monthly()
        elif strategy_flag == "template":
            return self.execute_template()
        elif strategy_flag == "cache":
            return self.execute_cache()
        elif strategy_flag == "honeytoken":
            return self.execute_honeytoken()
        elif strategy_flag == "vuln":
            return self.execute_vuln()
        elif strategy_flag == "forecast":
            return self.execute_forecast()
        elif strategy_flag == "hybrid":
            return self.execute_hybrid()
        else:
            return None

    def execute_monthly(self):
        """Strategy 1: Monthly Plan (Pre-defined long term)"""
        task = self.orch.get_monthly_task()
        if not task: return None
        
        if self.orch.use_llm:
            context = {"monthly_task": task, "notes": "Strictly follow monthly plan"}
            return self.llm.generate_scene("System", {"home_dir": "/tmp"}, context)
        else:
            # Fallback
            return {
                "name": f"Monthly Task: {task}",
                "category": "Routine",
                "zone": "/var/www/project",
                "commands": [f"echo 'Working on {task}'", "git status"]
            }

    def execute_template(self):
        """Strategy 3: Template + Random (Fuzzing)"""
        persona = random.choice(list(self.orch.personas.keys()))
        data = self.orch.personas[persona]
        if not data.get('scenes'): return None
        
        base_scene = random.choice(data['scenes'])
        new_scene = base_scene.copy()
        new_scene['name'] += " (Randomized)"
        
        # Load Fuzzing Rules
        fuzz_config = self.content_manager.get_template("fuzzing") if self.content_manager else {}
        files = fuzz_config.get("files", ["utils.py"])
        msgs = fuzz_config.get("commit_messages", ["Update"])

        new_cmds = []
        for cmd in base_scene['commands']:
            if "main.py" in cmd:
                cmd = cmd.replace("main.py", random.choice(files))
            if "git commit" in cmd:
                 cmd = f"git commit -m '{random.choice(msgs)}'"
            new_cmds.append(cmd)
        
        new_scene['commands'] = new_cmds
        return (persona, new_scene)

    def execute_cache(self):
        """Strategy 4: Pre-Made Cache (Loaded from File)"""
        if self.content_manager:
            scene = self.content_manager.get_template("cache")
            if scene: return scene
            
        # Hard fallback only if file missing
        return {
            "name": "Fallback Maintenance",
            "category": "Routine",
            "zone": "/tmp",
            "commands": ["ls -la"]
        }

    def execute_forecast(self):
        """Strategy 8: Batch Forecast (Time Machine)"""
        if self.content_manager:
            scene = self.content_manager.get_next_forecast_scene()
            if scene:
                # Scene object from batch likely has 'user' field
                user = scene.get("user", "sys_bob") # Default fallback
                return (user, scene)
        return None

    def execute_honeytoken(self):
        """Strategy 5: Honeytoken Factory (Dynamic or Static)"""
        if self.content_manager:
            cmds = self.content_manager.get_random_asset("honeytoken")
            if cmds:
                if isinstance(cmds, str):
                    cmds = [cmds]
                return {
                    "name": "Honeytoken Placement (Dynamic)",
                    "category": "Routine",
                    "zone": "/home/dev_alice",
                    "commands": cmds
                }
        return self.honeytoken_factory.generate()

    def execute_vuln(self):
        """Strategy 6: Vulnerability Feint (Dynamic or Static)"""
        if self.content_manager:
            cmds = self.content_manager.get_random_asset("vuln")
            if cmds:
                if isinstance(cmds, str):
                    cmds = [cmds]
                return {
                    "name": "Vulnerability Simulation (Dynamic)",
                    "category": "Anomaly",
                    "zone": "/etc",
                    "commands": cmds
                }
        return self.vuln_feint.generate()

    def execute_hybrid(self):
        """Strategy 7: Hybrid (The Professional Deceiver)"""
        roll = random.random()
        
        if roll < 0.25 and self.orch.use_llm:
            user = random.choice(list(self.orch.personas.keys()))
            logger.info(f"[Hybrid] Chose LIVE LLM for {user}")
            return ("LLM_DELEGATE", user) 

        elif roll < 0.45 and self.content_manager:
            scene = self.execute_forecast()
            if scene:
                logger.info("[Hybrid] Chose Forecast Strategy")
                return scene
            logger.info("[Hybrid] Forecast Empty -> Fallback to Template")
            return self.execute_template()

        elif roll < 0.70:
            logger.info("[Hybrid] Chose Template Strategy")
            return self.execute_template()
            
        elif roll < 0.90:
            logger.info("[Hybrid] Chose Cache Strategy")
            user = "sys_bob"
            selected_scene = self.execute_cache()
            return (user, selected_scene)
            
        elif roll < 0.95:
            logger.info("[Hybrid] Chose Honeytoken Strategy")
            return self.execute_honeytoken()
            
        elif roll < 0.98:
            logger.info("[Hybrid] Chose Vulnerability Strategy")
            return self.execute_vuln()
            
        elif self.content_manager:
            # 2% Chance of Auto-Refresh (Self-Healing)
            if random.random() < 0.5:
                logger.info("[Hybrid] Triggering Content Auto-Refresh")
                self.content_manager.refresh_assets()
                return ("sys_bob", {
                    "name": "System Maintenance (Asset Refresh)",
                    "category": "Maintenance",
                    "zone": "/var/log",
                    "commands": ["echo 'Maintenance Complete'", "Truncating logs..."]
                })
            elif random.random() < 0.5:
                 # 1% Chance Persona Evolution
                 self.content_manager.evolve_personas()
                 return None # No scene, just background task
            else:
                 # 1% Chance Breadcrumb Planting
                 crumb = self.content_manager.get_breadcrumb()
                 if not crumb:
                     self.content_manager.generate_breadcrumbs() # Replenish
                     crumb = "echo 'Replenishing breadcrumbs...'"
                 
                 return ("dev_alice", {
                     "name": "Accidental Leak (Breadcrumb)",
                     "category": "Anomaly",
                     "zone": "/tmp",
                     "commands": [f"echo '{crumb}' >> debug.log"]
                 })

        else:
            return self.execute_vuln() # Fallback if no content manager
    
    def apply_noise(self, commands):
        """Applies 'Contextual Noise' to ANY command list."""
        return self.contextual_noise.inject(commands)


# --- Dynamic Factories ---
class HoneytokenFactory:
    """Generates enticing fake credentials using templates."""
    def __init__(self, content_manager):
        self.cm = content_manager
        
    def generate(self):
        # Generate dynamic key
        keys = [
            "AIzaSy" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=20)),
            "ghp_" + "".join(random.choices("0123456789abcdef", k=30)),
            "sk_live_" + "".join(random.choices("0123456789", k=24))
        ]
        
        # Get template from JSON/Cache
        raw_cmd = self.cm.get_random_asset("honeytoken")
        if not raw_cmd:
             # Fallback if cache empty
             raw_cmd = "echo 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE' > .aws/credentials"

        # Inject dynamic key if template has placeholder (optional refinement)
        # For now, we assume the template might be complete or simple
        
        return {
            "name": "Honeytoken Placement",
            "category": "Routine",
            "zone": "/home/dev_alice",
            "commands": [raw_cmd] if isinstance(raw_cmd, str) else raw_cmd
        }

class VulnerabilityFeint:
    """Simulates bad security practices using templates."""
    def __init__(self, content_manager):
        self.cm = content_manager

    def generate(self):
        raw_cmd = self.cm.get_random_asset("vuln")
        if not raw_cmd:
            raw_cmd = "chmod 777 -R /var/www/html/uploads"
            
        return {
            "name": "Vulnerability Simulation",
            "category": "Anomaly",
            "zone": "/etc",
            "commands": [raw_cmd] if isinstance(raw_cmd, str) else raw_cmd
        }

class ContextualNoise:
    """Injects realistic developer 'noise' (typos, checks) from config."""
    def __init__(self, content_manager):
        self.cm = content_manager
        
    def inject(self, commands):
        config = self.cm.get_template("fuzzing") or {} # Abuse get_template for config dicts
        typos = self.cm.get_template("typos") or {}
        
        # If fallback needed
        if not typos: typos = {"git": ["gti"]}
        
        final_cmds = []
        
        # 1. Navigation Fluff
        if random.random() < 0.3:
            final_cmds.extend(["ls -la", "pwd"])
            
        for cmd in commands:
            parts = cmd.split()
            base = parts[0]
            
            # 2. Status Anxiety
            if base in ["git", "docker"] and random.random() < 0.2:
                final_cmds.append(f"{base} status" if base == "git" else f"{base} ps")
            
            # 3. Typos
            if base in typos and random.random() < 0.1:
                bad_cmd = cmd.replace(base, random.choice(typos[base]), 1)
                final_cmds.append(bad_cmd)
            
            final_cmds.append(cmd)
            
        return final_cmds
