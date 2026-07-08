import time
import json
import sys
import os
import importlib
import cProfile
import pstats
import io
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "01_SRC"))
sys.path.insert(0, str(BASE_DIR / "00_SOPORTE"))

def profile_imports():
    print("--- Profiling Imports ---")
    modules = [
        ("config", "2024-06-19_CLAW_CONFIG_V01"),
        ("providers", "2024-06-19_CLAW_PROVIDERS_V01"),
        ("tools", "2024-06-19_CLAW_TOOLS_V01"),
        ("agent", "2024-06-19_CLAW_AGENT_V01"),
        ("memory", "2024-06-19_CLAW_MEMORY_SHIM_V01"),
        ("task_tools", "task.tools"),
    ]

    results = {}
    for name, path in modules:
        start = time.perf_counter()
        try:
            importlib.import_module(path)
            end = time.perf_counter()
            results[name] = end - start
            print(f"{name:15}: {results[name]:.4f}s")
        except Exception as e:
            print(f"{name:15}: FAILED ({e})")
    return results

def profile_execution_cycle():
    print("\n--- Profiling Execution Cycle ---")

    # 1. Tool Registration
    print("Profiling Tool Registration...")
    pr = cProfile.Profile()
    pr.enable()
    import tools
    importlib.reload(tools)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

    # 2. Memory Search
    print("Profiling Memory Search...")
    import memory
    start = time.perf_counter()
    memory.search_memory("test query")
    end = time.perf_counter()
    print(f"Memory Search: {end - start:.4f}s")

    # 3. System Prompt Building
    print("Profiling System Prompt Construction...")
    import context
    # Warm up caches
    context.build_system_prompt()
    start = time.perf_counter()
    for _ in range(20):
        context.build_system_prompt()
    end = time.perf_counter()
    print(f"Build System Prompt (avg of 20): {(end - start)/20:.4f}s")

    # 4. Task Listing
    print("Profiling Task Listing...")
    from task.tools import list_tasks
    try:
        start = time.perf_counter()
        list_tasks()
        end = time.perf_counter()
        print(f"List Tasks: {end - start:.4f}s")
    except Exception as e:
        print(f"List Tasks: FAILED ({e})")

    # 5. Model Provider Setup Overhead
    print("Profiling Provider Setup Overhead...")
    import providers
    start = time.perf_counter()
    providers.detect_provider("gpt-4o")
    providers.get_api_key("openai", {"openai_api_key": "test"})
    end = time.perf_counter()
    print(f"Provider metadata ops: {end - start:.4f}s")

def main():
    profile_imports()
    profile_execution_cycle()

if __name__ == "__main__":
    main()
