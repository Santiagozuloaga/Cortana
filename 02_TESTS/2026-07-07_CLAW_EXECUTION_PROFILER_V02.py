import time
import json
import sys
import os
import importlib
import cProfile
import pstats
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "01_SRC"))
sys.path.insert(0, str(BASE_DIR / "00_SOPORTE"))

# Lazy imports
import agent
import providers
import tools
import context
import task.tools
import memory_shim as memory

def profile_agent_run():
    print("\n--- Profiling Agent Execution Cycle (Mocked LLM) ---")

    state = agent.AgentState()
    config = {
        "model": "gpt-4o",
        "max_tokens": 4096,
        "permission_mode": "accept-all",
    }

    def mock_stream(*args, **kwargs):
        from providers import TextChunk, AssistantTurn
        yield TextChunk("Hello! ")
        yield TextChunk("I am a mocked response.")
        yield AssistantTurn("Hello! I am a mocked response.", [], 10, 5)

    pr = cProfile.Profile()

    # Patch at the entry point in agent.run
    with patch("agent.stream", side_effect=mock_stream):
        pr.enable()
        # Simulate a few turns
        for i in range(5):
            for event in agent.run(f"Turn {i}", state, config, "System Prompt"):
                pass
        pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    print(s.getvalue())

def profile_tool_dispatch():
    print("\n--- Profiling Tool Dispatch ---")
    config = {"permission_mode": "accept-all"}

    # Pre-read README.md content to avoid being dominated by I/O if possible
    # though Read tool does exactly that.

    pr = cProfile.Profile()
    pr.enable()
    # Mock Read tool call
    for _ in range(100):
        tools.execute_tool("Read", {"file_path": "README.md"}, config=config)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

def profile_memory_ops():
    print("\n--- Profiling Memory Operations ---")
    # Simulate searching memories
    pr = cProfile.Profile()
    pr.enable()
    for i in range(50):
        memory.search_memory(f"test {i}")
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

def main():
    profile_agent_run()
    profile_tool_dispatch()
    profile_memory_ops()

if __name__ == "__main__":
    main()
