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
        
        # Initialize Defender Agent (OODA Loop)
        self.defender_agent = DefenderAgent(self.llm, self.content_manager)

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
        """Strategy 7: Hybrid (The Professional Deceiver) - Powered by OODA Loop."""
        # Use the Defender Agent to decide (OODA Loop)
        decision = self.defender_agent.decide()
        
        logger.info(f"[Defender Agent] Decision: {decision['strategy']} ({decision['reason']})")
        
        if decision['strategy'] == "LIVE_LLM":
            user = random.choice(list(self.orch.personas.keys()))
            return ("LLM_DELEGATE", user)

        elif decision['strategy'] == "SKILL":
            return self.execute_skill()

        elif decision['strategy'] == "FORECAST":
            scene = self.execute_forecast()
            if scene: return scene
            return self.execute_template() # Fallback

        elif decision['strategy'] == "TEMPLATE":
            return self.execute_template()
            
        elif decision['strategy'] == "CACHE":
            user = "sys_bob"
            selected_scene = self.execute_cache()
            return (user, selected_scene)
            
        elif decision['strategy'] == "HONEYTOKEN":
            return self.execute_honeytoken()
            
        elif decision['strategy'] == "VULN":
            return self.execute_vuln()
            
        elif decision['strategy'] == "MAINTENANCE":
            # Self-Healing / Refresh
            self.content_manager.refresh_assets()
            scene = self.content_manager.get_template("maintenance_refresh")
            if not scene:
                 scene = {
                    "name": "System Maintenance (Asset Refresh)",
                    "category": "Maintenance",
                    "zone": "/var/log",
                    "commands": ["echo 'Maintenance Complete'"]
                 }
            return ("sys_bob", scene)

        elif decision['strategy'] == "BREADCRUMB":
             crumb = self.content_manager.get_breadcrumb()
             if not crumb:
                 self.content_manager.generate_breadcrumbs()
                 crumb = self.content_manager.get_breadcrumb() # Retry
                 if not crumb:
                     crumb = "Error: Connection check failed - timeout"
             
             tpl = self.content_manager.get_template("breadcrumb_leak")
             if tpl:
                 scene = json.loads(json.dumps(tpl))
                 scene["commands"] = [c.format(crumb=crumb) for c in scene["commands"]]
             else:
                 scene = {
                     "name": "Accidental Leak (Breadcrumb)",
                     "category": "Anomaly",
                     "zone": "/tmp",
                     "commands": [f"echo '{crumb}' >> debug.log"]
                 }
             return ("dev_alice", scene)

        else:
            return self.execute_template()

    def execute_skill(self):
        """Executes a Skill (OpenClaw-style tool use)."""
        # Pick a persona with skills
        candidates = [p for p, data in self.orch.personas.items() if "skills" in data]
        if not candidates: return self.execute_template()
        
        user = random.choice(candidates)
        user_data = self.orch.personas[user]
        user_skills = user_data.get("skills", [])
        home = user_data.get("home_dir", f"/home/{user}")
        
        # Dynamic Import / Instantiation
        # heuristic: map string "git" to GitSkill class
        skill_map = {
            "git": "GitSkill",
            "docker": "DockerSkill"
        }
        
        selected_skill_name = None
        for s in user_skills:
            if s in skill_map:
                selected_skill_name = s
                break
        
        if not selected_skill_name: return self.execute_template()
        
        # Instantiate and run
        try:
            # Local import to avoid circular dependency issues at top level
            if selected_skill_name == "git":
                from skills.git_skill import GitSkill
                skill = GitSkill(user, home)
            elif selected_skill_name == "docker":
                from skills.docker_skill import DockerSkill
                skill = DockerSkill(user, home)
            else:
                 return self.execute_template()
                 
            commands = skill.generate_activity()
            
            return (user, {
                "name": f"Skill Execution: {selected_skill_name.title()}",
                "category": "Skill",
                "zone": home,
                "commands": commands
            })
        except Exception as e:
            logger.error(f"Skill execution failed: {e}")
            return self.execute_template()

    
    def apply_noise(self, commands):
        """Applies 'Contextual Noise' to ANY command list."""
        return self.contextual_noise.inject(commands)


# --- Agentic Defender (OODA Loop) ---
class DefenderAgent:
    """
    Implements the Observe-Orient-Decide-Act (OODA) loop for proactive deception.
    """
    def __init__(self, llm, content_manager):
        self.llm = llm
        self.cm = content_manager
        self.state = {
            "alert_level": "LOW",
            "last_action": None,
            "consecutive_idle": 0
        }

    def decide(self):
        """
        Executes the OODA loop to select the next best strategy.
        """
        # 1. OBSERVE (Mocked for now - normally would read logs/history)
        # In a real implementation, we'd check if an attacker is probing.
        # For now, we simulate 'Alert Level' changes based on RNG or mock triggers.
        observation = self._observe_environment()
        
        # 2. ORIENT (Context analysis)
        # 3. DECIDE (Select Strategy)
        if observation == "ATTACK_DETECTED":
            return {"strategy": "HONEYTOKEN", "reason": "Attack detected, deploying honeytoken"}
        
        elif observation == "PROBING_DETECTED":
            return {"strategy": "VULN", "reason": "Probing detected, feigning vulnerability"}
            
        elif observation == "SYSTEM_STALE":
            return {"strategy": "MAINTENANCE", "reason": "System stale, refreshing assets"}
            
        else:
            # Standard probabilistic mix for "NORMAL" state
            roll = random.random()
            if roll < 0.30 and self.llm: return {"strategy": "LIVE_LLM", "reason": "Normal traffic generation (LLM)"}
            if roll < 0.45: return {"strategy": "SKILL", "reason": "Persona using specialized skill"}
            if roll < 0.60: return {"strategy": "FORECAST", "reason": "Executing planned forecast"}
            if roll < 0.70: return {"strategy": "TEMPLATE", "reason": "Standard template activity"}
            if roll < 0.85: return {"strategy": "CACHE", "reason": "Cached background noise"}
            if roll < 0.90: return {"strategy": "BREADCRUMB", "reason": "Leaking info"}
            if roll < 0.95: return {"strategy": "HONEYTOKEN", "reason": "Random trap placement"}
            return {"strategy": "VULN", "reason": "Random vulnerability feint"}

    def _observe_environment(self):
        """
        Simulates observing system state. 
        TODO: Connect to actual 'sys_core.py' metrics or logic.
        """
        # Simple simulation logic
        if random.random() < 0.05: return "ATTACK_DETECTED"
        if random.random() < 0.10: return "PROBING_DETECTED"
        
        # Check if we should refresh
        if random.random() < 0.02: return "SYSTEM_STALE"
        
        return "NORMAL"

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
