"""
Alternative fuel transition scenarios.
Section 22: Evaluates fleet transition across VLSFO, LNG, Bio-methanol, Green ammonia, LH2, and Shore power.
"""

from typing import Any, Dict, List
from common.config_loader import load_config


def get_alternative_fuel_scenarios() -> List[Dict[str, Any]]:
    """Return structured transition scenarios with containment penalties and availability limits."""
    fuel_cfg = load_config("fuels.yaml")
    pathways = fuel_cfg["pathways"]

    scenarios = [
        {
            "id": "scenario_1_vlsfo_baseline",
            "name": "Scenario 1: Conventional VLSFO Baseline",
            "primary_fuel": "vlsfo",
            "shore_power_enabled": False,
            "cargo_penalty_pct": pathways["vlsfo"]["cargo_capacity_penalty_pct"],
        },
        {
            "id": "scenario_2_lng_transition",
            "name": "Scenario 2: Fossil LNG Dual-Fuel",
            "primary_fuel": "fossil_lng",
            "shore_power_enabled": False,
            "cargo_penalty_pct": pathways["fossil_lng"]["cargo_capacity_penalty_pct"],
        },
        {
            "id": "scenario_3_bio_methanol",
            "name": "Scenario 3: Bio-Methanol Transition",
            "primary_fuel": "bio_methanol",
            "shore_power_enabled": False,
            "cargo_penalty_pct": pathways["bio_methanol"]["cargo_capacity_penalty_pct"],
        },
        {
            "id": "scenario_4_green_ammonia",
            "name": "Scenario 4: Green Ammonia Decarbonization",
            "primary_fuel": "green_ammonia",
            "shore_power_enabled": False,
            "cargo_penalty_pct": pathways["green_ammonia"]["cargo_capacity_penalty_pct"],
        },
        {
            "id": "scenario_5_liquid_hydrogen",
            "name": "Scenario 5: Liquid Hydrogen Deep Decarbonization",
            "primary_fuel": "liquid_hydrogen",
            "shore_power_enabled": False,
            "cargo_penalty_pct": pathways["liquid_hydrogen"]["cargo_capacity_penalty_pct"],
        },
        {
            "id": "scenario_6_shore_power_hybrid",
            "name": "Scenario 6: Bio-Methanol + In-Port Cold Ironing",
            "primary_fuel": "bio_methanol",
            "shore_power_enabled": True,
            "cargo_penalty_pct": pathways["bio_methanol"]["cargo_capacity_penalty_pct"],
        },
    ]
    return scenarios
