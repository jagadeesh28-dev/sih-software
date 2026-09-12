"""
Phase 2 Comprehensive Test Suite.
Section 24: 20 mandatory tests verifying scientific and methodological corrections:
1. STW is used by physics predictor.
2. SOG is not silently substituted for STW.
3. Current variables are preserved.
4. Physics predictor output validity and diagnostics.
5. ML baseline does not use unnecessary StandardScaler.
6. Residual construction strictly on TRAIN.
7. Alpha weighting discrete sweep in {0.0, 0.25, 0.50, 0.75, 1.00}.
8. Alpha bounds enforced in [0.0, 1.0].
9. No TEST leakage.
10. No VALIDATION leakage into TRAIN preprocessing.
11. QPSO equal evaluation budget to Random Search.
12. QPSO validation-only objective.
13. Random Search equal-budget reproducibility.
14. Quantile monotonic non-crossing (q05 <= q50 <= q95).
15. PICP correctness.
16. Pinball loss correctness.
17. Vessel-ID exclusion in cross-vessel CONFIG-A.
18. Chronological temporal split correctness.
19. Synthetic model-mismatch presence.
20. Reproducibility across seeds.
"""

import pytest
import numpy as np
import pandas as pd

from data.synthetic_generator import generate_synthetic_maritime_dataset
from data.splitting import LeakageSafeSplitter
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.ml_baseline import PureMLPredictor, CONFIG_A_FEATURES, CONFIG_B_FEATURES
from prediction.residual_model import HybridResidualPredictor
from prediction.qpso_model_selection import QPSOModelSelector, RandomSearchModelSelector, HyperparameterSearchSpace
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.evaluate import evaluate_predictions, evaluate_quantiles, calculate_picp, pinball_loss


@pytest.fixture
def sample_data():
    """Generates controlled synthetic maritime test data with model mismatch."""
    df = generate_synthetic_maritime_dataset(n_records=300, seed=42, inject_anomalies=False)
    return df


# -----------------------------------------------------------------------------
# 1. STW is used by physics predictor
# -----------------------------------------------------------------------------
def test_stw_is_used_by_physics_predictor(sample_data):
    predictor = PhysicsFuelPredictor()
    row = sample_data.iloc[0].to_dict()
    # Modify STW and ensure physics output changes monotonically
    row_low = dict(row, stw_kn=10.0)
    row_high = dict(row, stw_kn=16.0)

    out_low = predictor.predict_record(row_low)
    out_high = predictor.predict_record(row_high)

    assert out_high["predicted_fuel_kg_h"] > out_low["predicted_fuel_kg_h"]
    assert out_high["predicted_power_kw"] > out_low["predicted_power_kw"]
    assert out_low["physics_diagnostics"]["stw_kn"] == 10.0
    assert out_high["physics_diagnostics"]["stw_kn"] == 16.0


# -----------------------------------------------------------------------------
# 2. SOG is not silently substituted for STW
# -----------------------------------------------------------------------------
def test_sog_not_silently_substituted_for_stw(sample_data):
    predictor = PhysicsFuelPredictor()
    row = sample_data.iloc[0].to_dict()
    # Remove stw_kn entirely, leaving only sog_kn
    del row["stw_kn"]
    row["sog_kn"] = 15.0

    # Must raise ValueError rather than silently substituting SOG
    with pytest.raises(ValueError, match="Hydrodynamic physics pipeline requires Speed Through Water"):
        predictor.predict_record(row)


# -----------------------------------------------------------------------------
# 3. Current variables are preserved
# -----------------------------------------------------------------------------
def test_current_variables_preserved(sample_data):
    assert "current_speed_ms" in sample_data.columns
    assert "current_direction_deg" in sample_data.columns
    assert "sog_kn" in sample_data.columns
    assert "stw_kn" in sample_data.columns
    # Ensure SOG and STW are distinct columns with non-identical values
    assert not np.array_equal(sample_data["sog_kn"].values, sample_data["stw_kn"].values)


# -----------------------------------------------------------------------------
# 4. Physics predictor output validity and diagnostics
# -----------------------------------------------------------------------------
def test_physics_predictor_output_validity_and_diagnostics(sample_data):
    predictor = PhysicsFuelPredictor()
    record = sample_data.iloc[0].to_dict()
    out = predictor.predict_record(record)

    # Required contract fields
    assert "predicted_fuel_kg_h" in out
    assert "predicted_power_kw" in out
    assert "total_resistance_n" in out
    assert "resistance_components" in out
    assert "physics_diagnostics" in out

    res_comp = out["resistance_components"]
    assert res_comp["r_total_newtons"] > 0
    assert res_comp["r_calm_newtons"] > 0

    diag = out["physics_diagnostics"]
    assert diag["pe_kw"] > 0
    assert diag["pd_kw"] > 0
    assert diag["pb_kw"] > 0
    assert 0.0 < diag["eta_d"] < 1.0


# -----------------------------------------------------------------------------
# 5. ML baseline does not use unnecessary StandardScaler
# -----------------------------------------------------------------------------
def test_ml_baseline_no_standard_scaler(sample_data):
    model = PureMLPredictor(feature_cols=CONFIG_A_FEATURES)
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    model.fit(train_df, val_df)
    meta = model.training_metadata
    assert "feature_scaling" in meta
    assert "NONE" in meta["feature_scaling"]
    assert not hasattr(model, "scaler")


# -----------------------------------------------------------------------------
# 6. Residual construction strictly on TRAIN
# -----------------------------------------------------------------------------
def test_residual_construction_train_only(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    model = HybridResidualPredictor()
    model.fit(train_df, val_df)

    # Verify model was fitted with train row count
    assert model.training_metadata["training_rows"] == len(train_df)
    assert model.training_metadata["validation_rows"] == len(val_df)


# -----------------------------------------------------------------------------
# 7. Alpha weighting discrete sweep in {0.0, 0.25, 0.50, 0.75, 1.00}
# -----------------------------------------------------------------------------
def test_alpha_discrete_sweep_weights(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    model = HybridResidualPredictor()
    candidate_alphas = [0.0, 0.25, 0.50, 0.75, 1.00]
    model.fit(train_df, val_df, tune_alpha=True, candidate_alphas=candidate_alphas)

    assert model.alpha in candidate_alphas
    assert len(model.training_metadata["alpha_sweep_scores"]) == 5


# -----------------------------------------------------------------------------
# 8. Alpha bounds enforced in [0.0, 1.0]
# -----------------------------------------------------------------------------
def test_alpha_bounds_enforced():
    dim = HyperparameterSearchSpace.get_dim()
    vec = np.ones(dim)  # Max vector
    params = HyperparameterSearchSpace.vector_to_params(vec)
    assert 0.0 <= params["alpha_residual"] <= 1.0

    vec_zero = np.zeros(dim)
    params_zero = HyperparameterSearchSpace.vector_to_params(vec_zero)
    assert params_zero["alpha_residual"] == 0.0


# -----------------------------------------------------------------------------
# 9. No TEST leakage
# -----------------------------------------------------------------------------
def test_no_test_leakage(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    # Max train timestamp must precede min test timestamp
    max_train_t = pd.to_datetime(train_df["timestamp"]).max()
    min_test_t = pd.to_datetime(test_df["timestamp"]).min()
    assert max_train_t < min_test_t


# -----------------------------------------------------------------------------
# 10. No VALIDATION leakage into TRAIN preprocessing
# -----------------------------------------------------------------------------
def test_no_validation_leakage_into_train_preprocessing(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    model = PureMLPredictor(feature_cols=CONFIG_A_FEATURES)
    # Fit strictly on train
    model.fit(train_df, val_df)

    # Categorical categories learned should only come from TRAIN
    train_vessel_types = set(train_df["vessel_type"].unique())
    model_vessel_types = set(model.categorical_dtypes["vessel_type"].categories)
    assert model_vessel_types == train_vessel_types


# -----------------------------------------------------------------------------
# 11. QPSO equal evaluation budget to Random Search
# -----------------------------------------------------------------------------
def test_qpso_equal_evaluation_budget_to_random_search(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    # Budget of 6 evaluations (2 particles * 3 iters = 6)
    qpso = QPSOModelSelector(n_particles=2, max_iterations=3, seed=42)
    res_qpso = qpso.search(train_df, val_df)

    rs = RandomSearchModelSelector(total_budget=6, seed=42)
    res_rs = rs.search(train_df, val_df)

    assert res_qpso["evaluations"] == 6
    assert res_rs["evaluations"] == 6
    assert res_qpso["evaluations"] == res_rs["evaluations"]


# -----------------------------------------------------------------------------
# 12. QPSO validation-only objective
# -----------------------------------------------------------------------------
def test_qpso_validation_only_objective(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    qpso = QPSOModelSelector(n_particles=2, max_iterations=2, seed=42)
    # search requires val_df, does not accept test_df
    res = qpso.search(train_df, val_df)
    assert "best_validation_mae" in res
    assert res["best_validation_mae"] > 0


# -----------------------------------------------------------------------------
# 13. Random Search equal-budget comparison
# -----------------------------------------------------------------------------
def test_random_search_equal_budget_reproducibility(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    rs1 = RandomSearchModelSelector(total_budget=4, seed=100)
    res1 = rs1.search(train_df, val_df)

    rs2 = RandomSearchModelSelector(total_budget=4, seed=100)
    res2 = rs2.search(train_df, val_df)

    assert res1["best_validation_mae"] == res2["best_validation_mae"]
    assert res1["best_params"] == res2["best_params"]


# -----------------------------------------------------------------------------
# 14. Quantile monotonic non-crossing (q05 <= q50 <= q95)
# -----------------------------------------------------------------------------
def test_quantile_monotonic_non_crossing(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    q_model = QuantileUncertaintyPredictor(seed=42)
    q_model.fit(train_df, val_df=val_df)
    preds = q_model.predict_quantiles(test_df)

    q05 = preds["q05"]
    q50 = preds["q50"]
    q95 = preds["q95"]

    assert np.all(q05 <= q50)
    assert np.all(q50 <= q95)
    assert np.all(preds["quantile_derived_dispersion_proxy"] >= 0)


# -----------------------------------------------------------------------------
# 15. PICP correctness
# -----------------------------------------------------------------------------
def test_picp_metric_correctness():
    y = np.array([100.0, 110.0, 120.0, 130.0])
    q_low = np.array([90.0, 105.0, 115.0, 135.0])   # 4th is outside
    q_high = np.array([105.0, 115.0, 125.0, 140.0])

    picp = calculate_picp(y, q_low, q_high)
    assert picp == 75.0  # 3 of 4 covered = 75%


# -----------------------------------------------------------------------------
# 16. Pinball loss correctness
# -----------------------------------------------------------------------------
def test_pinball_loss_correctness():
    y = np.array([100.0, 100.0])
    y_pred = np.array([90.0, 110.0])  # underprediction (+10), overprediction (-10)
    tau = 0.9

    # For underprediction: tau * (y - y_pred) = 0.9 * 10 = 9.0
    # For overprediction: (1 - tau) * (y_pred - y) = 0.1 * 10 = 1.0
    # Mean = 5.0
    loss = pinball_loss(y, y_pred, tau=tau)
    assert pytest.approx(loss, abs=1e-4) == 5.0


# -----------------------------------------------------------------------------
# 17. Vessel-ID exclusion in cross-vessel CONFIG-A
# -----------------------------------------------------------------------------
def test_vessel_id_exclusion_in_cross_vessel_config_a():
    assert "vessel_id" not in CONFIG_A_FEATURES
    assert "vessel_id" in CONFIG_B_FEATURES

    model_a = PureMLPredictor(feature_cols=CONFIG_A_FEATURES)
    assert "vessel_id" not in model_a.feature_cols


# -----------------------------------------------------------------------------
# 18. Chronological temporal split correctness
# -----------------------------------------------------------------------------
def test_chronological_temporal_split_monotonicity(sample_data):
    splitter = LeakageSafeSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(sample_data)

    t_train = pd.to_datetime(train_df["timestamp"])
    t_val = pd.to_datetime(val_df["timestamp"])
    t_test = pd.to_datetime(test_df["timestamp"])

    assert t_train.max() <= t_val.min()
    assert t_val.max() <= t_test.min()


# -----------------------------------------------------------------------------
# 19. Synthetic model-mismatch presence
# -----------------------------------------------------------------------------
def test_synthetic_model_mismatch_presence():
    df_mismatch = generate_synthetic_maritime_dataset(n_records=300, seed=42, inject_anomalies=False, inject_model_mismatch=True)
    df_no_mismatch = generate_synthetic_maritime_dataset(n_records=300, seed=42, inject_anomalies=False, inject_model_mismatch=False)

    # Target values should differ due to model mismatch injection
    assert not np.allclose(df_mismatch["fuel_mass_flow_kg_h"].values, df_no_mismatch["fuel_mass_flow_kg_h"].values)


# -----------------------------------------------------------------------------
# 20. Reproducibility across seeds
# -----------------------------------------------------------------------------
def test_reproducibility_across_seeds():
    df1 = generate_synthetic_maritime_dataset(n_records=150, seed=77, inject_anomalies=False)
    df2 = generate_synthetic_maritime_dataset(n_records=150, seed=77, inject_anomalies=False)

    pd.testing.assert_frame_equal(df1, df2)


# -----------------------------------------------------------------------------
# 21. SOG / STW / Current Dimensional Consistency & Vector Screening Check
# -----------------------------------------------------------------------------
def test_sog_stw_current_dimensional_consistency_check(sample_data):
    from data.data_quality import DataQualityAuditor
    df_test = sample_data.copy()

    # Inject impossible velocity relationship: STW = 8 kn, SOG = 22 kn, Current = 0.2 m/s
    df_test.loc[0, "stw_kn"] = 8.0
    df_test.loc[0, "sog_kn"] = 22.0
    df_test.loc[0, "current_speed_ms"] = 0.2

    auditor = DataQualityAuditor()
    res = auditor.audit_dataset(df_test)

    # Must preserve row count and flag the observation as SUSPICIOUS
    assert len(df_test) == len(sample_data)
    assert res["summary"]["classifications"]["SUSPICIOUS"]["count"] > 0

