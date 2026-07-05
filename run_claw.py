#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path

# Set paths for P.A.R.A. structure
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root / "01_SRC"))
sys.path.insert(0, str(project_root / "00_SOPORTE"))

# Load the canonical ISO-SAGE core module dynamically
core_path = project_root / "01_SRC" / "2024-06-19_CLAW_CORE_V01.py"
spec = importlib.util.spec_from_file_location("claw_core", core_path)

if spec is None or spec.loader is None:
    raise ImportError(f"Could not load core module from {core_path}")

core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

if __name__ == "__main__":
    core.main()
