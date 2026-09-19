#!/usr/bin/env python3
"""
SIH26138 — Egreen Quanta: Single-Command Master Reproduction Runner.
Root invocation wrapper for scripts/reproduce_release.py.
"""
import sys
from pathlib import Path

# Delegate directly to scripts/reproduce_release.py
scripts_dir = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(scripts_dir))
import reproduce_release

if __name__ == "__main__":
    sys.exit(reproduce_release.main())
