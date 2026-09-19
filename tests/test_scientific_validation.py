"""
Unit and Integration Tests for Scientific Validation Gate.
Section 13, 14, 15, 18:
Validates independent physics reference formulas, fuel LCA audit, and QPSO benchmark functions.
"""

import sys
from pathlib import Path
import pytest
import numpy as np

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from scientific_validation.validation_gate import (
    run_independent_physics_hand_checks,
    run_comprehensive_lca_audit,
    reproduce_phase0_smoke_test_values,
)
from scientific_validation.qpso_benchmark import benchmark_qpso_mathematical_functions


def test_independent_physics_hand_checks():
    """Verify that naval architecture power and fuel rate formulas match independent analytical hand-calculations."""
    res = run_independent_physics_hand_checks()
    assert res["physics_validation_status"] == "PASS"
    assert res["power_rel_diff_pct"] < 0.01  # Less than 0.01% difference
    assert res["fuel_rel_diff_pct"] < 0.01


def test_smoke_test_values_reproduction():
    """Verify exact reproduction of Phase 0 smoke test values within 0.1% tolerance."""
    repro = reproduce_phase0_smoke_test_values()
    assert repro["all_reproduced"] is True
    for metric, data in repro["comparison"].items():
        assert data["match"] is True, f"{metric} failed reproduction: rel_diff={data['rel_difference_pct']:.4f}%"


def test_comprehensive_lca_audit():
    """Verify LCA audit covers registered fuels (including certified MGO) and correctly accounts for methane slip."""
    df_lca = run_comprehensive_lca_audit()
    assert len(df_lca) >= 5
    fuels = set(df_lca["fuel_key"])
    expected_fuels = {"vlsfo", "mgo", "fossil_lng", "bio_methanol", "green_ammonia", "liquid_hydrogen"}
    assert fuels == expected_fuels

    # Methane slip check for LNG
    lng_row = df_lca[df_lca["fuel_key"] == "fossil_lng"].iloc[0]
    assert lng_row["methane_slip_fraction"] == 0.022
    assert lng_row["ttw_ch4_tonnes_co2e"] > 0.5  # 1000 kg * 0.022 * 29.8 = 0.6556 tCO2e

    # WtW = WtT + TtW check
    for _, row in df_lca.iterrows():
        calc_wtw = row["wtt_tonnes_co2e"] + row["ttw_total_tonnes_co2e"]
        assert row["wtw_total_tonnes_co2e"] == pytest.approx(calc_wtw, rel=1e-5)


def test_qpso_mathematical_benchmarks():
    """Verify QPSO objective reduction on Sphere, Rastrigin, and Rosenbrock benchmark functions."""
    res = benchmark_qpso_mathematical_functions(dim=3, n_particles=30, max_iterations=60, seed=42)
    assert res["status"] == "PASS"

    benchmarks = res["benchmarks"]
    for name in ["sphere", "rastrigin", "rosenbrock"]:
        b = benchmarks[name]
        assert b["within_bounds"] is True
        assert b["objective_reduced"] is True
        assert b["final_best_score"] < b["initial_score"]
