"""Backward-compatibility shim: CLAW_2024_06_19_AGENT_V01 → agent.py

Allows old code using `from CLAW_2024_06_19_AGENT_V01 import ...` to work with the new shim.
"""
from agent import *  # noqa: F401,F403
