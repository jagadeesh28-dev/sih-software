"""
End-to-end integration tests connecting physics, prediction, LCA, and optimization.
"""

import sys
from pathlib import Path
import numpy as np
import pytest

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from tests.smoke_test import run_smoke_test


def test_smoke_test_run():
    """Verify that smoke test pipeline exits with 0."""
    status = run_smoke_test()
    assert status == 0
