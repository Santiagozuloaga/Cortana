"""Backward-compatibility shim for the short import name `agent`.

This module re-exports the canonical agent implementation (2024-06-19_CLAW_AGENT_V01.py)
to allow short imports like `import agent` instead of the full ISO-SAGE naming convention.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CANONICAL_PATH = Path(__file__).with_name("2024-06-19_CLAW_AGENT_V01.py")
_spec = importlib.util.spec_from_file_location("_claw_agent_canonical", _CANONICAL_PATH)

if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load canonical agent module from {_CANONICAL_PATH}")

_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

# Re-export all public names
for _name in dir(_module):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_module, _name)

__all__ = getattr(_module, "__all__", [name for name in dir(_module) if not name.startswith("_")])
