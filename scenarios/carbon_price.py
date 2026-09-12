"""
Carbon price sensitivity scenario definition.
Section 23: Configurable sweep across carbon tax regimes ($0 - $150 / tCO2e).
"""

from typing import List
from common.config_loader import load_config


def get_carbon_price_ladder() -> List[float]:
    """Retrieve configurable carbon price sweep levels."""
    cfg = load_config("scenarios.yaml")
    return cfg["carbon_price_sweep"]["sweep_values"]
