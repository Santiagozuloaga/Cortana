#!/usr/bin/env python3
import sys
from pathlib import Path

# Set paths for P.A.R.A. structure
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root / "01_SRC"))
sys.path.insert(0, str(project_root / "00_SOPORTE"))

# Import core using correct ISO-SAGE nomenclature (date-first)
# We prioritize using the 'core' symlink for cleaner imports
import core

if __name__ == "__main__":
    core.main()
