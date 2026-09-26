"""
Symmetric berth accounting (optimization/berth_model.py).

Shore power ON  -> grid electricity cost + grid GHG, no berth fuel.
Shore power OFF -> onboard generation: berth fuel, its fuel/ETS cost and WtW GHG, no electricity.
Expected values are computed from the authoritative engines, never hard-coded.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from optimization.berth_model import (DEFAULT_PORT_HOURS, SFOC_KG_VLSFO_PER_KWH, berth_accounting,
                                      grid_emission_factor_g_per_kwh)
from optimization.fleet_heterogeneous import FLEET_VESSELS
from optimization.sih_objective_engine import SIHObjectiveEngine

ENGINE = SIHObjectiveEngine()
GRID = ENGINE.shore_power_grid_emission_factor


def berth(vessel_id, fuel, shore, hours=DEFAULT_PORT_HOURS):
    return berth_accounting(FLEET_VESSELS[vessel_id].hotel_load_kw, hours, fuel, shore,
                            ENGINE.emissions_engine, ENGINE.cost_engine, GRID)


def test_grid_factor_comes_from_configuration():
    assert grid_emission_factor_g_per_kwh() == GRID == ENGINE.fuels_config["shore_power"]["grid_emission_factor_g_co2e_kwh"]


def test_poseidon_vlsfo_paths_are_mutually_exclusive():
    on, off = berth("CPS_Poseidon", "vlsfo", True), berth("CPS_Poseidon", "vlsfo", False)
    assert on.energy_kwh == off.energy_kwh == 6500 * 2.0 == 13000
    # ON: electricity only
    assert on.electricity_cost_usd == pytest.approx(13000 * ENGINE.shore_power_tariff + ENGINE.shore_power_connect_fee)
    assert on.grid_ghg_t == pytest.approx(13000 * GRID / 1e6)
    assert on.fuel_kg == on.fuel_cost_usd == on.carbon_cost_usd == on.fuel_wtw_ghg_t == 0.0
    # OFF: onboard fuel only, costed/emitted by the same engines as voyage fuel
    kg = ENGINE.emissions_engine.convert_fuel_mass_for_pathway(baseline_vlsfo_kg=13000 * SFOC_KG_VLSFO_PER_KWH,
                                                                target_fuel_type="vlsfo")
    em = ENGINE.emissions_engine.compute_leg_emissions(fuel_mass_kg=kg, fuel_type="vlsfo")
    assert off.fuel_kg == pytest.approx(kg) and kg == pytest.approx(2860.0)
    assert off.fuel_cost_usd == pytest.approx(kg / 1000 * ENGINE.bunker_prices["vlsfo"], abs=0.01)
    assert off.carbon_cost_usd == pytest.approx(em["ttw_co2_tonnes"] * ENGINE.cost_engine.carbon_price_usd_tonne, abs=0.01)
    assert off.fuel_wtw_ghg_t == pytest.approx(em["wtw_total_tonnes_co2e"])
    assert off.electricity_cost_usd == off.grid_ghg_t == 0.0


def test_poseidon_bio_methanol_shore_is_cheaper_when_engine_economics_say_so():
    on, off = berth("CPS_Poseidon", "bio_methanol", True), berth("CPS_Poseidon", "bio_methanol", False)
    kg = ENGINE.emissions_engine.convert_fuel_mass_for_pathway(baseline_vlsfo_kg=13000 * SFOC_KG_VLSFO_PER_KWH,
                                                                target_fuel_type="bio_methanol")
    assert off.fuel_kg == pytest.approx(kg) and kg > 13000 * SFOC_KG_VLSFO_PER_KWH  # lower LHV -> more mass
    assert (on.cost_usd < off.cost_usd) == (on.electricity_cost_usd < off.fuel_cost_usd + off.carbon_cost_usd)
    assert on.cost_usd < off.cost_usd  # consequence of the configured prices in fuels.yaml


def test_ceto_green_ammonia_ghg_relationship_differs_from_vlsfo():
    d_vlsfo = berth("OSS_Ceto", "vlsfo", True).ghg_t - berth("OSS_Ceto", "vlsfo", False).ghg_t
    d_nh3 = berth("OSS_Ceto", "green_ammonia", True).ghg_t - berth("OSS_Ceto", "green_ammonia", False).ghg_t
    assert d_vlsfo < 0.0 < d_nh3  # grid beats VLSFO generation; green NH3 generation beats the grid


@pytest.mark.parametrize("vessel_id", list(FLEET_VESSELS))
def test_sih_engine_consistency_invariant(vessel_id):
    v = FLEET_VESSELS[vessel_id]
    for fuel in [f for f in v.compatible_fuels if f in ENGINE.registry.pathways]:
        kw = dict(vessel_id=vessel_id, vessel_type=v.class_family, speed_knots=12.0, voyage_distance_nm=200.0,
                  schedule_deadline_hours=24.0, baseline_fuel_rate_kg_h=1500.0, fuel_type=fuel)
        voyage = ENGINE.evaluate_voyage(**kw)  # no berth time
        for shore in (True, False):
            r = ENGINE.evaluate_voyage(**kw, use_shore_power=shore, port_hours=4.0, hotel_load_kw=v.hotel_load_kw)
            b = berth(vessel_id, fuel, shore, hours=4.0)
            assert r.operational_cost_usd == pytest.approx(voyage.operational_cost_usd + b.cost_usd, abs=0.02)
            assert r.lifecycle_ghg_tonnes == pytest.approx(voyage.lifecycle_ghg_tonnes + b.ghg_t, abs=1e-3)
            assert r.fuel_tonnes == pytest.approx(voyage.fuel_tonnes + b.fuel_kg / 1000.0, abs=1e-3)
            assert r.shore_power_cost_usd == pytest.approx(b.electricity_cost_usd if shore else 0.0, abs=0.01)
            assert r.berth_source == ("SHORE POWER" if shore else "ONBOARD GENERATION")


FRONT = Path(__file__).resolve().parents[1] / "results" / "pareto_front.csv"


@pytest.fixture(scope="module")
def fleet_evaluator():
    from experiments.exp_phase3_master_runner import load_real_surrogates
    from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
    ev = Phase4FleetEvaluator(surrogates=load_real_surrogates())
    ev.weights = np.array([0.35, 0.35, 0.30, 0.0, 0.0])
    return ev


def test_fleet_evaluator_berth_semantics_match_sih_engine(fleet_evaluator):
    import pandas as pd
    x = np.asarray(json.loads(pd.read_csv(FRONT).iloc[0]["x_vector"]), dtype=float)
    for i, vid in enumerate(["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]):
        on, off = x.copy(), x.copy()
        on[i * 6 + 5], off[i * 6 + 5] = 1.0, 0.0
        r_on, r_off = fleet_evaluator.evaluate_vector(on), fleet_evaluator.evaluate_vector(off)
        fuel = r_on.fuel_decisions[vid]
        args = (FLEET_VESSELS[vid].hotel_load_kw, fleet_evaluator.port_hours, fuel)
        engines = (fleet_evaluator.emissions_engine, fleet_evaluator.cost_engine, fleet_evaluator.grid_factor_g_per_kwh)
        b_on, b_off = berth_accounting(*args, True, *engines), berth_accounting(*args, False, *engines)
        # berth terms are scenario-independent, so the probability-weighted difference is exactly ON - OFF
        assert r_on.total_opex_usd - r_off.total_opex_usd == pytest.approx(b_on.cost_usd - b_off.cost_usd, abs=0.05)
        assert r_on.total_wtw_ghg_tonnes - r_off.total_wtw_ghg_tonnes == pytest.approx(b_on.ghg_t - b_off.ghg_t, abs=0.02)
        assert r_on.total_fuel_tonnes - r_off.total_fuel_tonnes == pytest.approx(-b_off.fuel_kg / 1000.0, abs=0.02)
