"""
Configurable Fuel Pathway Registry based on IMO MEPC.391(81).
Avoids universal constants; loads certified supply chain factors from configs/fuels.yaml.
"""

from typing import Any, Dict, List, Optional
from common.config_loader import load_config


class FuelPathwayRegistry:
    """Registry managing maritime fuel pathways, LHVs, WtT, and TtW factors."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = load_config("fuels.yaml")
        self.config = config
        self.pathways: Dict[str, Dict[str, Any]] = self.config["pathways"]
        self.gwp_factors: Dict[str, float] = self.config["global_gwp_factors"]

    def get_pathway(self, fuel_key: str) -> Dict[str, Any]:
        """Retrieve pathway details for a specific fuel."""
        if fuel_key not in self.pathways:
            raise KeyError(f"Fuel pathway '{fuel_key}' not found in registry. Available: {list(self.pathways.keys())}")
        return self.pathways[fuel_key]

    def list_available_fuels(self) -> List[str]:
        """Return list of configured fuel keys."""
        return list(self.pathways.keys())
