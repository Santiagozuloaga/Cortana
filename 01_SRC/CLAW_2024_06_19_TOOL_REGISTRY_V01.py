"""Backward-compatibility shim: CLAW_2024_06_19_TOOL_REGISTRY_V01 → tool_registry.py

Allows old code using `from CLAW_2024_06_19_TOOL_REGISTRY_V01 import ...` to work with tool_registry.
"""
from tool_registry import *  # noqa: F401,F403
