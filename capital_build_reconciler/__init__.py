"""Factory-facing package for Capital Build Reconciler."""

from __future__ import annotations

import sys
from pathlib import Path


_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists():
    src_path = str(_SRC)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

__version__ = "0.0.2"

__all__ = ["__version__"]
