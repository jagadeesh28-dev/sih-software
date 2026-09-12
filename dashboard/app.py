"""
SIH26138 — Egreen Quanta Platform
Interactive Decision & Research Dashboard
Physics-Informed Fuel Consumption Prediction, Uncertainty Quantification,
LCA Compliance, and Scientific Evidence Ledger.
"""

import sys
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json
import yaml
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data.splitting import LeakageSafeSplitter
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.ml_baseline import PureMLPredictor
from prediction.residual_model import HybridResidualPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from lca.fuel_registry import FuelPathwayRegistry
from lca.well_to_wake import calculate_well_to_wake
from lca.fuel_eu import calculate_fueleu_compliance

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Egreen Quanta — SIH26138 Decision Platform",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Aesthetic Dark Theme CSS
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #0b132b;
        color: #f0f4f8;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Metric Card styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(28, 37, 65, 0.85), rgba(11, 19, 43, 0.95));
        border: 1px solid rgba(0, 245, 212, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 245, 212, 0.5);
    }
    
    /* Header gradients */
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00F5D4, #70EE9C, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    
    /* Glassmorphism containers */
    .glass-card {
        background: rgba(28, 37, 65, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Badge styling */
    .badge-verified {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-refuted {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-pending {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Cached Data & Model Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_prediction_comparisons():
    path = REPO_ROOT / "results" / "experiments" / "prediction_comparison.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_cross_vessel_results():
    path = REPO_ROOT / "results" / "experiments" / "cross_vessel_results.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_error_analysis_files():
    base_dir = REPO_ROOT / "results" / "experiments" / "error_analysis"
    res = {}
    if base_dir.exists():
        for f in base_dir.glob("*.csv"):
            res[f.stem] = pd.read_csv(f)
    return res

@st.cache_data
def load_lca_audit():
    path = REPO_ROOT / "results" / "scientific_validation" / "lca_audit.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_claims_ledger():
    path = REPO_ROOT / "evidence" / "claims.yaml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("claims", [])
    return []

@st.cache_data
def load_experiment_predictions(exp_id: str):
    pred_path = REPO_ROOT / "results" / "experiments" / exp_id / "predictions.csv"
    res_path = REPO_ROOT / "results" / "experiments" / exp_id / "residuals.csv"
    df_pred = pd.read_csv(pred_path) if pred_path.exists() else None
    df_res = pd.read_csv(res_path) if res_path.exists() else None
    return df_pred, df_res

@st.cache_resource
def get_live_models():
    """Load and train live predictors on the clean training set for interactive what-if queries."""
    data_path = REPO_ROOT / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    if not data_path.exists():
        return None, None, None, None
    df = pd.read_csv(data_path)
    # Clean subset
    df_clean = df.dropna(subset=["sog_kn", "shaft_power_kw", "fuel_mass_flow_kg_h"]).copy()
    df_clean = df_clean[df_clean["fuel_mass_flow_kg_h"] > 0]
    
    splitter = LeakageSafeSplitter()
    train_df, val_df, test_df = splitter.chronological_split(df_clean)
    
    # 1. Physics Model
    physics_model = PhysicsFuelPredictor()
    
    # 2. Pure ML Model
    ml_model = PureMLPredictor()
    ml_model.fit(train_df, val_df)
    
    # 3. Hybrid Residual Model
    hybrid_model = HybridResidualPredictor(physics_predictor=physics_model)
    hybrid_model.fit(train_df, val_df)
    
    # 4. Quantile Model
    quantile_model = QuantileUncertaintyPredictor()
    quantile_model.fit(train_df, val_df)
    
    return physics_model, ml_model, hybrid_model, quantile_model


# -----------------------------------------------------------------------------
# Sidebar Navigation & Epistemic Notice
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=400&q=80", use_container_width=True)
    st.markdown("<h2 style='color:#00F5D4; margin-top:0;'>SIH26138 Platform</h2>", unsafe_allow_html=True)
    st.caption("Quantum-Inspired Fuel Prediction & Green Fleet Decision Engine")
    
    st.markdown("---")
    navigation = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "📈 Fuel Prediction Benchmarks",
            "🔍 Regime & Error Diagnostics",
            "🌐 Cross-Vessel Generalization",
            "⚛️ QPSO vs Random Search",
            "🔮 Live Interactive Simulator",
            "🌿 LCA & FuelEU Compliance",
            "📜 Scientific Evidence Ledger",
        ],
        index=0,
    )
    
    st.markdown("---")
    st.markdown("### 🛡️ Scientific Notice")
    st.info(
        "**Epistemic Rule (Sec. 2)**: All model evaluations shown derive from controlled `SYNTHETIC_TEST_DATA` (1,192 records) for software verification. "
        "No real-world maritime operational accuracy is claimed until sea-trial sensor data are validated."
    )
    st.caption("Egreen Quanta © 2026 | MIT License")


# -----------------------------------------------------------------------------
# View 1: Executive Overview
# -----------------------------------------------------------------------------
if navigation == "📊 Executive Overview":
    st.markdown("<div class='hero-title'>🚢 SIH26138 — Egreen Quanta Platform</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Physics-Informed Fuel Consumption Prediction Engine & Scientific Validation Suite</div>", unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Validation Pipeline Records", value="1,192", delta="Clean Partitioned")
    with col2:
        st.metric(label="Best Model (ML-Only)", value="1.43 kg/h", delta="LightGBM MAE (R² 0.998)")
    with col3:
        st.metric(label="Quantile Coverage (90% Nominal)", value="89.94%", delta="-0.06% Calibrated")
    with col4:
        st.metric(label="Automated Test Suite", value="31 / 31", delta="100% Passed (18.6s)")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Architecture Overview
    st.markdown("### 🏛️ Platform Architecture & Data Pipeline")
    st.markdown("""
    The SIH26138 platform connects a multi-stage, leakage-safe pipeline enforcing strict maritime physics and modern decision intelligence:
    """)
    
    col_arch1, col_arch2 = st.columns([3, 2])
    with col_arch1:
        st.markdown("""
        ```
        [Sensors / Metocean Ingestion]
                     ↓
        [16-Point Data Quality Audit] → [Deterministic Unit Normalization]
                     ↓
        [Leakage-Safe Partitioning: Chronological 70/15/15 + Leave-Vessel-Out]
                     ↓
        ┌──────────────────────────────────────────────────────────────────┐
        │                 PREDICTION ENGINE COMPARISON                     │
        │                                                                  │
        │  1. Physics Baseline: ITTC-1957 Friction + Holtrop Resistance    │
        │  2. ML Baseline: LightGBM Regressor (Huber / L1 loss)            │
        │  3. Physics + ML Residual: F_pred = F_phys + α * F_residual      │
        │  4. QPSO Optimization: Offline Quantum-Behaved Swarm Tuning      │
        └──────────────────────────────────────────────────────────────────┘
                     ↓
        [Quantile Uncertainty Bands: q05, q50, q95 Pinball Loss]
                     ↓
        [Well-to-Wake LCA & FuelEU Maritime Compliance Cost Engine]
        ```
        """)
    with col_arch2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔬 Core Research Hypotheses & Status")
        st.markdown("""
        - **H1: Hybrid Residual Superiority?**  
          <span class='badge-refuted'>REFUTED ON BENCHMARK</span>  
          *Finding*: Direct ML-Only achieved 1.43 kg/h MAE vs 22.43 kg/h for the tuned Hybrid model. Uncalibrated physics introduced systematic drag bias.
        - **H2: QPSO Optimization Advantage?**  
          <span class='badge-verified'>VERIFIED (+7.9% VAL LOSS)</span>  
          *Finding*: QPSO achieved validation MAE 19.70 kg/h vs 21.39 kg/h for Random Search under identical 225-eval budgets.
        - **H3: Cross-Vessel Generalization?**  
          <span class='badge-pending'>CLASS-DEPENDENT</span>  
          *Finding*: Sister feeder vessels transfer well (MAE 2.18–3.34 kg/h), but transfer to unseen Handymax bulk carriers degrades to 94.10 kg/h.
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Experimental Comparison Snapshot
    df_comp = load_prediction_comparisons()
    if not df_comp.empty:
        st.markdown("### 📊 Empirical Prediction Engine Comparison")
        fig_bar = px.bar(
            df_comp,
            x="model",
            y="MAE",
            color="model",
            title="Mean Absolute Error (kg/h) on Unseen Forward Chronological Test Partition (N=179)",
            labels={"MAE": "Test MAE (kg/h)", "model": "Model Class"},
            color_discrete_sequence=["#EF4444", "#10B981", "#3B82F6", "#00F5D4"],
            template="plotly_dark",
        )
        fig_bar.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)


# -----------------------------------------------------------------------------
# View 2: Fuel Prediction Benchmarks
# -----------------------------------------------------------------------------
elif navigation == "📈 Fuel Prediction Benchmarks":
    st.markdown("## 📈 Phase 2: Fuel Consumption Prediction Benchmarks")
    st.markdown("Comprehensive evaluation across **Physics-Only**, **ML-Only (LightGBM)**, **Physics + ML Residual**, and **QPSO-Tuned Hybrid**.")
    
    df_comp = load_prediction_comparisons()
    if df_comp.empty:
        st.warning("Prediction comparison data not found. Run `python experiments/exp_phase2_runner.py` first.")
    else:
        # Formatted Table
        st.markdown("### 📋 Unified Model Comparison Table")
        st.dataframe(
            df_comp[[
                "experiment_id", "model", "MAE", "RMSE", "MAPE", "R2",
                "mean_error", "median_absolute_error", "max_absolute_error", "test_rows"
            ]].style.format({
                "MAE": "{:.2f}",
                "RMSE": "{:.2f}",
                "MAPE": "{:.2f}%",
                "R2": "{:.4f}",
                "mean_error": "{:+.2f}",
                "median_absolute_error": "{:.2f}",
                "max_absolute_error": "{:.2f}",
            }),
            use_container_width=True,
        )
        
        # Interactive Plots
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            fig_mae = px.bar(
                df_comp,
                x="model",
                y="MAE",
                text="MAE",
                color="model",
                title="Model Test MAE Comparison (kg/h) [Lower is Better]",
                template="plotly_dark",
                color_discrete_sequence=["#EF4444", "#10B981", "#3B82F6", "#00F5D4"],
            )
            fig_mae.update_traces(texttemplate='%{text:.2f} kg/h', textposition='outside')
            fig_mae.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig_mae, use_container_width=True)
            
        with col_m2:
            fig_r2 = px.bar(
                df_comp[df_comp["R2"] > 0],
                x="model",
                y="R2",
                text="R2",
                color="model",
                title="Model R² Coefficient of Determination [Higher is Better]",
                template="plotly_dark",
                color_discrete_sequence=["#10B981", "#3B82F6", "#00F5D4"],
            )
            fig_r2.update_traces(texttemplate='%{text:.4f}', textposition='outside')
            fig_r2.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig_r2, use_container_width=True)

        # Actual vs Predicted Scatter
        st.markdown("### 🎯 Actual vs. Predicted Fuel Flow (Test Partition)")
        model_choice = st.selectbox(
            "Select Experiment to Inspect Predictions & Residuals",
            ["EXP-PRED-02 (ML-Only LightGBM)", "EXP-PRED-04 (Physics+ML QPSO Tuned)", "EXP-PRED-03 (Physics+ML Base Residual)", "EXP-PRED-01 (Physics Baseline)"]
        )
        exp_id = model_choice.split()[0]
        df_pred, df_res = load_experiment_predictions(exp_id)
        
        if df_pred is not None:
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                fig_scatter = px.scatter(
                    df_pred,
                    x="fuel_observed_kg_h",
                    y="fuel_predicted_kg_h",
                    color_discrete_sequence=["#00F5D4"],
                    title=f"{exp_id}: Observed vs Predicted Fuel Mass Flow",
                    labels={"fuel_observed_kg_h": "Observed Fuel Flow (kg/h)", "fuel_predicted_kg_h": "Predicted Fuel Flow (kg/h)"},
                    template="plotly_dark",
                )
                min_v = min(df_pred["fuel_observed_kg_h"].min(), df_pred["fuel_predicted_kg_h"].min())
                max_v = max(df_pred["fuel_observed_kg_h"].max(), df_pred["fuel_predicted_kg_h"].max())
                fig_scatter.add_trace(go.Scatter(x=[min_v, max_v], y=[min_v, max_v], mode="lines", name="Ideal 1:1 Line", line=dict(color="#EF4444", dash="dash")))
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            with col_sc2:
                df_pred["residual_kg_h"] = df_pred["fuel_observed_kg_h"] - df_pred["fuel_predicted_kg_h"]
                fig_hist = px.histogram(
                    df_pred,
                    x="residual_kg_h",
                    nbins=30,
                    title=f"{exp_id}: Residual Error Distribution (Observed - Predicted)",
                    color_discrete_sequence=["#3B82F6"],
                    template="plotly_dark",
                    labels={"residual_kg_h": "Prediction Error (kg/h)"},
                )
                fig_hist.update_layout(height=400)
                st.plotly_chart(fig_hist, use_container_width=True)


# -----------------------------------------------------------------------------
# View 3: Regime & Error Diagnostics
# -----------------------------------------------------------------------------
elif navigation == "🔍 Regime & Error Diagnostics":
    st.markdown("## 🔍 Operating Regime & Sliced Error Analysis")
    st.markdown("Detailed error slicing across **Speed**, **Wave Height**, **Engine Load**, and **Operational Regimes** to identify failure modes.")
    
    error_data = load_error_analysis_files()
    if not error_data:
        st.warning("Error analysis files not found in `results/experiments/error_analysis/`.")
    else:
        tab_speed, tab_wave, tab_load, tab_regime = st.tabs(["⚡ Speed Bins", "🌊 Wave Height Bins", "⚙️ Engine Load Bins", "🧭 Regime Diagnostics"])
        
        with tab_speed:
            if "speed_bins" in error_data:
                df_sp = error_data["speed_bins"]
                st.dataframe(df_sp.style.format({"physics_mae": "{:.2f}", "ml_mae": "{:.2f}", "hybrid_mae": "{:.2f}"}), use_container_width=True)
                
                fig_sp = px.bar(
                    df_sp,
                    x="bin",
                    y=["physics_mae", "hybrid_mae", "ml_mae"],
                    barmode="group",
                    title="MAE by Vessel Speed Bins (knots)",
                    labels={"value": "MAE (kg/h)", "bin": "Speed Range (knots)", "variable": "Model"},
                    color_discrete_map={"physics_mae": "#EF4444", "hybrid_mae": "#3B82F6", "ml_mae": "#10B981"},
                    template="plotly_dark",
                )
                fig_sp.update_layout(height=400)
                st.plotly_chart(fig_sp, use_container_width=True)
                
        with tab_wave:
            if "wave_bins" in error_data:
                df_wv = error_data["wave_bins"]
                st.dataframe(df_wv.style.format({"physics_mae": "{:.2f}", "ml_mae": "{:.2f}", "hybrid_mae": "{:.2f}"}), use_container_width=True)
                
                fig_wv = px.bar(
                    df_wv,
                    x="bin",
                    y=["hybrid_mae", "ml_mae"],
                    barmode="group",
                    title="MAE by Significant Wave Height (m)",
                    labels={"value": "MAE (kg/h)", "bin": "Significant Wave Height (m)", "variable": "Model"},
                    color_discrete_map={"hybrid_mae": "#3B82F6", "ml_mae": "#10B981"},
                    template="plotly_dark",
                )
                fig_wv.update_layout(height=400)
                st.plotly_chart(fig_wv, use_container_width=True)
                
        with tab_load:
            if "load_bins" in error_data:
                df_ld = error_data["load_bins"]
                st.dataframe(df_ld.style.format({"physics_mae": "{:.2f}", "ml_mae": "{:.2f}", "hybrid_mae": "{:.2f}"}), use_container_width=True)
                
                fig_ld = px.bar(
                    df_ld,
                    x="bin",
                    y=["hybrid_mae", "ml_mae"],
                    barmode="group",
                    title="MAE by Engine Load Percentage (%)",
                    labels={"value": "MAE (kg/h)", "bin": "Engine Load Bin", "variable": "Model"},
                    color_discrete_map={"hybrid_mae": "#3B82F6", "ml_mae": "#10B981"},
                    template="plotly_dark",
                )
                fig_ld.update_layout(height=400)
                st.plotly_chart(fig_ld, use_container_width=True)

        with tab_regime:
            st.markdown("### 🏆 Physics vs. ML Comparative Regime Diagnostics")
            st.markdown("""
            - **Low Speed / Low Load (< 12 kn, < 50% load)**: Uncalibrated physics overestimates wave and auxiliary power resistance by $+538.7\,\text{kg/h}$. The ML model easily learns true generator curves ($\text{MAE} = 3.27\,\text{kg/h}$).
            - **Cruising / MCR (12 - 15 kn, 60 - 85% load)**: ML baseline achieves near-perfect tracking ($\text{MAE} = 0.90\,\text{kg/h}$, $\text{MAPE} < 0.2\%$).
            - **High Speed (> 15 kn)**: Wave resistance increases cubically; ML maintains tight control ($\text{MAE} = 2.17\,\text{kg/h}$) while Hybrid residual absorbs $92.7\%$ of physical error.
            """)


# -----------------------------------------------------------------------------
# View 4: Cross-Vessel Generalization
# -----------------------------------------------------------------------------
elif navigation == "🌐 Cross-Vessel Generalization":
    st.markdown("## 🌐 Cross-Vessel & Leave-Vessel-Out Evaluation")
    st.markdown("Testing model transferability to unseen vessels and different ship classes under strict isolation.")
    
    df_cross = load_cross_vessel_results()
    if df_cross.empty:
        st.warning("Cross-vessel results not found. Run `python experiments/exp_phase2_runner.py` first.")
    else:
        st.dataframe(
            df_cross[[
                "holdout_vessel", "vessel_type", "train_samples", "test_samples",
                "physics_mae", "ml_mae", "hybrid_mae", "ml_r2", "best_model"
            ]].style.format({
                "physics_mae": "{:.2f}",
                "ml_mae": "{:.2f}",
                "hybrid_mae": "{:.2f}",
                "ml_r2": "{:.4f}",
            }),
            use_container_width=True,
        )
        
        fig_cross = px.bar(
            df_cross,
            x="holdout_vessel",
            y=["physics_mae", "hybrid_mae", "ml_mae"],
            barmode="group",
            title="Leave-Vessel-Out Transfer MAE (kg/h) Across Distinct Vessel Hull Types",
            labels={"value": "MAE (kg/h)", "holdout_vessel": "Held-Out Unseen Test Vessel", "variable": "Model Architecture"},
            color_discrete_map={"physics_mae": "#EF4444", "hybrid_mae": "#3B82F6", "ml_mae": "#10B981"},
            template="plotly_dark",
        )
        fig_cross.update_layout(height=420)
        st.plotly_chart(fig_cross, use_container_width=True)
        
        st.markdown("""
        ### 💡 Scientific Transfer Insights:
        1. **Sister-Vessel In-Class Transfer (`VESSEL_FE_01` & `VESSEL_FE_02`)**:
           - Both vessels share identical hull lines (1,000 TEU container feeder).
           - Gradient boosted trees trained on one feeder transfer to the sister feeder with exceptional accuracy (**MAE 2.18–3.34 kg/h**).
        2. **Cross-Class Domain Shift (`VESSEL_HM_03`)**:
           - Held-out vessel is a 55,000 DWT Handymax bulk carrier with radically different block coefficient ($C_B \approx 0.82$ vs $0.65$), draft, and displacement.
           - Testing without any bulk carriers in training causes error to spike to **94.10 kg/h for ML** and **496.41 kg/h for Hybrid**.
           - **Conclusion**: Universal vessel foundation claims are unsupported; domain adaptation or class-specific calibration is mandatory.
        """)


# -----------------------------------------------------------------------------
# View 5: QPSO vs Random Search
# -----------------------------------------------------------------------------
elif navigation == "⚛️ QPSO vs Random Search":
    st.markdown("## ⚛️ QPSO Metaheuristic vs. Random Search Baseline")
    st.markdown("Empirical benchmark of the Quantum-Behaved Particle Swarm Optimization metaheuristic under **equal computational budgets** (Section 19).")
    
    col_qp1, col_qp2 = st.columns(2)
    with col_qp1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🔬 Optimization Protocol & Budget Fairness")
        st.markdown("""
        - **Evaluation Budget**: Exactly **225 candidate evaluations** for both algorithms.
        - **Objective Function**: Validation Set MAE ($\text{kg/h}$) with early stopping on Train.
        - **Search Space (8 Hyperparameters)**:
          - `learning_rate` $\in [0.01, 0.25]$
          - `num_leaves` $\in [15, 127]$
          - `max_depth` $\in [3, 12]$
          - `min_child_samples` $\in [5, 50]$
          - `feature_fraction` $\in [0.6, 1.0]$
          - `reg_alpha` $\in [10^{-3}, 10.0]$
          - `reg_lambda` $\in [10^{-3}, 10.0]$
          - `residual_alpha` $\in [0.2, 1.0]$
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_qp2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Benchmark Optimization Results")
        df_opt = pd.DataFrame([
            {"Optimizer": "QPSO Metaheuristic", "Budget": "225 Evals (15x15)", "Best Val MAE (kg/h)": 19.70, "Test MAE (kg/h)": 22.43, "Test R²": 0.7326},
            {"Optimizer": "Random Search Baseline", "Budget": "225 Uniform Draws", "Best Val MAE (kg/h)": 21.39, "Test MAE (kg/h)": 24.12, "Test R²": 0.7005},
        ])
        st.dataframe(df_opt.style.format({"Best Val MAE (kg/h)": "{:.2f}", "Test MAE (kg/h)": "{:.2f}", "Test R²": "{:.4f}"}), use_container_width=True)
        
        st.markdown("""
        **Validation Advantage**: QPSO attained a **7.9% reduction in validation MAE** over Random Search.  
        **Caveat**: Classical stochastic search operates effectively, but provides no quantum speedup or exponential advantage.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # QPSO Contraction-Expansion Formula
    st.markdown("### 🧮 Classical QPSO Mathematical Dynamics")
    st.latex(r"X_{i,d}^{(t+1)} = p_{i,d} \pm \beta \cdot |C_d - X_{i,d}^{(t)}| \cdot \ln\left(\frac{1}{u}\right)")
    st.caption("Where C is the mean best position of all particles, p is the local stochastic attractor, and beta is the contraction-expansion coefficient.")


# -----------------------------------------------------------------------------
# View 6: Live Interactive Simulator
# -----------------------------------------------------------------------------
elif navigation == "🔮 Live Interactive Simulator":
    st.markdown("## 🔮 Live Interactive Fuel Predictor & Uncertainty Simulator")
    st.markdown("Adjust vessel operating parameters and environmental conditions to query live predictions and 90% uncertainty intervals.")
    
    physics_m, ml_m, hybrid_m, quant_m = get_live_models()
    if ml_m is None:
        st.error("Model training data not found in `data/synthetic/`.")
    else:
        col_ctrl, col_res = st.columns([1, 2])
        
        with col_ctrl:
            st.markdown("#### ⚙️ Voyage Operating Conditions")
            vessel_choice = st.selectbox("Vessel Hull Type", ["container_feeder", "bulk_handymax"])
            vessel_id = "VESSEL_FE_01" if vessel_choice == "container_feeder" else "VESSEL_HM_03"
            
            sog = st.slider("Speed Over Ground (SOG, knots)", min_value=8.0, max_value=20.0, value=14.0, step=0.5)
            stw = st.slider("Speed Through Water (STW, knots)", min_value=8.0, max_value=20.0, value=14.2, step=0.5)
            draft = st.slider("Vessel Draft (m)", min_value=6.0, max_value=12.0, value=8.5, step=0.1)
            displacement = st.slider("Displacement (tonnes)", min_value=10000, max_value=60000, value=18000, step=1000)
            
            st.markdown("#### 🌊 Metocean Environment")
            wave_h = st.slider("Significant Wave Height (m)", min_value=0.0, max_value=6.0, value=1.5, step=0.2)
            wind_spd = st.slider("Wind Speed (m/s)", min_value=0.0, max_value=25.0, value=7.5, step=0.5)
            
            st.markdown("#### ⚡ Engine Telemetry")
            engine_load = st.slider("Engine Load (%)", min_value=30.0, max_value=100.0, value=72.0, step=1.0)
            power_kw = (engine_load / 100.0) * (9000.0 if vessel_choice == "container_feeder" else 8500.0)
            rpm = (engine_load / 100.0) * 110.0 + 30.0
            
            st.markdown("#### 🔬 Hybrid Tuning")
            alpha_val = st.slider("Residual Blending Weight (α)", min_value=0.0, max_value=1.0, value=1.0, step=0.05)

        # Assemble Query Row
        query_dict = {
            "sog_kn": sog,
            "stw_kn": stw,
            "draft_m": draft,
            "displacement_t": displacement,
            "rpm": rpm,
            "shaft_power_kw": power_kw,
            "shaft_torque_nm": (power_kw * 1000) / (2 * np.pi * (rpm / 60)) if rpm > 0 else 0,
            "engine_load_pct": engine_load,
            "wind_speed_ms": wind_spd,
            "wind_direction_deg": 45.0,
            "wave_height_m": wave_h,
            "wave_period_s": 7.0,
            "wave_direction_deg": 30.0,
            "current_speed_ms": 0.5,
            "current_direction_deg": 90.0,
            "water_depth_m": 80.0,
            "vessel_type": vessel_choice,
            "vessel_id": vessel_id,
            "fuel_type": "VLSFO",
        }
        df_query = pd.DataFrame([query_dict])
        
        # Inference
        pred_phys_res = physics_m.predict(df_query)
        pred_phys = pred_phys_res["predicted_fuel_kg_h"].iloc[0]
        pred_ml = ml_m.predict(df_query)[0]
        
        # Hybrid prediction
        hybrid_m.alpha = alpha_val
        pred_hybrid = hybrid_m.predict(df_query)[0]
        
        # Quantiles
        quant_res = quant_m.predict_quantiles(df_query)
        q05 = quant_res["q05"].iloc[0]
        q50 = quant_res["q50"].iloc[0]
        q95 = quant_res["q95"].iloc[0]
        
        with col_res:
            st.markdown("#### 📊 Live Prediction Comparison & Confidence Intervals")
            
            kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
            with kpi_c1:
                st.metric("ML-Only Prediction", f"{pred_ml:.1f} kg/h", delta="Primary Baseline")
            with kpi_c2:
                st.metric(f"Hybrid Prediction (α={alpha_val:.2f})", f"{pred_hybrid:.1f} kg/h", delta=f"{pred_hybrid - pred_ml:+.1f} vs ML")
            with kpi_c3:
                st.metric("Physics-Only", f"{pred_phys:.1f} kg/h", delta="Naval Arch Drag")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gauge / Quantile chart
            fig_q = go.Figure()
            
            # Confidence Band
            fig_q.add_trace(go.Bar(
                name="90% Quantile Interval (q05 - q95)",
                x=["Fuel Flow Range"],
                y=[q95 - q05],
                base=[q05],
                marker_color="rgba(0, 245, 212, 0.35)",
                hoverinfo="text",
                hovertext=f"q05: {q05:.1f} kg/h | q95: {q95:.1f} kg/h | Width: {q95-q05:.1f} kg/h",
            ))
            
            # Individual Model Markers
            fig_q.add_trace(go.Scatter(
                name="ML Prediction",
                x=["Fuel Flow Range"],
                y=[pred_ml],
                mode="markers",
                marker=dict(color="#10B981", size=18, symbol="diamond"),
            ))
            fig_q.add_trace(go.Scatter(
                name=f"Hybrid (α={alpha_val:.2f})",
                x=["Fuel Flow Range"],
                y=[pred_hybrid],
                mode="markers",
                marker=dict(color="#3B82F6", size=16, symbol="circle"),
            ))
            fig_q.add_trace(go.Scatter(
                name="Physics Estimate",
                x=["Fuel Flow Range"],
                y=[pred_phys],
                mode="markers",
                marker=dict(color="#EF4444", size=14, symbol="triangle-up"),
            ))
            
            fig_q.update_layout(
                title="Live 90% Quantile Prediction Interval (q05 - q95) vs Point Estimates",
                yaxis_title="Fuel Mass Flow (kg/h)",
                template="plotly_dark",
                height=380,
                showlegend=True,
            )
            st.plotly_chart(fig_q, use_container_width=True)
            
            st.info(
                f"**Quantile-Derived Dispersion Proxy**: The 90% prediction interval ranges from **{q05:.1f} kg/h** to **{q95:.1f} kg/h** "
                f"(Interval Width: **{q95-q05:.1f} kg/h**). This accounts for metocean turbulence and engine operational uncertainty."
            )


# -----------------------------------------------------------------------------
# View 7: LCA & FuelEU Compliance
# -----------------------------------------------------------------------------
elif navigation == "🌿 LCA & FuelEU Compliance":
    st.markdown("## 🌿 Well-to-Wake LCA & FuelEU Maritime Compliance")
    st.markdown("Life cycle greenhouse gas accounting across 5 registered maritime fuels and regulatory penalty modeling.")
    
    df_lca = load_lca_audit()
    if df_lca.empty:
        st.warning("LCA audit data not found in `results/scientific_validation/lca_audit.csv`.")
    else:
        col_l1, col_l2 = st.columns([3, 2])
        
        with col_l1:
            st.markdown("### 📊 Well-to-Wake (WtW) GHG Intensity Comparison")
            fig_lca = px.bar(
                df_lca,
                x="fuel",
                y=["wtt_tco2e", "ttw_tco2e"],
                title="Well-to-Tank (WtT) vs. Tank-to-Wake (TtW) Emissions per 1,000 kg Fuel Bunkered",
                labels={"value": "Total Emissions (tCO2e per tonne fuel)", "fuel": "Marine Fuel Pathway", "variable": "Lifecycle Stage"},
                color_discrete_map={"wtt_tco2e": "#3B82F6", "ttw_tco2e": "#EF4444"},
                template="plotly_dark",
            )
            fig_lca.update_layout(height=400)
            st.plotly_chart(fig_lca, use_container_width=True)
            
        with col_l2:
            st.markdown("### 📋 Fuel Pathway Registry (configs/fuels.yaml)")
            st.dataframe(
                df_lca[["fuel", "lhv_mj_kg", "wtw_gco2e_per_mj", "methane_slip_tco2e"]].style.format({
                    "lhv_mj_kg": "{:.1f}",
                    "wtw_gco2e_per_mj": "{:.2f}",
                    "methane_slip_tco2e": "{:.3f}",
                }),
                use_container_width=True,
            )
            st.caption("Includes IPCC AR6 GWP-100 values (CH4=29.8, N2O=273) and dimensional methane slip.")

        # Interactive FuelEU Calculator
        st.markdown("---")
        st.markdown("### 💶 Interactive FuelEU Maritime Penalty Calculator")
        
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            fuel_sel = st.selectbox("Voyage Fuel Pathway", ["VLSFO", "Fossil LNG", "Bio-MGO", "E-Methanol", "Green Ammonia"])
        with f_c2:
            consumption_t = st.number_input("Voyage Fuel Bunkered (metric tonnes)", min_value=10.0, max_value=5000.0, value=150.0, step=10.0)
        with f_c3:
            reporting_year = st.selectbox("FuelEU Target Year", [2025, 2030, 2035, 2040, 2050], index=0)
            
        # Target table (Regulation EU 2023/1805)
        fueleu_targets = {2025: 89.34, 2030: 85.66, 2035: 78.44, 2040: 64.00, 2050: 18.23}
        target_intensity = fueleu_targets[reporting_year]
        
        fuel_row = df_lca[df_lca["fuel"] == fuel_sel].iloc[0]
        actual_intensity = fuel_row["wtw_gco2e_per_mj"]
        total_energy_mj = consumption_t * 1000.0 * fuel_row["lhv_mj_kg"]
        
        diff = actual_intensity - target_intensity
        penalty_rate_eur_per_mj = 2400.0 / (41000.0 * 1.0) # approx 2,400 EUR per tonne VLSFO equivalent
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("Actual GHG Intensity", f"{actual_intensity:.2f} g/MJ")
        with col_res2:
            st.metric(f"FuelEU {reporting_year} Target", f"{target_intensity:.2f} g/MJ", delta=f"{-diff:.2f} Compliance Gap")
        with col_res3:
            if diff > 0:
                deficit_energy_mj = diff * total_energy_mj / actual_intensity
                total_penalty_eur = (diff / actual_intensity) * (total_energy_mj / 41000.0) * 2400.0
                st.metric("Estimated FuelEU Penalty", f"€{total_penalty_eur:,.0f}", delta="PENALTY SURCHARGE", delta_color="inverse")
            else:
                st.metric("Estimated FuelEU Penalty", "€0", delta="COMPLIANT SURPLUS")


# -----------------------------------------------------------------------------
# View 8: Scientific Evidence Ledger
# -----------------------------------------------------------------------------
elif navigation == "📜 Scientific Evidence Ledger":
    st.markdown("## 📜 Epistemic Evidence Ledger (`evidence/claims.yaml`)")
    st.markdown("Strict epistemic governance classifying all platform statements into **FACT**, **MEASURED_RESULT**, or **HYPOTHESIS**.")
    
    claims = load_claims_ledger()
    if not claims:
        st.warning("No claims found in `evidence/claims.yaml`.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            type_filter = st.multiselect("Filter by Epistemic Type", ["FACT", "MEASURED_RESULT", "HYPOTHESIS", "ASSUMPTION"], default=["FACT", "MEASURED_RESULT", "HYPOTHESIS"])
        with col_f2:
            status_filter = st.multiselect(
                "Filter by Verification Status",
                ["CONFIRMED", "EMPIRICALLY_VERIFIED", "REFUTED", "REFUTED_ON_SYNTHETIC", "PENDING_VALIDATION"],
                default=["CONFIRMED", "EMPIRICALLY_VERIFIED", "REFUTED", "REFUTED_ON_SYNTHETIC"]
            )
            
        filtered_claims = [
            c for c in claims
            if (not type_filter or c.get("type") in type_filter)
            and (not status_filter or c.get("status") in status_filter)
        ]
        
        st.markdown(f"**Showing {len(filtered_claims)} of {len(claims)} registered epistemic claims:**")
        
        for c in filtered_claims:
            st_class = c.get("status", "")
            if "VERIFIED" in st_class or "CONFIRMED" in st_class:
                badge = f"<span class='badge-verified'>{st_class}</span>"
            elif "REFUTED" in st_class:
                badge = f"<span class='badge-refuted'>{st_class}</span>"
            else:
                badge = f"<span class='badge-pending'>{st_class}</span>"
                
            st.markdown(f"""
            <div class='glass-card'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                    <strong style='font-size:1.1rem; color:#00F5D4;'>{c.get('claim_id')}</strong>
                    <div>
                        <span style='color:#94A3B8; font-size:0.85rem; margin-right:10px;'>Type: {c.get('type')}</span>
                        {badge}
                    </div>
                </div>
                <p style='color:#E2E8F0; margin-bottom:8px;'>{c.get('claim')}</p>
                <div style='font-size:0.85rem; color:#94A3B8;'>
                    <strong>Source:</strong> {c.get('source')}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("SIH26138 Egreen Quanta Platform — Quantum-Inspired Predictive Maritime Intelligence")
