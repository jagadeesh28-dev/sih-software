"""
Test Suite: Phase 2.1 Evidence Hardening and Methodological Integrity.
Verifies:
1. Leave-vessel-out validation isolation.
2. Held-out vessel never used in model selection or alpha tuning.
3. Multi-seed QPSO reproducibility and seed determinism.
4. Equal evaluation budget enforcement between QPSO and Random Search.
5. Statistical comparison correctness (Wilcoxon signed-rank and Cohen's d).
6. Synthetic target dependency audit completeness.
7. Prediction interval empirical coverage confidence interval calculation (Wilson score).
8. Actual Git commit hash capture (no fallback string).
"""

import os
from pathlib import Path
import re
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from common.reproducibility import get_git_commit
from data.splitting import LeakageSafeSplitter
from prediction.evaluate import compute_coverage_confidence_interval, evaluate_quantiles
from prediction.ml_baseline import CONFIG_A_FEATURES, PureMLPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.qpso_model_selection import (
    HyperparameterSearchSpace,
    QPSOModelSelector,
    RandomSearchModelSelector,
)
from prediction.residual_model import HybridResidualPredictor


@pytest.fixture
def clean_synthetic_data():
    pkg_root = Path(__file__).resolve().parent.parent
    data_path = pkg_root / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    df_raw = pd.read_csv(data_path)
    clean_mask = (
        df_raw["fuel_mass_flow_kg_h"].notna() &
        (df_raw["fuel_mass_flow_kg_h"] > 0) &
        df_raw["shaft_power_kw"].notna() &
        (df_raw["shaft_power_kw"] >= 0) &
        df_raw["stw_kn"].notna() &
        (df_raw["stw_kn"] > 0) &
        df_raw["sog_kn"].notna() &
        (df_raw["sog_kn"] > 0) &
        (df_raw["latitude"] >= -90) & (df_raw["latitude"] <= 90) &
        (df_raw["longitude"] >= -180) & (df_raw["longitude"] <= 180)
    )
    return df_raw[clean_mask].drop_duplicates().copy()


def test_leave_vessel_out_validation_isolation(clean_synthetic_data):
    """
    Test 1: In leave-vessel-out evaluation, remaining vessels are partitioned into
    distinct train and validation sets, with zero overlap with the held-out test set.
    """
    df = clean_synthetic_data
    splitter = LeakageSafeSplitter()
    holdout = "VESSEL_FE_01"

    train_lvo, test_lvo = splitter.leave_vessel_out_split(df, holdout_vessel_id=holdout)
    n_lvo = len(train_lvo)
    t_cut = int(n_lvo * 0.80)
    tr_sub = train_lvo.iloc[:t_cut]
    val_sub = train_lvo.iloc[t_cut:]

    # Zero overlap between train, validation, and held-out test
    tr_idx = set(tr_sub.index)
    val_idx = set(val_sub.index)
    test_idx = set(test_lvo.index)

    assert len(tr_idx.intersection(val_idx)) == 0, "Train and validation indices must be disjoint."
    assert len(tr_idx.intersection(test_idx)) == 0, "Train and test indices must be disjoint."
    assert len(val_idx.intersection(test_idx)) == 0, "Validation and test indices must be disjoint."

    # Test vessel identity isolation
    assert (test_lvo["vessel_id"] == holdout).all()
    assert (tr_sub["vessel_id"] != holdout).all()
    assert (val_sub["vessel_id"] != holdout).all()


def test_held_out_vessel_never_used_in_model_selection(clean_synthetic_data):
    """
    Test 2: Model selection (alpha tuning) executes strictly on validation data
    from training vessels; the held-out vessel is never passed to tuning.
    """
    df = clean_synthetic_data
    splitter = LeakageSafeSplitter()
    holdout = "VESSEL_FE_02"

    train_lvo, test_lvo = splitter.leave_vessel_out_split(df, holdout_vessel_id=holdout)
    t_cut = int(len(train_lvo) * 0.80)
    tr_sub = train_lvo.iloc[:t_cut]
    val_sub = train_lvo.iloc[t_cut:]

    phys = PhysicsFuelPredictor()
    model = HybridResidualPredictor(physics_predictor=phys, feature_cols=CONFIG_A_FEATURES, seed=42)

    # Fit with alpha tuning on val_sub
    model.fit(train_df=tr_sub, val_df=val_sub, tune_alpha=True, candidate_alphas=[0.0, 0.5, 1.0])

    meta = model.training_metadata
    assert meta["training_rows"] == len(tr_sub)
    assert meta["validation_rows"] == len(val_sub)
    assert holdout not in tr_sub["vessel_id"].values
    assert holdout not in val_sub["vessel_id"].values


def test_multiseed_qpso_reproducibility(clean_synthetic_data):
    """
    Test 3: QPSO produces bitwise identical results when executed with the same random seed.
    """
    df = clean_synthetic_data
    splitter = LeakageSafeSplitter()
    tr, val, _ = splitter.temporal_split(df)

    opt1 = QPSOModelSelector(n_particles=4, max_iterations=3, seed=123)
    res1 = opt1.search(train_df=tr, val_df=val, feature_cols=CONFIG_A_FEATURES)

    opt2 = QPSOModelSelector(n_particles=4, max_iterations=3, seed=123)
    res2 = opt2.search(train_df=tr, val_df=val, feature_cols=CONFIG_A_FEATURES)

    assert np.isclose(res1["best_validation_mae"], res2["best_validation_mae"], atol=1e-6)
    assert res1["best_params"] == res2["best_params"]
    assert np.allclose(res1["best_vector"], res2["best_vector"], atol=1e-6)


def test_equal_qpso_and_random_search_budgets(clean_synthetic_data):
    """
    Test 4: QPSO and Random Search enforce identical evaluation budgets.
    """
    df = clean_synthetic_data
    splitter = LeakageSafeSplitter()
    tr, val, _ = splitter.temporal_split(df)

    budget = 16  # 4 particles * 4 iterations = 16
    qpso = QPSOModelSelector(n_particles=4, max_iterations=4, seed=42)
    qpso_res = qpso.search(train_df=tr, val_df=val, feature_cols=CONFIG_A_FEATURES)

    rs = RandomSearchModelSelector(total_budget=budget, seed=42)
    rs_res = rs.search(train_df=tr, val_df=val, feature_cols=CONFIG_A_FEATURES)

    assert qpso_res["evaluations"] == budget
    assert rs_res["evaluations"] == budget


def test_statistical_comparison_correctness():
    """
    Test 5: Paired difference, Wilcoxon signed-rank test, and effect size formulas operate correctly.
    """
    # Create controlled paired samples where QPSO is lower
    qpso_scores = np.array([20.0, 21.0, 19.5, 20.5, 22.0, 19.0, 20.2, 21.5, 20.8, 19.9])
    rs_scores   = np.array([22.0, 22.5, 21.0, 22.0, 23.5, 21.0, 21.8, 22.8, 22.2, 21.5])

    diffs = qpso_scores - rs_scores
    assert (diffs < 0).all(), "All paired differences should be negative (QPSO lower error)."

    stat, p_val = stats.wilcoxon(diffs, alternative="two-sided")
    assert p_val < 0.05, "Consistent paired improvement should achieve statistical significance."

    cohens_d = float(np.mean(diffs) / np.std(diffs, ddof=1))
    assert cohens_d < -1.0, "Effect size should indicate large magnitude improvement."


def test_synthetic_target_dependency_audit():
    """
    Test 6: Synthetic target dependency documentation exists and details required channels.
    """
    pkg_root = Path(__file__).resolve().parent.parent
    audit_file = pkg_root / "results" / "experiments" / "synthetic_target_dependency.md"

    assert audit_file.exists(), f"Missing audit file: {audit_file}"
    content = audit_file.read_text(encoding="utf-8")

    required_keywords = [
        "shaft_power_kw",
        "stw_kn",
        "engine_load_pct",
        "SFC",
        "P_phys_ref",
        "instantaneous operational estimation",
    ]
    for kw in required_keywords:
        assert kw in content, f"Audit document missing keyword: {kw}"


def test_prediction_interval_coverage_ci_calculation():
    """
    Test 7: Wilson score confidence interval calculation for empirical coverage proportion.
    """
    # Evaluate 156 covered out of 179 observations (87.15%)
    ci_low, ci_high = compute_coverage_confidence_interval(k_covered=156, n_total=179, confidence_level=0.95)

    assert 80.0 <= ci_low <= 84.0, f"Expected Wilson lower bound around 81.4%, got {ci_low}%"
    assert 90.0 <= ci_high <= 93.0, f"Expected Wilson upper bound around 91.3%, got {ci_high}%"
    assert ci_low < 87.15 < ci_high, "Point estimate must lie strictly within the 95% confidence interval."

    # Test edge cases
    assert compute_coverage_confidence_interval(0, 0) == (0.0, 0.0)
    assert compute_coverage_confidence_interval(100, 100)[0] > 95.0


def test_actual_git_hash_capture():
    """
    Test 8: System captures real 40-character Git SHA-1 hash rather than fallback string.
    """
    git_hash = get_git_commit()
    assert git_hash is not None
    assert git_hash != "UNKNOWN_NON_GIT_WORKSPACE", "Git hash should not be the unknown fallback."
    assert len(git_hash) == 40, f"Git SHA-1 commit hash must be 40 characters long, got '{git_hash}'"
    assert re.match(r"^[0-9a-f]{40}$", git_hash), "Git hash must be valid hexadecimal."
