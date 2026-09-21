"""
Egreen Quanta - SIH26138: Screen 9 — Pareto / Trade-Offs.
Multi-objective Pareto frontier visualization (Operational Cost vs Lifecycle GHG).
Inspects non-dominated solutions, highlights compromise boundaries, and enforces objective decision support.
Conforms to Phase 13 of Master UI Requirements:
"Do NOT globally label a point 'BEST'. Use labels such as Lowest Cost, Lowest GHG, Lowest Fuel, Balanced Trade-off."
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_verified_pareto_front, get_verified_tradeoffs, log_audit_event


def render_pareto_tradeoffs():
    """Renders Screen 9 Pareto & Trade-offs."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800;">
                Pareto Frontier & Multi-Objective Trade-Offs
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Trade-off exploration across Cost ($) vs Lifecycle GHG (tCO2e). Demonstrates that no single solution is universally 'best'.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_pareto = get_verified_pareto_front()

    if df_pareto.empty:
        st.error("Verified Pareto frontier dataset not found at results/pareto_front.csv.")
        return

    # Principles Reminder (Phase 13 requirement)
    st.info(
        "💡 **Maritime Decision Principle (Phase 13)**: In multi-objective dispatch, no single point is globally 'best'. "
        "Solutions are classified strictly by specific objective compromises: **Lowest Cost**, **Lowest GHG**, **Lowest Fuel**, or **Balanced Trade-off**."
    )

    # Filter Controls
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        st.markdown("<h4 style='color: #38bdf8;'>Operational Cost ($) vs Lifecycle Well-to-Wake GHG (tCO2e)</h4>", unsafe_allow_html=True)
    with col_f2:
        max_cost = st.slider("Filter Max Cost ($)", min_value=90000, max_value=200000, value=180000, step=5000)

    filtered_df = df_pareto[df_pareto["cost_usd"] <= max_cost].copy()

    # Scatter Chart
    st.scatter_chart(
        filtered_df,
        x="cost_usd",
        y="ghg_tonnes",
        size="fuel_tonnes",
        color="algorithm",
        height=380,
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Classify Non-Biased Labels (Phase 13)
    min_cost_idx = df_pareto["cost_usd"].idxmin()
    min_ghg_idx = df_pareto["ghg_tonnes"].idxmin()
    min_fuel_idx = df_pareto["fuel_tonnes"].idxmin()

    labels_list = []
    for idx, row in df_pareto.iterrows():
        tags = []
        if idx == min_cost_idx:
            tags.append("Lowest Cost")
        if idx == min_ghg_idx:
            tags.append("Lowest GHG")
        if idx == min_fuel_idx:
            tags.append("Lowest Fuel")
        if not tags:
            tags.append("Balanced Trade-off")
        labels_list.append(" / ".join(tags))

    df_pareto_tagged = df_pareto.copy()
    df_pareto_tagged["Classification"] = labels_list

    # Inspect Specific Pareto Solutions
    st.markdown("<h4 style='color: #f8fafc;'>Inspect Non-Dominated Solutions</h4>", unsafe_allow_html=True)

    sol_options = [
        f"Sol #{idx+1}: [{row['Classification']}] Cost=${row['cost_usd']:,.0f}, GHG={row['ghg_tonnes']:.1f}t, Fuel={row['fuel_tonnes']:.1f}t ({row['algorithm']})"
        for idx, row in df_pareto_tagged.iterrows()
    ]
    selected_sol_idx = st.selectbox("Select Solution for Detailed Fleet Inspection:", range(len(sol_options)), format_func=lambda i: sol_options[i])

    sel_row = df_pareto_tagged.iloc[selected_sol_idx]

    # Solution Detail Drawer
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Total Voyage Fuel", f"{sel_row['fuel_tonnes']:.2f} t", delta=f"{sel_row['Classification']}")
    with d2:
        st.metric("Operational Cost", f"${sel_row['cost_usd']:,.2f}", delta="Evaluated OPEX")
    with d3:
        st.metric("Lifecycle GHG", f"{sel_row['ghg_tonnes']:.2f} t CO2e", delta="IMO MEPC.391(81)")
    with d4:
        st.metric("Schedule Delay", f"{sel_row['delay_hours']:.1f} hours", delta="Feasible Schedule" if sel_row['delay_hours'] == 0 else "Demurrage Incurred")

    # Table of verified front with classification tags
    st.markdown("<h4 style='color: #f8fafc; margin-top: 14px;'>Verified Non-Dominated Solutions Ledger</h4>", unsafe_allow_html=True)
    table_display = df_pareto_tagged[["formulation", "algorithm", "Classification", "fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours", "evaluations"]].copy()
    table_display.columns = ["Formulation", "Algorithm", "Objective Classification", "Fuel (t)", "Cost ($)", "WtW GHG (t)", "Delay (h)", "Evaluations"]
    st.dataframe(table_display, use_container_width=True)

    # Action
    if st.button("📌 Adopt Selected Solution as Advisory Recommendation", use_container_width=True):
        st.session_state.active_scenario_name = f"Pareto Sol #{selected_sol_idx+1} ({sel_row['Classification']})"
        log_audit_event(
            action="PARETO_SOLUTION_SELECTED",
            scenario_id=f"PARETO-{selected_sol_idx+1}",
            vessel_id="FLEET_ALL",
            details={
                "solver": sel_row["algorithm"],
                "fuel_prediction": sel_row["fuel_tonnes"],
                "notes": f"Cost ${sel_row['cost_usd']:,.2f}, GHG {sel_row['ghg_tonnes']:.2f} t [{sel_row['Classification']}]",
            },
        )
        st.success(f"Selected Solution #{selected_sol_idx+1} [{sel_row['Classification']}] loaded into active advisory plan.")
