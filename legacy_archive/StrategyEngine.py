import random
import re
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyEngine:
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.llm = orchestrator.llm_provider
        self.content_manager = getattr(orchestrator, 'content_manager', None)
        self.contextual_noise = ContextualNoise()
        self.honeytoken_factory = HoneytokenFactory()
        self.vuln_feint = VulnerabilityFeint()

    def select_strategy(self, strategy_flag):
        if strategy_flag == "monthly": return self.execute_monthly()
        elif strategy_flag == "template": return self.execute_template()
        elif strategy_flag == "cache": return self.execute_cache()
        elif strategy_flag == "honeytoken": return self.execute_honeytoken()
        elif strategy_flag == "vuln": return self.execute_vuln()
        elif strategy_flag == "forecast": return self.execute_forecast()
        elif strategy_flag == "hybrid": return self.execute_hybrid()
        return None

    def execute_monthly(self):
        task = self.orch.get_monthly_task()
        if not task: return None
        if self.orch.use_llm:
            context = {"monthly_task": task, "notes": "Strictly follow monthly plan"}
            return self.llm.generate_scene("System", {"home_dir": "/tmp"}, context)
        return {
            "name": f"Monthly Task: {task}", "category": "Routine", "zone": "/var/www/project",
            "commands": [f"echo 'Working on {task}'", "git status"]
        }

    def execute_template(self):
        persona = random.choice(list(self.orch.personas.keys()))
        data = self.orch.personas[persona]
        if not data.get('scenes'): return None
        base_scene = random.choice(data['scenes'])
        new_scene = base_scene.copy()
        new_scene['name'] += " (Randomized)"
        new_cmds = []
        for cmd in base_scene['commands']:
            if "main.py" in cmd: cmd = cmd.replace("main.py", random.choice(["utils.py", "config.py", "app.py"]))
            if "git commit" in cmd:
                 msgs = ["Fix typo", "WIP", "Update logic", "Refactor"]
                 cmd = f"git commit -m '{random.choice(msgs)}'"
            new_cmds.append(cmd)
        new_scene['commands'] = new_cmds
        return (persona, new_scene)

    def execute_cache(self):
        return {
            "name": "Cached Maintenance", "category": "Routine", "zone": "/tmp",
            "commands": ["tar -czf backup.tar.gz /var/log", "mv backup.tar.gz /mnt/backup"]
        }

    def execute_forecast(self):
        if self.content_manager:
            scene = self.content_manager.get_next_forecast_scene()
            if scene:
                user = scene.get("user", "sys_bob")
                return (user, scene)
        return None

    def execute_honeytoken(self):
        # cmds = None
        # if self.content_manager:
        #     cmds = self.content_manager.get_random_asset("honeytoken")
        
        # if cmds:
        #     if isinstance(cmds, str): cmds = [cmds]
        #     return {
        #         "name": "Honeytoken Placement (Dynamic)",
        #         "category": "Routine",
        #         "zone": "/home/dev_alice",
        #         "commands": cmds
        #     }
        
        return self.honeytoken_factory.generate()

    def execute_vuln(self):
        cmds = None
        if self.content_manager:
            cmds = self.content_manager.get_random_asset("vuln")
        
        if cmds:
            if isinstance(cmds, str): cmds = [cmds]
            return {
                "name": "Vulnerability Simulation (Dynamic)",
                "category": "Anomaly",
                "zone": "/etc",
                "commands": cmds
            }
        return self.vuln_feint.generate()

    # def execute_hybrid(self):
    #     return None
