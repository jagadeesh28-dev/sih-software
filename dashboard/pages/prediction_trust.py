"""
Egreen Quanta - SIH26138: Screen 3 — Prediction & Trust.
Exposes dual-model cross-checking (QI-C1 vs MODEL-REAL-04),
split conformal prediction intervals, out-of-distribution (OOD) distance gauge,
and hardened safe routing policy.
Conforms to Sections 2, 7, and 12 of Operator UI Master Requirements.
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_cached_predictor, get_default_fleet_state


def render_prediction_trust():
    """Renders Screen 3 Prediction & Trust."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Prediction & Trust Engine
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Dual-model architectural cross-check, calibrated 90% split conformal prediction intervals, and convex envelope OOD guard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    predictor = get_cached_predictor()
    fleet = get_default_fleet_state()

    # Interactive Input Form for Trust Engine
    st.markdown("<h4 style='color: #38bdf8;'>1. Real-Time Telemetry & Operating Inputs</h4>", unsafe_allow_html=True)
    
    col_v, col_s, col_d, col_disp = st.columns(4)
    with col_v:
        v_choice = st.selectbox("Vessel Selection", options=[v["name"] for v in fleet], index=0)
        vessel = next(v for v in fleet if v["name"] == v_choice)
    with col_s:
        stw_input = st.slider("Speed STW (kn)", min_value=8.0, max_value=22.0, value=float(vessel["stw_kn"]), step=0.1)
    with col_d:
        draft_input = st.slider("Draft (m)", min_value=2.5, max_value=12.0, value=float(vessel["draft_m"]), step=0.1)
    with col_disp:
        disp_input = st.number_input("Displacement (t)", min_value=1000.0, max_value=80000.0, value=float(vessel["displacement_t"]), step=500.0)

    col_env1, col_env2, col_env3, col_cov = st.columns(4)
    with col_env1:
        wave_input = st.slider("Wave Height Hs (m)", min_value=0.0, max_value=10.0, value=float(vessel["wave_height_m"]), step=0.2)
    with col_env2:
        depth_input = st.slider("Water Depth (m)", min_value=10.0, max_value=300.0, value=float(vessel["water_depth_m"]), step=5.0)
    with col_env3:
        fuel_choice = st.selectbox("Bunker Fuel", options=["vlsfo", "mgo"], index=0)
    with col_cov:
        cov_level = st.selectbox("Conformal Coverage", options=[0.90, 0.95], index=0, format_func=lambda x: f"{int(x*100)}% Nominal")

    # Construct input dictionary
    eval_input = {
        "vessel_id": vessel["id"],
        "vessel_type": vessel["vessel_type"],
        "fuel_type": fuel_choice,
        "stw_kn": stw_input,
        "sog_kn": stw_input,
        "draft_m": draft_input,
        "displacement_t": disp_input,
        "wind_speed_ms": float(vessel["wind_speed_ms"]),
        "wave_height_m": wave_input,
        "water_depth_m": depth_input,
    }

    # Execute authoritative prediction with uncertainty
    res = predictor.predict_fuel_with_uncertainty(eval_input, coverage=cov_level)
    unc = res["uncertainty"]
    cross = res.get("cross_check", {})
    env_dist = res.get("envelope_distance", 0.0)
    routing = res.get("routing_status", "NORMAL")
    selected_model = res["model"]

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Dual-Model Cross-Check Section
    st.markdown("<h4 style='color: #38bdf8;'>2. Dual-Model Cross-Check (Candidate vs Reference Anchor)</h4>", unsafe_allow_html=True)
    
    qi_pred = cross.get("qi_c1_vessel_type_pred_kg_h") or cross.get("qi_c1_pred_kg_h")
    m04_pred = cross.get("model_real_04_pred_kg_h")
    delta_val = cross.get("delta_kg_h", 0.0)

    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #00E5FF; border-radius: 6px; padding: 14px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Candidate Model</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-top: 2px;">QI-C1-vessel-type</div>
                <div style="font-size: 26px; font-weight: 800; color: #00E5FF; margin-top: 6px;">
                    {qi_pred:,.2f} <span style="font-size: 13px; color: #94a3b8;">kg/h</span>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Naval architectural conditioning (7 features)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_m2:
        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #38bdf8; border-radius: 6px; padding: 14px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Reference Anchor</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-top: 2px;">MODEL-REAL-04</div>
                <div style="font-size: 26px; font-weight: 800; color: #38bdf8; margin-top: 6px;">
                    {m04_pred:,.2f} <span style="font-size: 13px; color: #94a3b8;">kg/h</span>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Validated continuous hydrodynamics (14 features)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_m3:
        delta_color = "#10b981" if delta_val < 250.0 else ("#f59e0b" if delta_val < 500.0 else "#ef4444")
        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid {delta_color}; border-radius: 6px; padding: 14px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Discrepancy (Δ_model)</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-top: 2px;">Cross-Check Agreement</div>
                <div style="font-size: 26px; font-weight: 800; color: {delta_color}; margin-top: 6px;">
                    {delta_val:,.2f} <span style="font-size: 13px; color: #94a3b8;">kg/h</span>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                    {'Agreement within acceptable bounds' if delta_val < 500.0 else 'Discrepancy triggers MODEL-REAL-04 fallback'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Conformal Uncertainty & OOD Distance Section
    st.markdown("<h4 style='color: #38bdf8;'>3. Uncertainty Quantification & Operating Domain Membership</h4>", unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown(
            f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px;">
                    Split Conformal Prediction Interval ({int(cov_level*100)}%)
                </div>
                <div style="font-size: 22px; font-weight: 800; color: #34d399; font-family: monospace;">
                    [{unc['lower_bound_kg_h']:,.1f} – {unc['upper_bound_kg_h']:,.1f}] kg/h
                </div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 6px;">
                    Interval Width (MPIW): <strong>{unc['interval_width_kg_h']:,.1f} kg/h</strong>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                    Empirical Calibration: 93.56% coverage on held-out test data (exceeds 90% nominal).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_u2:
        ood_badge = "IN-DOMAIN (Safe)" if env_dist <= 1.0 else ("WARNING (Near Boundary)" if env_dist <= 1.5 else "OUT-OF-DOMAIN (Fallback Engaged)")
        badge_c = "#10b981" if env_dist <= 1.0 else ("#f59e0b" if env_dist <= 1.5 else "#ef4444")
        st.markdown(
            f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px;">
                    Convex Envelope Distance (d_env)
                </div>
                <div style="font-size: 22px; font-weight: 800; color: {badge_c}; font-family: monospace;">
                    d_env = {env_dist:.3f}
                </div>
                <div style="font-size: 12px; color: {badge_c}; font-weight: 600; margin-top: 6px;">
                    Status: {ood_badge}
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                    Thresholds: [0.0 - 1.0] In-Domain | (1.0 - 1.5] Warning | >1.5 OOD Fallback
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Routing Decision Output
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if routing == "NORMAL":
        st.success(f"✔ **ROUTING DECISION: NORMAL** — Operating state is in-domain (d_env={env_dist:.3f}). Serving primary quantum-inspired candidate `{selected_model}`.")
    elif routing == "FALLBACK":
        st.warning(f"⚠ **ROUTING DECISION: FALLBACK** — State requires reference model protection ({res.get('warning', 'Warning state')}). Re-routed to `{selected_model}`.")
    else:
        st.error(f"⛔ **ROUTING DECISION: {routing}** — {res.get('warning', 'Outside operating domain')}. Re-routed to `{selected_model}`.")
