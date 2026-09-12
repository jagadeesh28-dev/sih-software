"""
Unit tests validating physical dimensions, monotonic behaviour, and calculation consistency.
Section 33: Minimum tests for Physics, LCA, Optimization, and QPSO.
"""

import sys
from pathlib import Path
import numpy as np
import pytest

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from physics.holtrop_mennen import calculate_calm_water_resistance
from physics.propulsion import calculate_propulsion_power, calculate_fuel_rate
from physics.resistance_model import VesselResistanceModel
from lca.methane_slip import calculate_methane_slip
from lca.fuel_registry import FuelPathwayRegistry
from lca.well_to_wake import calculate_well_to_wake
from lca.imo_cii import calculate_imo_cii
from lca.fuel_eu import calculate_fueleu_compliance
from optimization.variables import SolutionChromosome, VesselAssignmentDecision
from optimization.repair import SolutionRepairOperator
from optimization.qpso import QPSOOptimizer
from optimization.problem import MaritimeFleetProblem


def test_physics_monotonicity_and_positive_resistance():
    """Verify that calm water resistance increases monotonically with speed and remains strictly positive."""
    speeds = [10.0, 12.0, 14.0, 16.0, 18.0]  # knots
    model = VesselResistanceModel("container_feeder")
    resistances = []

    for sp in speeds:
        res = model.compute_total_resistance(speed_knots=sp)
        r_tot = res["r_total_newtons"]
        assert r_tot > 0.0, f"Resistance should be positive, got {r_tot} at speed {sp}"
        assert res["power"]["pb_kw"] > 0.0
        assert res["fuel"]["total_fuel_kg_h"] > 0.0
        resistances.append(r_tot)

    # Monotonicity check
    for i in range(len(resistances) - 1):
        assert resistances[i + 1] > resistances[i], (
            f"Resistance should strictly increase with speed: {resistances[i]} vs {resistances[i+1]}"
        )


def test_methane_slip_dimensional_consistency():
    """
    Verify dimensional consistency of methane slip:
    fuel_mass_kg * (LHV_MJ_per_kg) = fuel_energy_MJ
    fuel_mass_kg * methane_slip_fraction = unburned_methane_mass_kg
    emissions = mass_g * GWP
    """
    fuel_mass_kg = 1000.0  # 1 tonne LNG
    slip_frac = 0.022      # 2.2%
    lhv = 48.0            # MJ/kg
    gwp = 29.8

    res = calculate_methane_slip(
        fuel_mass_kg=fuel_mass_kg,
        methane_slip_fraction=slip_frac,
        lhv_mj_per_kg=lhv,
        methane_gwp100=gwp,
    )

    assert res["fuel_energy_mj"] == pytest.approx(48000.0)
    assert res["unburned_methane_kg"] == pytest.approx(22.0)
    assert res["unburned_methane_g"] == pytest.approx(22000.0)
    assert res["methane_emissions_g_co2e"] == pytest.approx(22000.0 * 29.8)
    assert res["methane_emissions_tonnes_co2e"] == pytest.approx((22000.0 * 29.8) / 1e6)


def test_lca_well_to_wake_aggregation():
    """Verify that WtW = WtT + TtW."""
    registry = FuelPathwayRegistry()
    res = calculate_well_to_wake(
        fuel_mass_kg=5000.0,
        fuel_type="vlsfo",
        registry=registry,
    )

    assert res["wtw_total_tonnes_co2e"] > 0.0
    expected_sum = res["wtt_tonnes_co2e"] + res["ttw_total_tonnes_co2e"]
    assert res["wtw_total_tonnes_co2e"] == pytest.approx(expected_sum, rel=1e-5)
    assert res["wtw_intensity_g_co2e_per_mj"] > 0.0


def test_imo_cii_calculation():
    """Verify IMO CII calculation and compliance rating output."""
    res = calculate_imo_cii(
        ship_type="container",
        capacity_dwt=15000.0,
        co2_emissions_grams=25000000.0,
        distance_nautical_miles=890.0,
        reduction_factor_pct=11.0,
    )
    assert res["attained_cii"] > 0.0
    assert res["required_cii"] > 0.0
    assert res["rating"] in ["A", "B", "C", "D", "E"]
    assert isinstance(res["is_compliant"], bool)


def test_fueleu_maritime_decoupling():
    """Verify FuelEU evaluates intensity and penalties independently."""
    res_compliant = calculate_fueleu_compliance(
        energy_consumed_mj=1000000.0,
        wtw_ghg_emissions_tonnes_co2e=80.0,  # 80 g/MJ < 89.34 target
    )
    assert res_compliant["is_compliant"] is True
    assert res_compliant["penalty_eur"] == 0.0

    res_non_compliant = calculate_fueleu_compliance(
        energy_consumed_mj=1000000.0,
        wtw_ghg_emissions_tonnes_co2e=95.0,  # 95 g/MJ > 89.34 target
    )
    assert res_non_compliant["is_compliant"] is False
    assert res_non_compliant["penalty_eur"] > 0.0


def test_chromosome_repair_operator():
    """Verify that repair operator projects speeds and bounds correctly."""
    chrom = SolutionChromosome(
        assignments=[
            VesselAssignmentDecision(
                vessel_id="V1",
                leg_id="leg1",
                speed_knots=25.0,  # Exceeds max 20.0
                cargo_allocation_teu=1200.0,  # Exceeds max 1000.0
            ),
            VesselAssignmentDecision(
                vessel_id="V2",
                leg_id="leg1",
                speed_knots=5.0,   # Below min 10.0
                cargo_allocation_teu=400.0,
            ),
        ]
    )

    repair = SolutionRepairOperator(
        min_speed_knots=10.0,
        max_speed_knots=20.0,
        max_vessel_capacity_teu=1000.0,
        total_cargo_demand_teu=850.0,
    )

    repaired = repair.repair_chromosome(chrom)
    assert repaired.assignments[0].speed_knots == 20.0
    assert repaired.assignments[1].speed_knots == 10.0
    total_cargo = sum(a.cargo_allocation_teu for a in repaired.assignments)
    assert total_cargo == pytest.approx(850.0, abs=1.0)


def test_qpso_determinism_and_bounds():
    """Verify deterministic QPSO execution with fixed seed and boundary enforcement."""
    prob = MaritimeFleetProblem(vessel_ids=["V1", "V2"])
    qpso1 = QPSOOptimizer(n_particles=10, max_iterations=5, seed=999)
    res1 = qpso1.optimize(prob)

    qpso2 = QPSOOptimizer(n_particles=10, max_iterations=5, seed=999)
    res2 = qpso2.optimize(prob)

    np.testing.assert_allclose(res1["best_x"], res2["best_x"])
    assert res1["best_score"] == pytest.approx(res2["best_score"])
    # Check within problem bounds
    assert np.all(res1["best_x"] >= prob.xl)
    assert np.all(res1["best_x"] <= prob.xu)
