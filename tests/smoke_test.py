"""
Phase 0 Smoke Test Runner.
Executes lightweight checks on config loading, physics calculations, LCA conversions,
and problem evaluations to verify platform integrity without executing full heavy benchmarks.
"""

import sys
from pathlib import Path

# Add project root to sys.path
pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from common.logger import setup_logger
from common.config_loader import load_config
from common.reproducibility import audit_environment, set_seed
from physics.resistance_model import VesselResistanceModel
from lca.fuel_registry import FuelPathwayRegistry
from lca.well_to_wake import calculate_well_to_wake
from optimization.problem import MaritimeFleetProblem

logger = setup_logger("smoke_test")


def run_smoke_test() -> int:
    logger.info("=== STARTING SIH26138 PHASE 0 SMOKE TEST ===")

    # 1. Config Loader Check
    try:
        physics_cfg = load_config("physics.yaml")
        fuels_cfg = load_config("fuels.yaml")
        opt_cfg = load_config("optimization.yaml")
        scen_cfg = load_config("scenarios.yaml")
        bench_cfg = load_config("benchmark.yaml")
        claims_cfg = load_config("claims.yaml")
        logger.info(f"Configurations loaded successfully: {len(claims_cfg.get('claims', []))} claims registered.")
    except Exception as e:
        logger.error(f"Config loading check failed: {e}")
        return 1

    # 2. Environment Audit Check
    try:
        env = audit_environment()
        logger.info(f"Environment audited: Python {env['python_version'].split()[0]} on {env['platform']}")
        logger.info(f"Key packages verified: NumPy {env['packages'].get('numpy')}, SciPy {env['packages'].get('scipy')}, PyMoo {env['packages'].get('pymoo')}")
    except Exception as e:
        logger.error(f"Environment audit check failed: {e}")
        return 1

    # 3. Physics Model Smoke Check
    try:
        vessel_model = VesselResistanceModel("container_feeder")
        res = vessel_model.compute_total_resistance(speed_knots=15.0, wave_height_m=1.0)
        logger.info(f"Physics smoke check: Total Resistance = {res['r_total_newtons']:.1f} N, Power = {res['power']['pb_kw']:.1f} kW, Fuel Rate = {res['fuel']['total_fuel_kg_h']:.1f} kg/h")
        assert res["r_total_newtons"] > 0
    except Exception as e:
        logger.error(f"Physics smoke check failed: {e}")
        return 1

    # 4. LCA Well-to-Wake Smoke Check
    try:
        registry = FuelPathwayRegistry()
        vlsfo_res = calculate_well_to_wake(1000.0, "vlsfo", registry)
        lng_res = calculate_well_to_wake(1000.0, "fossil_lng", registry)
        logger.info(f"LCA smoke check: VLSFO WtW = {vlsfo_res['wtw_total_tonnes_co2e']:.2f} tCO2e, LNG WtW = {lng_res['wtw_total_tonnes_co2e']:.2f} tCO2e")
        assert vlsfo_res["wtw_total_tonnes_co2e"] > 0
    except Exception as e:
        logger.error(f"LCA smoke check failed: {e}")
        return 1

    # 5. Optimization Problem Smoke Check
    try:
        set_seed(42)
        prob = MaritimeFleetProblem(vessel_ids=["Vessel_A", "Vessel_B"])
        sample_x = (prob.xl + prob.xu) / 2.0
        out = {}
        prob._evaluate(sample_x, out)
        logger.info(f"Fleet optimization smoke check: Objectives = {out['F']}, Constraint = {out['G']}")
        assert len(out["F"]) == 3
    except Exception as e:
        logger.error(f"Optimization problem smoke check failed: {e}")
        return 1

    logger.info("=== PHASE 0 SMOKE TEST PASSED SUCCESSFULLY ===")
    return 0


if __name__ == "__main__":
    code = run_smoke_test()
    sys.exit(code)
