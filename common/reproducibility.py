"""
Reproducibility infrastructure: deterministic seed setting and environment auditing.
Section 30: Every experiment must record git commit, configuration, seed, and environment.
"""

import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from .logger import get_logger

logger = get_logger(__name__)


def set_seed(seed: int = 42) -> None:
    """
    Enforce deterministic execution across Python, NumPy, and PyTorch (if present).

    Args:
        seed: Integer random seed.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    # Optional torch seed if installed
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    logger.debug(f"Deterministic seed set to {seed}")


def get_git_commit() -> Optional[str]:
    """Retrieve current git commit hash if running in a git repository."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=3,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_NON_GIT_WORKSPACE"


def audit_environment() -> Dict[str, Any]:
    """
    Capture comprehensive hardware, OS, and library versions for scientific reproducibility.

    Returns:
        Dictionary detailing hardware, software, and dependency environment.
    """
    packages = {}
    for pkg in [
        "numpy", "scipy", "pandas", "scikit-learn", "lightgbm", "xgboost",
        "pymoo", "pulp", "statsmodels", "pyyaml", "pydantic", "matplotlib",
        "plotly", "streamlit", "onnx", "onnxruntime", "pytest"
    ]:
        try:
            mod = __import__(pkg.replace("-", "_"))
            packages[pkg] = getattr(mod, "__version__", "installed")
        except ImportError:
            packages[pkg] = "not_installed"

    env_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "git_commit": get_git_commit(),
        "packages": packages,
    }
    return env_data


def save_metadata(
    output_path: Path,
    experiment_id: str,
    seed: int,
    config_snapshot: Dict[str, Any],
    additional_info: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Save experiment metadata to a reproducible JSON artifact.

    Args:
        output_path: Target JSON file path.
        experiment_id: Identifier of the experiment (e.g. 'EXP01', 'SMOKE_TEST').
        seed: Random seed used.
        config_snapshot: Snapshot of configurations used.
        additional_info: Optional dictionary of experiment-specific metrics.

    Returns:
        Path to saved metadata file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "experiment_id": experiment_id,
        "seed": seed,
        "environment": audit_environment(),
        "config_snapshot": config_snapshot,
        "additional_info": additional_info or {},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved experiment metadata: {output_path}")
    return output_path
