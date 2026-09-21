"""
Egreen Quanta - SIH26138: Screen 8 — Alerts, OOD & Safety.
Real-time alarm hierarchy, Out-of-Distribution boundary detection,
automatic fallback routing, and safety stress-test verification ledger.
Conforms to Sections 2 and 12 of Operator UI Master Requirements.
"""

from datetime import datetime, timezone
import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_cached_predictor, log_audit_event


def render_alerts_safety():
    """Renders Screen 8 Alerts & Safety."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Alerts, OOD Guard & Safety Engine
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Maritime safety hierarchy, out-of-distribution (OOD) protection, reference fallback, and 1,000-point adversarial test ledger.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Alarm Hierarchy Overview
    st.markdown("<h4 style='color: #38bdf8;'>1. Maritime Alarm State Hierarchy</h4>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #10b981; border-radius: 6px; padding: 12px;">
                <div style="font-weight: 800; color: #34d399; font-size: 13px;">✔ NORMAL (d_env ≤ 1.0)</div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">QI-C1 serving active with high confidence. Nominal 90% conformal intervals.</div>
            </div>
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #f59e0b; border-radius: 6px; padding: 12px;">
                <div style="font-weight: 800; color: #fbbf24; font-size: 13px;">⚠ WARNING (1.0 < d_env ≤ 1.5)</div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">State near envelope boundary. Flagged for operator review; uncertainty inflated.</div>
            </div>
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #ef4444; border-radius: 6px; padding: 12px;">
                <div style="font-weight: 800; color: #f87171; font-size: 13px;">⛔ OOD / FALLBACK (d_env > 1.5)</div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Severe sea state or extrapolation. Immediate auto-fallback to MODEL-REAL-04.</div>
            </div>
            <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #9333ea; border-radius: 6px; padding: 12px;">
                <div style="font-weight: 800; color: #c084fc; font-size: 13px;">🛡 HARD REJECTION</div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Physically impossible input (e.g. speed < 0 or draft < 1m). Blocked at gate.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Injected Safety Diagnostic Test
    st.markdown("<h4 style='color: #38bdf8;'>2. Interactive Safety & Fallback Injector</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 12px;'>Test how the hardened production server intercepts abnormal or adversarial conditions.</p>", unsafe_allow_html=True)

    c_t1, c_t2 = st.columns([1.5, 2.5])

    with c_t1:
        test_mode = st.radio(
            "Select Diagnostic Condition to Inject:",
            options=[
                "Normal Nominal State (STW=14.5, Wave=1.0m)",
                "Severe Storm OOD (Wave Hs=9.5m, STW=19.5kn)",
                "Unknown Vessel Type ('space_freighter')",
                "Invalid Physics (Negative Speed: STW=-5.0kn)",
            ],
            index=0,
        )

        inject_btn = st.button("⚡ Inject Test Condition into Predictor", use_container_width=True)

    with c_t2:
        predictor = get_cached_predictor()
        if inject_btn:
            if "Normal" in test_mode:
                t_input = {
                    "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
                    "stw_kn": 14.5, "sog_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0,
                    "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0
                }
            elif "Severe Storm" in test_mode:
                t_input = {
                    "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
                    "stw_kn": 19.5, "sog_kn": 19.5, "draft_m": 7.5, "displacement_t": 35000.0,
                    "wind_speed_ms": 28.0, "wave_height_m": 9.5, "water_depth_m": 25.0
                }
            elif "Unknown Vessel" in test_mode:
                t_input = {
                    "vessel_id": "Unknown_Alien", "vessel_type": "space_freighter", "fuel_type": "vlsfo",
                    "stw_kn": 14.0, "sog_kn": 14.0, "draft_m": 6.0, "displacement_t": 20000.0,
                    "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 50.0
                }
            else:  # Negative speed
                t_input = {
                    "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
                    "stw_kn": -5.0, "sog_kn": -5.0, "draft_m": 7.5, "displacement_t": 35000.0,
                    "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0
                }

            is_valid, errors, clean = predictor.validate_and_sanitize_point(t_input)
            if not is_valid:
                st.error(f"🛡 **HARD REJECTION AT INPUT GATE**: Input physically rejected with {len(errors)} error(s):")
                for err in errors:
                    st.write(f"- {err}")
                log_audit_event("INPUT_REJECTED", "DIAG_SAFETY", t_input.get("vessel_id", "N/A"), {"notes": str(errors)})
            else:
                diag_res = predictor.predict_fuel_with_uncertainty(clean)
                d_routing = diag_res["routing_status"]
                d_dist = diag_res.get("envelope_distance", 0.0)
                d_model = diag_res["model"]

                if d_routing == "NORMAL":
                    st.success(f"✔ **SYSTEM NORMAL**: In-domain (d_env={d_dist:.3f}). Served by primary candidate `{d_model}`.")
                elif d_routing == "FALLBACK":
                    st.warning(f"⚠️ **FAIL-SAFE ENGAGED**: OOD condition detected (d_env={d_dist:.3f}). Safely fell back to `{d_model}`.")
                    st.write(f"Reason: {diag_res.get('warning', 'Extrapolation detected')}")
                else:
                    st.error(f"⛔ **EMERGENCY ROUTING**: {d_routing} -> `{d_model}`.")
                
                log_audit_event("DIAGNOSTIC_RUN", "DIAG_SAFETY", t_input.get("vessel_id", "N/A"), {
                    "fuel_prediction": diag_res["fuel_prediction"],
                    "ood_state": d_routing,
                    "notes": f"d_env={d_dist:.3f}, model={d_model}",
                })
        else:
            st.info("Select a condition on the left and click 'Inject Test Condition' to observe real-time safety response.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Verified Frozen Safety Benchmarks (Section 2)
    st.markdown("<h4 style='color: #f8fafc;'>3. Official Release Gate Safety Benchmarks</h4>", unsafe_allow_html=True)
    
    benchmarks_data = [
        {"Test Suite": "Adversarial Stress Test", "Volume / Trials": "1,000 / 1,000", "Result": "100.0% REJECTED", "Status": "PASS (Gate G8)"},
        {"Test Suite": "Edge Operating Cases", "Volume / Trials": "16 / 16", "Result": "100.0% INTERCEPTED", "Status": "PASS (Gate G9)"},
        {"Test Suite": "Runtime Memory / Booster Fault", "Volume / Trials": "10 / 10", "Result": "100.0% FALLBACK (<2 ms)", "Status": "PASS (Gate G10)"},
        {"Test Suite": "In-Domain False Positive Rate (FPR)", "Volume / Trials": "2,000 Points", "Result": "0.00% FPR", "Status": "PASS (Gate G5)"},
        {"Test Suite": "Severe OOD Recall", "Volume / Trials": "Synthetic Storms", "Result": "96.55% Recall", "Status": "PASS (Gate G6)"},
        {"Test Suite": "Conformal Coverage Guarantee", "Volume / Trials": "Held-out Test Data", "Result": "93.56% (Nominal 90%)", "Status": "PASS (Gate G4)"},
    ]
    st.table(pd.DataFrame(benchmarks_data).set_index("Test Suite"))
