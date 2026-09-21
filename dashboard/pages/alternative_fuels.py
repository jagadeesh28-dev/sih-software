"""
Egreen Quanta - SIH26138: Screen 7 — Alternative Fuels & Shore Power.
Evaluates future green fuel candidates (Bio-Methanol, Green Ammonia, Liquid H2, Fossil LNG)
and Onshore Power Supply (OPS) cold ironing.
Enforces mandatory labeling conforming to Section 11 of Operator UI Master Requirements:
"SCENARIO ESTIMATE — not measured green-fuel telemetry."
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_cached_sih_engine, get_default_fleet_state


def render_alternative_fuels():
    """Renders Screen 7 Alternative Fuels."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Alternative Marine Fuels & Decarbonization
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Thermodynamic invariant shaft work modeling and IMO MEPC.391(81) Well-to-Wake lifecycle emission accounting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mandatory Regulatory Banner (Section 11)
    st.markdown(
        """
        <div style="
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid #dc2626;
            border-radius: 6px;
            padding: 12px 18px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 20px;">⚠️</span>
            <div>
                <div style="font-size: 13px; font-weight: 800; color: #f87171; letter-spacing: 0.5px;">
                    MANDATORY EPISTEMIC BOUNDARY: SCENARIO ESTIMATE — NOT MEASURED GREEN-FUEL TELEMETRY
                </div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 2px;">
                    Alternative fuel consumptions are derived strictly from certified Lower Heating Values (LHV) on an invariant shaft work basis (E = P_B * t). Telemetry from commercial vessels is measured in VLSFO/MGO.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sih_engine = get_cached_sih_engine()
    fleet = get_default_fleet_state()

    # Evaluation Scenario Controls
    col_v, col_dist, col_spd, col_port = st.columns(4)
    with col_v:
        v_choice = st.selectbox("Test Vessel", options=[v["name"] for v in fleet], index=0)
        vessel = next(v for v in fleet if v["name"] == v_choice)
    with col_dist:
        voy_dist = st.number_input("Voyage Distance (nm)", min_value=50.0, max_value=2000.0, value=250.0, step=25.0)
    with col_spd:
        voy_spd = st.slider("Cruising Speed (kn)", min_value=10.0, max_value=20.0, value=14.0, step=0.5)
    with col_port:
        port_hrs = st.number_input("Berth Port Stay (hours)", min_value=1.0, max_value=48.0, value=6.0, step=1.0)

    # Evaluate all 6 pathways
    fuel_candidates = [
        ("vlsfo", "VLSFO Conventional", 650.0, False, "MEASURED TELEMETRY"),
        ("mgo", "MGO Marine Gas Oil", 850.0, False, "MEASURED TELEMETRY"),
        ("fossil_lng", "Fossil LNG (+Slip)", 720.0, True, "SCENARIO ESTIMATE"),
        ("bio_methanol", "Bio-Methanol (E-Fuel)", 1050.0, True, "SCENARIO ESTIMATE"),
        ("green_ammonia", "Green Ammonia (Zero-C)", 950.0, True, "SCENARIO ESTIMATE"),
        ("liquid_hydrogen", "Liquid Hydrogen", 3200.0, True, "SCENARIO ESTIMATE"),
    ]

    results_data = []
    chart_rows = []

    for f_code, f_name, price, shore_pwr, status_lbl in fuel_candidates:
        eval_res = sih_engine.evaluate_voyage(
            vessel_id=vessel["id"],
            vessel_type=vessel["vessel_type"],
            speed_knots=voy_spd,
            voyage_distance_nm=voy_dist,
            schedule_deadline_hours=(voy_dist / voy_spd) + 2.0,
            baseline_fuel_rate_kg_h=2500.0,
            fuel_type=f_code,
            use_shore_power=shore_pwr,
            port_hours=port_hrs,
            hotel_load_kw=vessel["hotel_load_kw"],
        )

        results_data.append({
            "Fuel Pathway": f_name,
            "Price ($/t)": f"${price:,.0f}",
            "Fuel Mass (t)": f"{eval_res.fuel_tonnes:.2f} t",
            "Well-to-Tank (t)": f"{eval_res.wtt_ghg_tonnes:.2f} t",
            "Tank-to-Wake (t)": f"{eval_res.ttw_ghg_tonnes:.2f} t",
            "Methane Slip (t)": f"{eval_res.methane_slip_tonnes:.2f} t",
            "Total WtW GHG": f"{eval_res.lifecycle_ghg_tonnes:.2f} t CO2e",
            "Voyage OPEX ($)": f"${eval_res.operational_cost_usd:,.2f}",
            "Epistemic Status": status_lbl,
        })

        chart_rows.append({
            "Fuel Pathway": f_name.split()[0],
            "Well-to-Tank (Upstream)": eval_res.wtt_ghg_tonnes,
            "Tank-to-Wake (Combustion)": eval_res.ttw_ghg_tonnes,
            "Methane Slip": eval_res.methane_slip_tonnes,
        })

    # Display Breakdown Table
    st.markdown("<h4 style='color: #38bdf8;'>Lifecycle Emissions & Cost Matrix (IMO MEPC.391(81))</h4>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(results_data).set_index("Fuel Pathway"), use_container_width=True)

    # Lifecycle Emissions Decomposition Chart
    st.markdown("<h4 style='color: #f8fafc; margin-top: 14px;'>Well-to-Wake Emissions Decomposition (t CO2e)</h4>", unsafe_allow_html=True)
    df_chart = pd.DataFrame(chart_rows).set_index("Fuel Pathway")
    st.bar_chart(df_chart, height=300)

    # Shore Power (OPS) Analysis Callout
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background: #0f172a; border: 1px solid #1e3a5f; border-radius: 6px; padding: 14px 18px;">
            <div style="font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 6px;">
                ⚡ Onshore Power Supply (OPS / Cold Ironing) at Berth
            </div>
            <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
                For <strong>{vessel['name']}</strong> during a {port_hrs:.1f}h berth stay ({vessel['hotel_load_kw']:.0f} kW auxiliary load):
                <ul style="margin: 4px 0 0 0; padding-left: 20px;">
                    <li>Auxiliary Electricity Consumption: <strong>{vessel['hotel_load_kw'] * port_hrs:,.0f} kWh</strong></li>
                    <li>Port OPS Tariff: <strong>$0.18 / kWh</strong> + $500 connection fee = <strong>${(vessel['hotel_load_kw'] * port_hrs * 0.18) + 500:,.2f}</strong></li>
                    <li>Harbor Air Quality: Eliminates 100% of auxiliary diesel NOx, SOx, and direct PM2.5 in port.</li>
                    <li>Grid Upstream Factor: 450 g CO2e / kWh (European average grid mix).</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
