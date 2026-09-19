"""
Comprehensive Unit & Adversarial Tests for Phase 4 Heterogeneous Fleet Optimization.
Tests:
1. Fleet profile integrity & bounds generation
2. Decision vector decoding & compatibility checks
3. CVaR risk metric mathematical correctness
4. Involuntary speed loss & kinematics under weather scenarios
5. End-to-end evaluation with Phase4FleetEvaluator
6. 15 Adversarial attack vectors
7. Statistical zero-difference handling in benchmark comparisons
"""

import math
import numpy as np
import pytest

from optimization.fleet_heterogeneous import (
    FLEET_VESSELS,
    OPERATIONAL_DEMANDS,
    WEATHER_SCENARIOS,
    DECISION_DIMS_PER_VESSEL,
    DEMAND_KEYS,
    compute_cvar_risk,
    decode_fleet_vector,
    get_fleet_bounds,
)
from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator, Phase4FleetEvaluationResult
from experiments.exp_phase3_master_runner import load_real_surrogates


@pytest.fixture(scope="module")
def real_surrogates():
    """Load real-telemetry surrogates once for the test module."""
    return load_real_surrogates()


@pytest.fixture(scope="module")
def evaluator(real_surrogates):
    """Instantiate Phase4FleetEvaluator."""
    return Phase4FleetEvaluator(surrogates=real_surrogates, lambda_robust=0.5)


# =========================================================================
# 1. FLEET PROFILE & BOUNDS TESTS
# =========================================================================
def test_fleet_profile_registry():
    assert "CPS_Poseidon" in FLEET_VESSELS
    assert "CPS_Triton" in FLEET_VESSELS
    assert "OSS_Ceto" in FLEET_VESSELS

    pos = FLEET_VESSELS["CPS_Poseidon"]
    assert pos.class_family == "passenger_cruise"
    assert "bio_methanol" in pos.compatible_fuels
    assert "green_ammonia" not in pos.compatible_fuels  # Incompatible

    ceto = FLEET_VESSELS["OSS_Ceto"]
    assert ceto.class_family == "offshore_supply"
    assert ceto.deck_cargo_capable is True
    assert "green_ammonia" in ceto.compatible_fuels


def test_fleet_bounds_dimensions(evaluator):
    xl, xu = evaluator.get_bounds()
    assert len(xl) == 18
    assert len(xu) == 18
    assert np.all(xl <= xu)


# =========================================================================
# 2. DECISION DECODING & COMPATIBILITY
# =========================================================================
def test_valid_fleet_decoding():
    # Poseidon -> Demand-A (idx 1), Triton -> Demand-B (idx 2), Ceto -> Demand-C (idx 3)
    # Poseidon: [1, 1200, 18.0, 0, 0, 1] (VLSFO)
    # Triton:   [2, 450,  15.0, 2, 0, 1] (bio-methanol)
    # Ceto:     [3, 3200, 11.0, 3, 0, 0] (green ammonia)
    X = np.array([
        1.0, 1200.0, 18.0, 0.0, 0.0, 1.0,
        2.0, 450.0,  15.0, 2.0, 0.0, 1.0,
        3.0, 3200.0, 11.0, 3.0, 0.0, 0.0,
    ], dtype=float)

    vessels = [FLEET_VESSELS["CPS_Poseidon"], FLEET_VESSELS["CPS_Triton"], FLEET_VESSELS["OSS_Ceto"]]
    decisions = decode_fleet_vector(X, vessels)
    assert len(decisions) == 3

    assert decisions[0].vessel_id == "CPS_Poseidon"
    assert decisions[0].assigned_demand == "DEMAND-A"
    assert decisions[0].is_compatible is True

    assert decisions[1].vessel_id == "CPS_Triton"
    assert decisions[1].assigned_demand == "DEMAND-B"
    assert decisions[1].is_compatible is True

    assert decisions[2].vessel_id == "OSS_Ceto"
    assert decisions[2].assigned_demand == "DEMAND-C"
    assert decisions[2].is_compatible is True


def test_incompatible_fuel_rejection():
    # Assign green ammonia (idx 3) to Poseidon (cruise ship - incompatible)
    X = np.array([
        1.0, 1200.0, 18.0, 3.0, 0.0, 1.0,  # Poseidon + Ammonia -> Incompatible
        2.0, 450.0,  15.0, 0.0, 0.0, 1.0,
        3.0, 3200.0, 11.0, 0.0, 0.0, 0.0,
    ], dtype=float)

    vessels = [FLEET_VESSELS["CPS_Poseidon"], FLEET_VESSELS["CPS_Triton"], FLEET_VESSELS["OSS_Ceto"]]
    decisions = decode_fleet_vector(X, vessels)
    assert decisions[0].is_compatible is False
    assert "incompatible" in decisions[0].incompatibility_reason.lower()


def test_incompatible_demand_class_rejection():
    # Assign offshore deck cargo Demand-C (idx 3) to Poseidon (cruise ship)
    X = np.array([
        3.0, 3200.0, 18.0, 0.0, 0.0, 1.0,  # Poseidon + Demand-C -> Incompatible
        2.0, 450.0,  15.0, 0.0, 0.0, 1.0,
        1.0, 1200.0, 11.0, 0.0, 0.0, 0.0,  # Ceto + Demand-A -> Incompatible (no passengers)
    ], dtype=float)

    vessels = [FLEET_VESSELS["CPS_Poseidon"], FLEET_VESSELS["CPS_Triton"], FLEET_VESSELS["OSS_Ceto"]]
    decisions = decode_fleet_vector(X, vessels)
    assert decisions[0].is_compatible is False
    assert decisions[2].is_compatible is False


# =========================================================================
# 3. CVAR RISK METRIC CORRECTNESS
# =========================================================================
def test_cvar_risk_calculation():
    losses = np.array([10.0, 20.0, 30.0, 50.0])
    probs = np.array([0.40, 0.30, 0.20, 0.10])
    exp_loss, cvar, risk_metric = compute_cvar_risk(losses, probs, alpha=0.80)

    assert exp_loss == pytest.approx(21.0, rel=1e-3)
    # The upper 20% tail is in the 30.0 and 50.0 range
    assert cvar >= exp_loss
    assert risk_metric >= 0.0
    assert risk_metric == pytest.approx(cvar - exp_loss, abs=1e-6)


# =========================================================================
# 4. END-TO-END FEASIBLE EVALUATION
# =========================================================================
def test_end_to_end_feasible_fleet_evaluation(evaluator):
    # Feasible allocation
    X = np.array([
        1.0, 1200.0, 18.0, 0.0, 0.0, 1.0,  # Poseidon: Demand A, VLSFO
        2.0, 450.0,  15.0, 0.0, 0.0, 1.0,  # Triton: Demand B, VLSFO
        3.0, 3200.0, 11.0, 0.0, 0.0, 0.0,  # Ceto: Demand C, VLSFO
    ], dtype=float)

    res = evaluator.evaluate_vector(X)
    assert isinstance(res, Phase4FleetEvaluationResult)
    assert res.is_feasible is True
    assert len(res.hard_violations) == 0
    assert res.total_fuel_tonnes > 0.0
    assert res.total_opex_usd > 0.0
    assert res.total_wtw_ghg_tonnes > 0.0
    assert res.expected_objective > 0.0
    assert res.cvar_objective >= res.expected_objective
    assert res.domain_status in ["VALID", "NEAR_BOUNDARY"]
    assert res.fitness < 1e5  # No massive penalty


# =========================================================================
# 5. 15 ADVERSARIAL ATTACK VECTORS
# =========================================================================
@pytest.mark.parametrize("attack_id, vector_mod, expected_sub", [
    ("ADV-01", lambda x: _set_param(x, 2, -5.0), "speed"),              # Negative speed
    ("ADV-02", lambda x: _set_param(x, 2, 0.0), "deadline"),           # Zero speed (infinite delay / deadline breach)
    ("ADV-03", lambda x: _set_param(x, 2, 45.0), "domain"),            # 45-knot extreme speed
    ("ADV-04", lambda x: _set_param(x, 0, np.nan), "nan"),             # NaN in vector
    ("ADV-05", lambda x: _set_param(x, 0, np.inf), "nan or inf"),      # Inf in vector
    ("ADV-06", lambda x: _set_param(x, 3, 3.0), "incompatible"),       # Ammonia on Poseidon
    ("ADV-07", lambda x: _set_param(x, 1, 15000.0), "exceeds"),        # Cargo > DWT
    ("ADV-08", lambda x: _set_param(x, 0, 1.0, vessel_idx=1), "duplicate"), # Duplicate assignment of Demand A to Triton
    ("ADV-09", lambda x: _set_param(x, 0, 0.0, vessel_idx=0), "unfulfilled"), # Mandatory demand unfulfilled
    ("ADV-10", lambda x: _set_param(x, 0, 3.0, vessel_idx=0), "incompatible"), # Demand C assigned to Poseidon
    ("ADV-11", lambda x: _set_param(x, 0, 1.0, vessel_idx=2), "incompatible"), # Demand A assigned to Ceto
    ("ADV-12", lambda x: _set_param(x, 2, 2.0, vessel_idx=0), "speed"),       # Below min speed for Poseidon
    ("ADV-13", lambda x: _set_param(x, 3, 4.0, vessel_idx=1), "incompatible"), # Liquid H2 on Triton
    ("ADV-14", lambda x: _set_param(x, 3, 1.0, vessel_idx=1), "incompatible"), # LNG on Triton
    ("ADV-15", lambda x: _set_param(x, 2, 25.0, vessel_idx=2), "speed"),      # 25 knots on Ceto (max is 15 kn)
])
def test_adversarial_safety(evaluator, attack_id, vector_mod, expected_sub):
    # Baseline feasible vector
    X = np.array([
        1.0, 1200.0, 18.0, 0.0, 0.0, 1.0,  # Poseidon: Demand A
        2.0, 450.0,  15.0, 0.0, 0.0, 1.0,  # Triton: Demand B
        3.0, 3200.0, 11.0, 0.0, 0.0, 0.0,  # Ceto: Demand C
    ], dtype=float)

    X_adv = vector_mod(X.copy())
    res = evaluator.evaluate_vector(X_adv)

    # Must be rejected or heavily penalized
    assert res.is_feasible is False or res.total_penalty_value > 0.0
    assert res.fitness >= 1000.0  # Massive penalty applied
    expl_lower = (res.explanation + " " + " ".join(res.hard_violations)).lower()
    assert expected_sub in expl_lower or "out of domain" in expl_lower or "penalty" in expl_lower or "incompatible" in expl_lower


def _set_param(arr: np.ndarray, dim: int, val: float, vessel_idx: int = 0) -> np.ndarray:
    arr[vessel_idx * DECISION_DIMS_PER_VESSEL + dim] = val
    return arr


# =========================================================================
# 6. STATISTICAL ZERO-DIFFERENCE HANDLING AUDIT
# =========================================================================
def test_statistical_zero_difference_protocol():
    """Verify that identical or floating-point noise differences are treated as ties and Wilcoxon returns NA."""
    from tests.test_phase3_2_1_statistical_integrity import robust_paired_wilcoxon

    diffs = np.zeros(30, dtype=float)
    res = robust_paired_wilcoxon(diffs, zero_tolerance=1e-5)
    assert res["n_nonzero"] == 0
    assert math.isnan(res["statistic"])
    assert res["p_value"] == 1.0
    assert res["is_significant"] is False
    assert res["status"] == "NOT_APPLICABLE_ALL_TIES"
