"""
Reproducibility verification for benchmark runs.
Ensures common random numbers are strictly passed to identical problem instances.
"""

from typing import List
import numpy as np


def generate_common_random_seeds(n_seeds: int = 30, base_seed: int = 42) -> List[int]:
    """Generate fixed sequence of seeds for reproducibility."""
    rng = np.random.default_rng(base_seed)
    return [int(s) for s in rng.integers(1000, 999999, size=n_seeds)]
