"""Backward-compatibility shim: CLAW_2024_06_19_PROVIDERS_V01 → providers.py

Allows old code using `from CLAW_2024_06_19_PROVIDERS_V01 import ...` to work with the new shim.
"""
from providers import *  # noqa: F401,F403
