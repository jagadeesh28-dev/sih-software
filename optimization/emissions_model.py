"""
Maritime Emissions Accounting Engine.
Implements IMO MEPC.391(81) Well-to-Wake Lifecycle GHG calculations,
fugitive methane slip tracking, and alternative fuel energy equivalence conversions.
"""

from typing import Any, Dict, Optional
import numpy as np

from lca.fuel_registry import FuelPathwayRegistry
from lca.well_to_wake import calculate_well_to_wake
from lca.methane_slip import calculate_methane_slip


class FleetEmissionsEngine:
    """
    Computes voyage lifecycle emissions, fuel mass conversion under equivalent energy,
    and methane slip contributions for candidate operational strategies.
    """

    def __init__(self, registry: Optional[FuelPathwayRegistry] = None):
        self.registry = registry or FuelPathwayRegistry()
        self.vlsfo_lhv = self.registry.get_pathway("vlsfo")["lhv_mj_kg"]

    def convert_fuel_mass_for_pathway(
        self,
        baseline_vlsfo_kg: float,
        target_fuel_type: str,
        engine_efficiency_relative: float = 1.0,
    ) -> float:
        """
        Convert baseline VLSFO mass requirement to equivalent alternative fuel mass based on LHV:
        m_target = m_vlsfo * (LHV_vlsfo / LHV_target) / eta_rel
        """
        if baseline_vlsfo_kg <= 0.0:
            return 0.0

        target_pathway = self.registry.get_pathway(target_fuel_type)
        target_lhv = target_pathway["lhv_mj_kg"]

        equivalent_mass_kg = (
            baseline_vlsfo_kg
            * (self.vlsfo_lhv / target_lhv)
            / max(engine_efficiency_relative, 0.1)
        )
        return float(equivalent_mass_kg)

    def compute_leg_emissions(
        self,
        fuel_mass_kg: float,
        fuel_type: str,
    ) -> Dict[str, float]:
        """
        Calculate full Well-to-Wake emissions breakdown for a voyage leg.
        """
        wtw_res = calculate_well_to_wake(
            fuel_mass_kg=fuel_mass_kg,
            fuel_type=fuel_type,
            registry=self.registry,
        )

        pathway = self.registry.get_pathway(fuel_type)
        slip_fraction = pathway.get("methane_slip_fraction", 0.0)
        slip_res = calculate_methane_slip(
            fuel_mass_kg=fuel_mass_kg,
            methane_slip_fraction=slip_fraction,
            lhv_mj_per_kg=pathway["lhv_mj_kg"],
            methane_gwp100=self.registry.gwp_factors.get("ch4_gwp100", 29.8),
        )

        return {
            "fuel_type": fuel_type,
            "fuel_mass_tonnes": fuel_mass_kg / 1000.0,
            "fuel_energy_mj": wtw_res["total_energy_mj"],
            "wtt_tonnes_co2e": wtw_res["wtt_tonnes_co2e"],
            "ttw_co2_tonnes": wtw_res["ttw_co2_tonnes"],
            "ttw_ch4_tonnes_co2e": wtw_res["ttw_ch4_tonnes_co2e"],
            "ttw_n2o_tonnes_co2e": wtw_res["ttw_n2o_tonnes_co2e"],
            "ttw_total_tonnes_co2e": wtw_res["ttw_total_tonnes_co2e"],
            "methane_slip_tonnes_co2e": slip_res["methane_emissions_tonnes_co2e"],
            "wtw_total_tonnes_co2e": wtw_res["wtw_total_tonnes_co2e"],
            "wtw_intensity_g_co2e_per_mj": wtw_res["wtw_intensity_g_co2e_per_mj"],
        }
