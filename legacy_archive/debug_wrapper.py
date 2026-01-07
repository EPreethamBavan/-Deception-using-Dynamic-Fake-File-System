
import sys
import traceback
import logging

# Suppress other logs
logging.basicConfig(level=logging.ERROR)

try:
    import Orchestrator_Paper1
    # Enable LLM/ContentManager flags to ensure StrategyManager is fully active
    engine = Orchestrator_Paper1.DeceptionEngine(dry_run=True, use_llm=True) 
    print("Init success. Running cycle...")
    engine.run(strategy_flag="hybrid")
    print("Run success.")
except Exception:
    traceback.print_exc()
