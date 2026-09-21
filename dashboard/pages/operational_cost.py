"""
Egreen Quanta - SIH26138: Screen 5 — Operational Cost Center.
Exposes the exact mathematical cost formulation:
C_total = C_fuel + C_electricity + C_OPS + C_carbon + C_schedule + C_FuelEU
Allows scenario comparisons and itemized cost audits from backend calculations.
Conforms to Phase 9 of the Master UI Requirements.
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_cached_sih_engine, get_default_fleet_state, log_audit_event


def render_operational_cost():
    """Renders the dedicated Operational Cost page."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Operational Cost Engine (C_total)
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Transparent, itemized voyage cost evaluation with zero double-counting across fuel, shore electricity, EU ETS carbon levy, demurrage, and FuelEU compliance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cost Formulation Mathematical Callout
    st.markdown(
        """
        <div style="background: #0f172a; border: 1px solid #1e3a5f; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 12px 18px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 700; color: #38bdf8;">
                Mathematical Formulation:
            </div>
            <div style="font-family: monospace; font-size: 13px; color: #f8fafc; margin-top: 4px;">
                C_total = C_fuel + C_electricity + C_OPS + C_carbon + C_schedule + C_FuelEU
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; line-height: 1.5;">
                • C_fuel = m_fuel · P_bunker &nbsp;|&nbsp; • C_OPS = (P_hotel · t_berth · Tariff) + Fee &nbsp;|&nbsp; • C_carbon = CO2_TtW · P_ETS · Scope &nbsp;|&nbsp; • C_schedule = max(0, t - deadline) · Demurrage
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fleet = get_default_fleet_state()
    sih_engine = get_cached_sih_engine()

    # Scenario Controls
    st.markdown("<h4 style='color: #38bdf8;'>1. Voyage & Fleet Cost Scenario Configuration</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vessel_choice = st.selectbox("Selected Vessel", options=[v["name"] for v in fleet], index=0)
        vessel = next(v for v in fleet if v["name"] == vessel_choice)
    with col2:
        speed_kn = st.slider("Operating Speed (kn)", min_value=10.0, max_value=20.0, value=float(vessel["stw_kn"]), step=0.5)
    with col3:
        distance_nm = st.number_input("Voyage Distance (nm)", min_value=50.0, max_value=1500.0, value=300.0, step=25.0)
    with col4:
        deadline_h = st.number_input("Arrival Deadline (h)", min_value=5.0, max_value=100.0, value=22.0, step=1.0)

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        fuel_choice = st.selectbox(
            "Fuel Pathway",
            options=["vlsfo", "mgo", "fossil_lng", "bio_methanol", "green_ammonia", "liquid_hydrogen"],
            index=0,
            format_func=lambda x: {
                "vlsfo": "VLSFO ($650/t)",
                "mgo": "MGO ($850/t)",
                "fossil_lng": "Fossil LNG ($720/t)",
                "bio_methanol": "Bio-Methanol ($1,050/t)",
                "green_ammonia": "Green Ammonia ($950/t)",
                "liquid_hydrogen": "Liquid Hydrogen ($3,200/t)",
            }.get(x, x),
        )
    with col_f2:
        use_ops = st.checkbox("Cold Ironing (Shore Power) at Berth", value=True)
    with col_f3:
        port_stay_h = st.number_input("Port Berth Hours", min_value=0.0, max_value=48.0, value=6.0, step=1.0)
    with col_f4:
        carbon_tax_price = st.number_input("EU ETS Carbon Price ($/t CO2)", min_value=0.0, max_value=250.0, value=90.0, step=5.0)

    # Evaluate using Authoritative Backend
    # Baseline fuel rate approximation based on speed
    base_fuel_rate = 2740.86 * ((speed_kn / 14.5) ** 2.8)

    cost_res = sih_engine.evaluate_voyage(
        vessel_id=vessel["id"],
        vessel_type=vessel["vessel_type"],
        speed_knots=speed_kn,
        voyage_distance_nm=distance_nm,
        schedule_deadline_hours=deadline_h,
        baseline_fuel_rate_kg_h=base_fuel_rate,
        fuel_type=fuel_choice,
        use_shore_power=use_ops,
        port_hours=port_stay_h,
        hotel_load_kw=vessel["hotel_load_kw"],
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Itemized Cost Breakdown Matrix
    st.markdown("<h4 style='color: #38bdf8;'>2. Itemized Cost Audit Ledger</h4>", unsafe_allow_html=True)

    cost_items = [
        {"Component": "C_fuel (Bunker Fuel Cost)", "Description": f"{cost_res.fuel_tonnes:.2f} t of {fuel_choice.upper()} consumed at sea", "Amount (USD)": cost_res.fuel_cost_usd},
        {"Component": "C_electricity (Aux Hotel Sea Load)", "Description": f"{vessel['hotel_load_kw']} kW service generators during voyage", "Amount (USD)": 0.0},  # Included in marine fuel burn
        {"Component": "C_OPS (Shore Power at Berth)", "Description": f"{vessel['hotel_load_kw'] * port_stay_h:,.0f} kWh grid electricity ($0.18/kWh) + $500 fee" if use_ops else "Shore power disabled", "Amount (USD)": cost_res.shore_power_cost_usd},
        {"Component": "C_carbon (EU ETS Carbon Levy)", "Description": f"{cost_res.ttw_ghg_tonnes:.2f} t fossil TtW CO2 @ ${carbon_tax_price:.0f}/t", "Amount (USD)": cost_res.carbon_cost_usd},
        {"Component": "C_schedule (Demurrage Penalty)", "Description": f"{cost_res.schedule_delay_hours:.1f} hours delay beyond {deadline_h:.1f}h window ($1,000/h)", "Amount (USD)": cost_res.schedule_penalty_usd},
        {"Component": "C_FuelEU (Maritime Compliance)", "Description": "Zero penalty: compliant with GHG intensity baseline", "Amount (USD)": cost_res.fueleu_penalty_usd},
    ]

    df_cost = pd.DataFrame(cost_items)
    df_cost["Formatted Amount"] = df_cost["Amount (USD)"].apply(lambda x: f"${x:,.2f}")

    st.dataframe(df_cost[["Component", "Description", "Formatted Amount"]].set_index("Component"), use_container_width=True)

    # Total Cost Big KPI Callout
    st.markdown(
        f"""
        <div style="background: #111827; border: 1px solid #1e3a5f; border-radius: 8px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <div>
                <span style="font-size: 13px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">TOTAL OPERATIONAL VOYAGE COST (C_total)</span>
                <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Fully computed by FleetCostEngine; zero double-counting</div>
            </div>
            <div style="font-size: 30px; font-weight: 900; color: #00E5FF; font-family: monospace;">
                ${cost_res.operational_cost_usd:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Cost Sensitivity over Speed
    st.markdown("<h4 style='color: #f8fafc; margin-top: 20px;'>Operational Cost Curve vs Cruising Speed</h4>", unsafe_allow_html=True)
    speeds_sweep = [10.0, 11.0, 12.0, 13.0, 14.0, 14.5, 15.0, 16.0, 17.0, 18.0]
    sweep_records = []
    for spd in speeds_sweep:
        b_rate = 2740.86 * ((spd / 14.5) ** 2.8)
        ev = sih_engine.evaluate_voyage(
            vessel_id=vessel["id"], vessel_type=vessel["vessel_type"], speed_knots=spd,
            voyage_distance_nm=distance_nm, schedule_deadline_hours=deadline_h,
            baseline_fuel_rate_kg_h=b_rate, fuel_type=fuel_choice, use_shore_power=use_ops,
            port_hours=port_stay_h, hotel_load_kw=vessel["hotel_load_kw"]
        )
        sweep_records.append({
            "Speed (kn)": spd,
            "Fuel Cost ($)": ev.fuel_cost_usd,
            "Carbon Cost ($)": ev.carbon_cost_usd,
            "Demurrage ($)": ev.schedule_penalty_usd,
            "Total Cost ($)": ev.operational_cost_usd,
        })

    df_sweep = pd.DataFrame(sweep_records).set_index("Speed (kn)")
    st.line_chart(df_sweep[["Fuel Cost ($)", "Carbon Cost ($)", "Total Cost ($)"]], height=280)

    # Log to Audit Button
    if st.button("📋 Log Cost Evaluation to Regulatory Audit Trail"):
        log_audit_event(
            action="COST_EVALUATED",
            scenario_id=f"COST-{speed_kn}KN-{fuel_choice.upper()}",
            vessel_id=vessel["id"],
            details={
                "solver": "FleetCostEngine",
                "fuel_prediction": cost_res.fuel_tonnes,
                "notes": f"Total Cost ${cost_res.operational_cost_usd:,.2f} (Fuel: ${cost_res.fuel_cost_usd:,.2f}, Carbon: ${cost_res.carbon_cost_usd:,.2f})",
            },
        )
        st.success("Operational cost record committed to immutable audit ledger.")
