"""
Unit tests for IMO MEPC.391(81) Well-to-Wake lifecycle emissions and fugitive methane slip.
"""

import pytest
import numpy as np
from lca.fuel_registry import FuelPathwayRegistry
from lca.methane_slip import calculate_methane_slip
from optimization.emissions_model import FleetEmissionsEngine


def test_methane_slip_mass_and_gwp_balance():
    """Verify exact dimensional tracking of methane slip mass and GWP100."""
    fuel_mass_kg = 1000.0  # 1 tonne LNG
    slip_fraction = 0.022  # 2.2% slip for 4-stroke LPDF
    lhv = 48.0             # MJ/kg
    gwp = 29.8             # IPCC AR6 100-year GWP

    res = calculate_methane_slip(
        fuel_mass_kg=fuel_mass_kg,
        methane_slip_fraction=slip_fraction,
        lhv_mj_per_kg=lhv,
        methane_gwp100=gwp,
    )

    # 1. Escaped mass: 1000 kg * 0.022 = 22 kg
    assert pytest.approx(res["unburned_methane_kg"], rel=1e-5) == 22.0
    assert pytest.approx(res["unburned_methane_g"], rel=1e-5) == 22000.0

    # 2. GWP CO2e: 22 kg * 29.8 = 655.6 kg CO2e = 0.6556 tonnes CO2e
    assert pytest.approx(res["methane_emissions_tonnes_co2e"], rel=1e-5) == 0.6556

    # 3. Energy: 1000 kg * 48 MJ/kg = 48,000 MJ
    assert pytest.approx(res["fuel_energy_mj"], rel=1e-5) == 48000.0


def test_alternative_fuel_mass_equivalence():
    """Verify that fuel mass scales inversely with LHV for energy equivalence."""
    engine = FleetEmissionsEngine()
    baseline_vlsfo_kg = 10000.0  # 10 tonnes VLSFO (LHV = 40.2 MJ/kg -> 402,000 MJ)

    # Methanol (LHV = 19.9 MJ/kg) -> requires ~2.02x mass
    meoh_mass = engine.convert_fuel_mass_for_pathway(baseline_vlsfo_kg, "bio_methanol")
    assert meoh_mass > baseline_vlsfo_kg
    assert pytest.approx(meoh_mass, rel=1e-2) == 10000.0 * (40.2 / 19.9)

    # Liquid Hydrogen (LHV = 120.0 MJ/kg) -> requires ~0.335x mass
    lh2_mass = engine.convert_fuel_mass_for_pathway(baseline_vlsfo_kg, "liquid_hydrogen")
    assert lh2_mass < baseline_vlsfo_kg
    assert pytest.approx(lh2_mass, rel=1e-2) == 10000.0 * (40.2 / 120.0)


def test_well_to_wake_emission_components():
    """Verify that WtW equals WtT + TtW."""
    engine = FleetEmissionsEngine()
    emis = engine.compute_leg_emissions(fuel_mass_kg=5000.0, fuel_type="vlsfo")

    assert emis["wtw_total_tonnes_co2e"] > 0.0
    assert emis["wtt_tonnes_co2e"] > 0.0
    assert emis["ttw_co2_tonnes"] > 0.0
    assert pytest.approx(emis["wtw_total_tonnes_co2e"], rel=1e-4) == (
        emis["wtt_tonnes_co2e"] + emis["ttw_total_tonnes_co2e"]
    )
