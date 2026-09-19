"""
Maritime Regulatory Compliance Engine.
Strictly decouples IMO Carbon Intensity Indicator (CII) from FuelEU Maritime (Regulation (EU) 2023/1805).
Returns structured compliance verdicts, margins, ratings, and statutory financial penalties.
"""

from typing import Any, Dict, Optional
from common.config_loader import load_config
from lca.fuel_eu import calculate_fueleu_compliance
from lca.imo_cii import calculate_imo_cii


class FleetRegulatoryEngine:
    """
    Evaluates international and regional maritime environmental compliance:
    1. IMO Operational Carbon Intensity Indicator (CII) Rating (A through E).
    2. FuelEU Maritime GHG Intensity Balance and Deficit Penalties.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            try:
                config = load_config("regulations.yaml")
            except Exception:
                config = {}
        self.config = config

        fueleu_cfg = self.config.get("fueleu_maritime", {})
        self.fueleu_target = fueleu_cfg.get("targets", {}).get("2025-2029", 89.3368)
        self.fueleu_penalty_rate = fueleu_cfg.get("statutory_penalty_eur_per_t_vlsfo_equiv", 2400.0)
        self.fueleu_energy_ref = fueleu_cfg.get("vlsfo_reference_energy_mj_tonne", 41000.0)
        self.eur_to_usd = fueleu_cfg.get("eur_to_usd", 1.08)

        cii_cfg = self.config.get("imo_cii", {})
        self.cii_reduction_pct = cii_cfg.get("annual_reduction_pct_2026", 11.0)

    def evaluate_imo_cii(
        self,
        vessel_class: str,
        capacity_val: float,
        co2_emissions_tonnes: float,
        distance_nm: float,
        annual_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate IMO Carbon Intensity Indicator compliance and rating.
        Under MARPOL Annex VI Reg 28, CII rating (A-E) is an annual operational metric.
        If annual_context is False (single-voyage leg), reports attained voyage intensity
        and instantaneous indicator, but sets rating='NOT_EVALUABLE' to avoid artificial penalties.
        """
        if distance_nm <= 0.0 or capacity_val <= 0.0:
            return {
                "attained_cii": 0.0,
                "required_cii": 0.0,
                "margin_pct": 0.0,
                "rating": "NOT_APPLICABLE",
                "voyage_instantaneous_rating": "NOT_APPLICABLE",
                "is_compliant": True,
                "status": "NOT_APPLICABLE",
            }

        # Offshore vessels are not rated under current MARPOL Annex VI Reg 28
        from optimization.canonical_mapper import canonicalize_vessel_type
        v_canon = canonicalize_vessel_type(vessel_class)
        if v_canon == "offshore_supply":
            return {
                "attained_cii": 0.0,
                "required_cii": 0.0,
                "margin_pct": 0.0,
                "rating": "NOT_APPLICABLE",
                "voyage_instantaneous_rating": "NOT_APPLICABLE",
                "is_compliant": True,
                "status": "NOT_APPLICABLE",
            }

        ship_type_mapped = "container" if v_canon == "cargo_feeder" else "cruise_passenger"
        co2_grams = co2_emissions_tonnes * 1e6

        cii_res = calculate_imo_cii(
            ship_type=ship_type_mapped,
            capacity_dwt=capacity_val,
            co2_emissions_grams=co2_grams,
            distance_nautical_miles=distance_nm,
            reduction_factor_pct=self.cii_reduction_pct,
        )

        if not annual_context:
            return {
                "attained_cii": round(float(cii_res["attained_cii"]), 3),
                "required_cii": round(float(cii_res["required_cii"]), 3),
                "margin_pct": round(float(cii_res["margin_pct"]), 2),
                "rating": "NOT_EVALUABLE",
                "voyage_instantaneous_rating": cii_res["rating"],
                "is_compliant": True,
                "status": "VOYAGE_INDICATOR_ONLY",
            }

        status = "COMPLIANT" if cii_res["is_compliant"] else "NON_COMPLIANT"
        return {
            "attained_cii": round(float(cii_res["attained_cii"]), 3),
            "required_cii": round(float(cii_res["required_cii"]), 3),
            "margin_pct": round(float(cii_res["margin_pct"]), 2),
            "rating": cii_res["rating"],
            "voyage_instantaneous_rating": cii_res["rating"],
            "is_compliant": bool(cii_res["is_compliant"]),
            "status": status,
        }

    def evaluate_fueleu(
        self,
        energy_consumed_mj: float,
        wtw_ghg_emissions_tonnes: float,
        scope_eea: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate FuelEU Maritime compliance balance and statutory penalty.
        """
        scoped_energy = energy_consumed_mj * scope_eea
        scoped_emissions = wtw_ghg_emissions_tonnes * scope_eea

        fueleu_res = calculate_fueleu_compliance(
            energy_consumed_mj=scoped_energy,
            wtw_ghg_emissions_tonnes_co2e=scoped_emissions,
            target_intensity_g_co2e_per_mj=self.fueleu_target,
            penalty_rate_eur_per_t_vlsfo_equiv=self.fueleu_penalty_rate,
            vlsfo_energy_density_mj_per_tonne=self.fueleu_energy_ref,
            eur_to_usd_rate=self.eur_to_usd,
        )

        status = "COMPLIANT" if fueleu_res["is_compliant"] else "NON_COMPLIANT"
        return {
            "attained_intensity_g_co2e_per_mj": round(float(fueleu_res["attained_intensity_g_co2e_per_mj"]), 2),
            "target_intensity_g_co2e_per_mj": round(float(fueleu_res["target_intensity_g_co2e_per_mj"]), 2),
            "compliance_balance_g_co2e": round(float(fueleu_res["compliance_balance_g_co2e"]), 2),
            "penalty_eur": round(float(fueleu_res["penalty_eur"]), 2),
            "penalty_usd": round(float(fueleu_res["penalty_usd"]), 2),
            "is_compliant": bool(fueleu_res["is_compliant"]),
            "status": status,
        }
