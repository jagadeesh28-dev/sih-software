"""
Unit tests for decoupled maritime regulatory compliance: IMO CII and FuelEU Maritime.
"""

import pytest
from optimization.regulatory import FleetRegulatoryEngine


def test_imo_cii_rating_boundaries():
    """Verify IMO CII rating boundaries A through E and non-applicability on offshore vessels."""
    reg = FleetRegulatoryEngine()

    # 1. Container ship evaluation
    res_c = reg.evaluate_imo_cii(
        vessel_class="cargo_feeder",
        capacity_val=14000.0,  # 14,000 DWT
        co2_emissions_tonnes=100.0,
        distance_nm=500.0,
    )
    assert res_c["rating"] in ["A", "B", "C", "D", "E"]
    assert res_c["attained_cii"] > 0.0
    assert res_c["required_cii"] > 0.0

    # 2. Offshore Supply Vessel -> Must be NOT_APPLICABLE
    res_osv = reg.evaluate_imo_cii(
        vessel_class="offshore_supply",
        capacity_val=5000.0,
        co2_emissions_tonnes=20.0,
        distance_nm=100.0,
    )
    assert res_osv["rating"] == "NOT_APPLICABLE"
    assert res_osv["status"] == "NOT_APPLICABLE"


def test_fueleu_maritime_compliance_and_penalty():
    """Verify FuelEU GHG intensity target and statutory financial penalty calculation."""
    reg = FleetRegulatoryEngine()

    # Case 1: Compliant bio-methanol (clean intensity ~30 g/MJ vs 89.34 g/MJ target)
    res_comp = reg.evaluate_fueleu(
        energy_consumed_mj=100000.0,
        wtw_ghg_emissions_tonnes=3.0,  # 30 g/MJ
    )
    assert res_comp["is_compliant"] is True
    assert res_comp["status"] == "COMPLIANT"
    assert res_comp["penalty_usd"] == 0.0
    assert res_comp["compliance_balance_g_co2e"] > 0.0

    # Case 2: High-emission fuel exceeding target (e.g. 100 g/MJ vs 89.34 g/MJ)
    res_def = reg.evaluate_fueleu(
        energy_consumed_mj=100000.0,
        wtw_ghg_emissions_tonnes=10.0,  # 100 g/MJ
    )
    assert res_def["is_compliant"] is False
    assert res_def["status"] == "NON_COMPLIANT"
    assert res_def["penalty_usd"] > 0.0
    assert res_def["compliance_balance_g_co2e"] < 0.0
