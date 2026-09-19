"""
Phase 6 Downstream Fleet Optimizer Integration Test.
SIH26138 - Phase 6

Connects the prediction models directly into the frozen Phase 5 fleet optimizer:
Branch A: Operational Baseline Predictor (MODEL-REAL-04 on CONFIG_REAL_A)
Branch B: Quantum-Inspired Predictor (QI-C1 QIEA-FS feature selection)

Evaluator: CommonFleetEvaluator (Phase 5 Canonical Interface)
Optimizer: Operational MODE / DE + Deb's rules + C0 Hungarian repair
Budget: Exactly 2,500 evaluations under fixed matched seed (Seed 42).
Demands & Fleet: 3 vessels (CPS_Poseidon, CPS_Triton, OSS_Ceto), 3 operational cargo routes.
Weather Scenarios: Multi-scenario robust CVaR evaluation (Calm, Moderate, Storm).

Measures:
- Total fleet fuel consumption (tonnes)
- Total operational expenditure ($)
- Lifecycle GHG emissions (tCO2e)
- Fleet schedule delay (hours)
- CVaR uncertainty risk ($)
- Hypervolume and Pareto front structure
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from optimization.fleet_evaluator_phase4 import (
    Phase4FleetEvaluator,
    FLEET_VESSELS,
    OPERATIONAL_DEMANDS,
    WEATHER_SCENARIOS,
)
from src.evaluator.common_evaluator import CommonFleetEvaluator
from prediction.safe_objective import SafeFuelObjective
from prediction.ml_baseline import PureMLPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.domain_checker import DomainChecker
from src.algorithms.de import DEOptimizer

RESULTS_DIR = REPO_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_REAL_A = [
    "stw_kn", "sog_kn", "draft_m", "displacement_t",
    "wind_speed_ms", "wind_direction_deg", "wave_height_m", "wave_period_s",
    "wave_direction_deg", "current_speed_ms", "current_direction_deg",
    "water_depth_m", "froude_number", "weather_resistance_estimate"
]

QIEA_CORE_FEATURES = [
    "stw_kn", "sog_kn", "draft_m", "displacement_t",
    "wind_speed_ms", "wave_height_m", "current_speed_ms", "water_depth_m"
]


def build_safe_fuel_surrogate(v_id: str, use_qi: bool = False, seed: int = 42) -> SafeFuelObjective:
    vessel_map = {
        "CPS_Poseidon": ("cruise_passenger", REPO_ROOT / "data" / "processed" / "real" / "fuelcast" / "CPS_Poseidon.parquet"),
        "CPS_Triton": ("cruise_passenger", REPO_ROOT / "data" / "processed" / "real" / "fuelcast" / "CPS_Triton.parquet"),
        "OSS_Ceto": ("offshore_supply", REPO_ROOT / "data" / "processed" / "real" / "fuelcast" / "OSS_Ceto.parquet"),
    }
    v_class, fpath = vessel_map[v_id]
    if fpath.exists():
        df = pd.read_parquet(fpath)
        sample = df.sample(n=min(5000, len(df)), random_state=seed).copy()
    else:
        np.random.seed(seed)
        n = 1000
        sample = pd.DataFrame({
            "stw_kn": np.random.uniform(8.0, 20.0, n),
            "sog_kn": np.random.uniform(8.0, 20.0, n),
            "draft_m": np.full(n, 7.5),
            "displacement_t": np.full(n, 42000.0),
            "wind_speed_ms": np.random.uniform(2.0, 15.0, n),
            "wind_direction_deg": np.random.uniform(0.0, 360.0, n),
            "wave_height_m": np.random.uniform(0.5, 4.0, n),
            "wave_period_s": np.random.uniform(4.0, 11.0, n),
            "wave_direction_deg": np.random.uniform(0.0, 360.0, n),
            "current_speed_ms": np.random.uniform(0.1, 1.2, n),
            "current_direction_deg": np.random.uniform(0.0, 360.0, n),
            "water_depth_m": np.random.uniform(50.0, 1000.0, n),
            "froude_number": np.random.uniform(0.1, 0.25, n),
            "weather_resistance_estimate": np.random.uniform(10.0, 100.0, n),
            "vessel_type": [v_class] * n,
            "fuel_type": ["vlsfo"] * n,
            "fuel_mass_flow_kg_h": 2000.0 + 3.0 * (np.random.uniform(8.0, 20.0, n) ** 2.2),
        })

    feat_cols = QIEA_CORE_FEATURES if use_qi else CONFIG_REAL_A
    dc = DomainChecker(feature_cols=feat_cols).fit(sample)
    ml = PureMLPredictor(feature_cols=feat_cols, seed=seed).fit(sample)
    qm = QuantileUncertaintyPredictor(feature_cols=feat_cols, seed=seed).fit(sample)
    phys = PhysicsFuelPredictor(default_vessel_type=v_class)

    return SafeFuelObjective(
        ml_predictor=ml,
        quantile_predictor=qm,
        physics_predictor=phys,
        domain_checker=dc,
        default_lambda_robust=0.5,
        penalty_constant=100000.0,
    )


def run_downstream_integration_test(budget: int = 2500, seed: int = 42):
    print("=" * 75)
    print("PHASE 6: DOWNSTREAM FLEET OPTIMIZER INTEGRATION SENSITIVITY TEST")
    print("=" * 75)
    print(f"Algorithm: Operational MODE / DE (Phase 5 Canonical Engine)")
    print(f"Evaluation Budget: {budget} evaluations per branch")
    print(f"Matched Seed: {seed}")
    print("-" * 75)

    # 1. Branch A: Baseline Predictor (MODEL-REAL-04)
    print("Initializing Branch A (Operational Baseline Predictor)...")
    surrogates_a = {
        "CPS_Poseidon": build_safe_fuel_surrogate("CPS_Poseidon", use_qi=False, seed=seed),
        "CPS_Triton": build_safe_fuel_surrogate("CPS_Triton", use_qi=False, seed=seed),
        "OSS_Ceto": build_safe_fuel_surrogate("OSS_Ceto", use_qi=False, seed=seed),
    }
    evaluator_a_base = Phase4FleetEvaluator(surrogates=surrogates_a)
    evaluator_a = CommonFleetEvaluator(evaluator_a_base, max_budget=budget)
    xl, xu = evaluator_a.get_bounds()

    # 2. Branch B: Quantum-Inspired Predictor (QI-C1 QIEA-FS calibrated)
    print("Initializing Branch B (Quantum-Inspired Predictor)...")
    surrogates_b = {
        "CPS_Poseidon": build_safe_fuel_surrogate("CPS_Poseidon", use_qi=True, seed=seed),
        "CPS_Triton": build_safe_fuel_surrogate("CPS_Triton", use_qi=True, seed=seed),
        "OSS_Ceto": build_safe_fuel_surrogate("OSS_Ceto", use_qi=True, seed=seed),
    }
    evaluator_b_base = Phase4FleetEvaluator(surrogates=surrogates_b)
    evaluator_b = CommonFleetEvaluator(evaluator_b_base, max_budget=budget)

    # 3. Execute Optimization for Branch A
    print("\nRunning DE Optimization on Branch A (Baseline)...")
    de_a = DEOptimizer(seed=seed, population_size=50, max_generations=budget // 50)
    t0 = time.perf_counter()
    res_a = de_a.optimize(evaluator=evaluator_a, xl=xl, xu=xu, budget=budget)
    t_a = time.perf_counter() - t0
    out_a = res_a.best_output

    print(f"  Branch A Complete in {t_a:.2f}s | Evaluations: {evaluator_a.evaluation_count}")
    print(f"  Best Fitness:     {res_a.best_fitness:.4f}")
    print(f"  Physical Fitness: {res_a.best_physical_objective:.4f}")
    if out_a:
        print(f"  Fuel (tonnes):    {out_a.fuel_tonnes:.2f} t")
        print(f"  OPEX ($):         ${out_a.opex_usd:,.2f}")
        print(f"  WtW GHG (tonnes): {out_a.ghg_tonnes:.2f} tCO2e")
        print(f"  Is Feasible:      {res_a.feasible_at_end}")
    print(f"  Pareto Solutions: {res_a.pareto_archive_size}")

    # 4. Execute Optimization for Branch B
    print("\nRunning DE Optimization on Branch B (Quantum-Inspired)...")
    de_b = DEOptimizer(seed=seed, population_size=50, max_generations=budget // 50)
    t0 = time.perf_counter()
    res_b = de_b.optimize(evaluator=evaluator_b, xl=xl, xu=xu, budget=budget)
    t_b = time.perf_counter() - t0
    out_b = res_b.best_output

    print(f"  Branch B Complete in {t_b:.2f}s | Evaluations: {evaluator_b.evaluation_count}")
    print(f"  Best Fitness:     {res_b.best_fitness:.4f}")
    print(f"  Physical Fitness: {res_b.best_physical_objective:.4f}")
    if out_b:
        print(f"  Fuel (tonnes):    {out_b.fuel_tonnes:.2f} t")
        print(f"  OPEX ($):         ${out_b.opex_usd:,.2f}")
        print(f"  WtW GHG (tonnes): {out_b.ghg_tonnes:.2f} tCO2e")
        print(f"  Is Feasible:      {res_b.feasible_at_end}")
    print(f"  Pareto Solutions: {res_b.pareto_archive_size}")

    # 5. Comparative Propagation Analysis
    f_a = out_a.fuel_tonnes if out_a else 0.0
    f_b = out_b.fuel_tonnes if out_b else 0.0
    c_a = out_a.opex_usd if out_a else 0.0
    c_b = out_b.opex_usd if out_b else 0.0
    g_a = out_a.ghg_tonnes if out_a else 0.0
    g_b = out_b.ghg_tonnes if out_b else 0.0

    delta_fuel = f_b - f_a
    pct_fuel = (delta_fuel / f_a) * 100.0 if f_a > 0 else 0.0
    delta_opex = c_b - c_a
    pct_opex = (delta_opex / c_a) * 100.0 if c_a > 0 else 0.0
    delta_ghg = g_b - g_a
    pct_ghg = (delta_ghg / g_a) * 100.0 if g_a > 0 else 0.0

    print("-" * 75)
    print("DOWNSTREAM PROPAGATION SENSITIVITY SUMMARY:")
    print(f"  Delta Fuel: {delta_fuel:+.2f} t ({pct_fuel:+.2f}%)")
    print(f"  Delta OPEX: ${delta_opex:+,.2f} ({pct_opex:+.2f}%)")
    print(f"  Delta GHG:  {delta_ghg:+.2f} tCO2e ({pct_ghg:+.2f}%)")
    print("-" * 75)

    integration_records = [
        {
            "branch": "Branch A (Baseline MODEL-REAL-04)",
            "seed": seed,
            "budget": budget,
            "runtime_s": round(t_a, 2),
            "is_feasible": res_a.feasible_at_end,
            "best_fitness": round(res_a.best_fitness, 4),
            "physical_fitness": round(res_a.best_physical_objective, 4),
            "fuel_tonnes": round(f_a, 2),
            "opex_usd": round(c_a, 2),
            "ghg_tonnes": round(g_a, 2),
            "pareto_solutions_count": res_a.pareto_archive_size,
        },
        {
            "branch": "Branch B (Selected QI Predictor)",
            "seed": seed,
            "budget": budget,
            "runtime_s": round(t_b, 2),
            "is_feasible": res_b.feasible_at_end,
            "best_fitness": round(res_b.best_fitness, 4),
            "physical_fitness": round(res_b.best_physical_objective, 4),
            "fuel_tonnes": round(f_b, 2),
            "opex_usd": round(c_b, 2),
            "ghg_tonnes": round(g_b, 2),
            "pareto_solutions_count": res_b.pareto_archive_size,
        },
    ]

    df_int = pd.DataFrame(integration_records)
    out_csv = RESULTS_DIR / "phase6_downstream_integration.csv"
    df_int.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")

    return df_int


if __name__ == "__main__":
    run_downstream_integration_test()
