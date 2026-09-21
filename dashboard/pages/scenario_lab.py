"""
Egreen Quanta - SIH26138: Screen 4 — Scenario Lab.
What-if operating/fuel/weather scenario generator and side-by-side evaluator.
Exposes assumptions, fuel prices, emission factors, and explicit [MEASURED] vs [ASSUMED] badges.
Conforms to Section 8 of Operator UI Master Requirements.
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_cached_predictor, get_cached_sih_engine, get_default_fleet_state, log_audit_event


def render_scenario_lab():
    """Renders Screen 4 Scenario Lab."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Voyage & Scenario Lab
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Evaluate operating trade-offs, slow-steaming scenarios, alternative marine fuels, and shore-power assignments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fleet = get_default_fleet_state()
    predictor = get_cached_predictor()
    sih_engine = get_cached_sih_engine()

    # Step 1: Vessel & Route Baseline Selection
    col_v, col_dist, col_dead = st.columns(3)
    with col_v:
        v_choice = st.selectbox("Operating Vessel", options=[v["name"] for v in fleet], index=0)
        vessel = next(v for v in fleet if v["name"] == v_choice)
    with col_dist:
        voyage_distance_nm = st.number_input("Voyage Distance (nm)", min_value=50.0, max_value=2000.0, value=300.0, step=25.0)
    with col_dead:
        deadline_hours = st.number_input("Laytime Deadline (hours)", min_value=5.0, max_value=200.0, value=22.0, step=1.0)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Step 2: What-If Controls (2 Columns: Baseline vs Scenario)
    st.markdown("<h4 style='color: #38bdf8;'>Configure What-If Operational Scenario</h4>", unsafe_allow_html=True)
    
    col_base, col_scen = st.columns(2)

    with col_base:
        st.markdown(
            """
            <div style="background: #111827; border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 12px;">
                <span style="font-size: 11px; background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-weight: 700;">
                    [MEASURED TELEMETRY]
                </span>
                <span style="font-weight: 700; color: #f8fafc; font-size: 14px; margin-left: 8px;">Baseline Condition</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        base_speed = float(vessel["stw_kn"])
        base_draft = float(vessel["draft_m"])
        base_fuel = "vlsfo"
        base_shore = False
        st.write(f"**Speed:** {base_speed:.1f} kn (Current Telemetry)")
        st.write(f"**Draft:** {base_draft:.2f} m (Current Loading)")
        st.write(f"**Bunker Fuel:** Conventional VLSFO ($650/t)")
        st.write(f"**Shore Power at Berth:** Unavailable / Disabled")
        st.write(f"**Weather:** Measured Hs = {vessel['wave_height_m']} m, Depth = {vessel['water_depth_m']} m")

    with col_scen:
        st.markdown(
            """
            <div style="background: #111827; border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 12px;">
                <span style="font-size: 11px; background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-weight: 700;">
                    [OPERATIONAL ASSUMPTION]
                </span>
                <span style="font-weight: 700; color: #f8fafc; font-size: 14px; margin-left: 8px;">Simulated Scenario</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        scen_speed = st.slider("Scenario Speed (kn)", min_value=10.0, max_value=20.0, value=13.5, step=0.5)
        scen_draft = st.slider("Scenario Draft (m)", min_value=3.0, max_value=10.0, value=base_draft, step=0.2)
        scen_fuel = st.selectbox(
            "Scenario Fuel Pathway",
            options=["vlsfo", "mgo", "fossil_lng", "bio_methanol", "green_ammonia", "liquid_hydrogen"],
            index=3,  # Bio-Methanol default
            format_func=lambda x: {
                "vlsfo": "VLSFO Conventional ($650/t)",
                "mgo": "MGO Low Sulfur ($850/t)",
                "fossil_lng": "Fossil LNG ($720/t + Slip)",
                "bio_methanol": "Bio-Methanol E-Fuel ($1,050/t - Green)",
                "green_ammonia": "Green Ammonia Zero-C ($950/t)",
                "liquid_hydrogen": "Liquid Hydrogen ($3,200/t)",
            }.get(x, x),
        )
        scen_shore = st.checkbox("Enable Shore Power (Cold Ironing) at Berth", value=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Compute Predictions & Voyage Evaluations
    # Baseline Prediction
    b_pred_res = predictor.predict_fuel_with_uncertainty({
        "vessel_id": vessel["id"],
        "vessel_type": vessel["vessel_type"],
        "fuel_type": base_fuel,
        "stw_kn": base_speed,
        "sog_kn": base_speed,
        "draft_m": base_draft,
        "displacement_t": vessel["displacement_t"],
        "wind_speed_ms": vessel["wind_speed_ms"],
        "wave_height_m": vessel["wave_height_m"],
        "water_depth_m": vessel["water_depth_m"],
    })

    # Scenario Prediction
    s_pred_res = predictor.predict_fuel_with_uncertainty({
        "vessel_id": vessel["id"],
        "vessel_type": vessel["vessel_type"],
        "fuel_type": "vlsfo",  # Predictor baseline is calibrated in VLSFO equivalent
        "stw_kn": scen_speed,
        "sog_kn": scen_speed,
        "draft_m": scen_draft,
        "displacement_t": vessel["displacement_t"],
        "wind_speed_ms": vessel["wind_speed_ms"],
        "wave_height_m": vessel["wave_height_m"],
        "water_depth_m": vessel["water_depth_m"],
    })

    b_eval = sih_engine.evaluate_voyage(
        vessel_id=vessel["id"],
        vessel_type=vessel["vessel_type"],
        speed_knots=base_speed,
        voyage_distance_nm=voyage_distance_nm,
        schedule_deadline_hours=deadline_hours,
        baseline_fuel_rate_kg_h=b_pred_res["fuel_prediction"],
        fuel_type=base_fuel,
        use_shore_power=base_shore,
        port_hours=6.0,
        hotel_load_kw=vessel["hotel_load_kw"],
    )

    s_eval = sih_engine.evaluate_voyage(
        vessel_id=vessel["id"],
        vessel_type=vessel["vessel_type"],
        speed_knots=scen_speed,
        voyage_distance_nm=voyage_distance_nm,
        schedule_deadline_hours=deadline_hours,
        baseline_fuel_rate_kg_h=s_pred_res["fuel_prediction"],
        fuel_type=scen_fuel,
        use_shore_power=scen_shore,
        port_hours=6.0,
        hotel_load_kw=vessel["hotel_load_kw"],
    )

    # Mandatory Notice for Alternative Fuel Scenarios
    if scen_fuel != "vlsfo" and scen_fuel != "mgo":
        st.warning("⚠️ **SCENARIO ESTIMATE — not measured green-fuel telemetry.** Thermodynamic invariant shaft work model applied.")

    # Side-by-Side Comparison Matrix
    st.markdown("<h4 style='color: #f8fafc;'>Side-by-Side Scenario Comparison</h4>", unsafe_allow_html=True)
    
    comp_df = pd.DataFrame([
        {
            "Metric": "Voyage Duration",
            "Unit": "hours",
            "Baseline": f"{voyage_distance_nm / base_speed:.1f} h",
            "Scenario": f"{voyage_distance_nm / scen_speed:.1f} h",
            "Delta": f"{(voyage_distance_nm / scen_speed) - (voyage_distance_nm / base_speed):+.1f} h",
        },
        {
            "Metric": "Fuel Consumption",
            "Unit": "tonnes",
            "Baseline": f"{b_eval.fuel_tonnes:.2f} t",
            "Scenario": f"{s_eval.fuel_tonnes:.2f} t",
            "Delta": f"{s_eval.fuel_tonnes - b_eval.fuel_tonnes:+.2f} t",
        },
        {
            "Metric": "Total Operational Cost",
            "Unit": "USD ($)",
            "Baseline": f"${b_eval.operational_cost_usd:,.2f}",
            "Scenario": f"${s_eval.operational_cost_usd:,.2f}",
            "Delta": f"${s_eval.operational_cost_usd - b_eval.operational_cost_usd:+,.2f}",
        },
        {
            "Metric": "Lifecycle WtW GHG",
            "Unit": "t CO2e",
            "Baseline": f"{b_eval.lifecycle_ghg_tonnes:.2f} t",
            "Scenario": f"{s_eval.lifecycle_ghg_tonnes:.2f} t",
            "Delta": f"{s_eval.lifecycle_ghg_tonnes - b_eval.lifecycle_ghg_tonnes:+.2f} t ({((s_eval.lifecycle_ghg_tonnes - b_eval.lifecycle_ghg_tonnes)/b_eval.lifecycle_ghg_tonnes)*100:+.1f}%)",
        },
        {
            "Metric": "Laytime Arrival Delay",
            "Unit": "hours",
            "Baseline": f"{b_eval.schedule_delay_hours:.1f} h",
            "Scenario": f"{s_eval.schedule_delay_hours:.1f} h",
            "Delta": f"{s_eval.schedule_delay_hours - b_eval.schedule_delay_hours:+.1f} h",
        },
    ]).set_index("Metric")

    st.table(comp_df)

    # Action Buttons
    col_act1, col_act2 = st.columns([1, 4])
    with col_act1:
        if st.button("📋 Log Scenario to Audit", use_container_width=True):
            log_audit_event(
                action="SCENARIO_EVALUATED",
                scenario_id=f"SCEN-{scen_speed}KN-{scen_fuel.upper()}",
                vessel_id=vessel["id"],
                details={
                    "model_version": s_pred_res["model_version"],
                    "fuel_prediction": s_pred_res["fuel_prediction"],
                    "uncertainty_interval": f"[{s_pred_res['uncertainty']['lower_bound_kg_h']:.1f}, {s_pred_res['uncertainty']['upper_bound_kg_h']:.1f}]",
                    "ood_state": s_pred_res["routing_status"],
                    "notes": f"Speed {scen_speed} kn, Fuel {scen_fuel}, Shore Power {scen_shore}",
                },
            )
            st.success("Scenario parameters successfully committed to immutable audit ledger.")
