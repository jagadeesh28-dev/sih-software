"""
Egreen Quanta - SIH26138: Screen 6 — Pareto / Trade-Offs.
Multi-objective Pareto frontier visualization (Operational Cost vs Lifecycle GHG).
Inspects non-dominated solutions, highlights compromise boundaries, and enforces objective decision support.
Conforms to Section 10 of Operator UI Master Requirements:
"Never call one point 'best' without defining the decision criterion."
"""

import pandas as pd
import streamlit as st

from dashboard.backend_bridge import get_verified_pareto_front, get_verified_tradeoffs, log_audit_event


def render_pareto_tradeoffs():
    """Renders Screen 6 Pareto & Trade-offs."""
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
    df_tradeoffs = get_verified_tradeoffs()

    if df_pareto.empty:
        st.error("Verified Pareto frontier dataset not found at results/pareto_front.csv.")
        return

    # Principles Reminder (Section 10 requirement)
    st.info(
        "💡 **Maritime Superintendent Principle**: In multi-objective dispatch, there is no single 'best' solution. "
        "Each Pareto point represents a non-dominated trade-off where reducing GHG requires alternative fuel investment, "
        "and minimizing fuel requires strict operational slow-steaming."
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

    # Inspect Specific Pareto Solutions
    st.markdown("<h4 style='color: #f8fafc;'>Inspect Non-Dominated Solutions</h4>", unsafe_allow_html=True)

    sol_options = [f"Solution #{idx+1}: {row['formulation']} (Cost=${row['cost_usd']:,.0f}, GHG={row['ghg_tonnes']:.1f}t)" for idx, row in df_pareto.iterrows()]
    selected_sol_idx = st.selectbox("Select Solution for Detailed Fleet Inspection:", range(len(sol_options)), format_func=lambda i: sol_options[i])

    sel_row = df_pareto.iloc[selected_sol_idx]

    # Solution Detail Drawer
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Total Voyage Fuel", f"{sel_row['fuel_tonnes']:.2f} t", delta=f"{sel_row['algorithm']} formulation")
    with d2:
        st.metric("Operational Cost", f"${sel_row['cost_usd']:,.2f}", delta="No double counting")
    with d3:
        st.metric("Lifecycle GHG", f"{sel_row['ghg_tonnes']:.2f} t CO2e", delta="MEPC.391(81)")
    with d4:
        st.metric("Schedule Delay", f"{sel_row['delay_hours']:.1f} hours", delta="Feasible Schedule" if sel_row['delay_hours'] == 0 else "Demurrage Incurred")

    # Table of verified front
    st.markdown("<h4 style='color: #f8fafc; margin-top: 14px;'>Verified Non-Dominated Solutions Table</h4>", unsafe_allow_html=True)
    table_display = df_pareto[["formulation", "algorithm", "seed", "fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours", "evaluations"]].copy()
    table_display.columns = ["Formulation", "Algorithm", "Seed", "Fuel (t)", "Cost ($)", "WtW GHG (t)", "Delay (h)", "Evaluations"]
    st.dataframe(table_display, use_container_width=True)

    # Action
    if st.button("📌 Adopt Selected Solution as Advisory Recommendation", use_container_width=True):
        st.session_state.active_scenario_name = f"Pareto Sol #{selected_sol_idx+1} ({sel_row['formulation']})"
        log_audit_event(
            action="PARETO_SOLUTION_SELECTED",
            scenario_id=f"PARETO-{selected_sol_idx+1}",
            vessel_id="FLEET_ALL",
            details={
                "solver": sel_row["algorithm"],
                "fuel_prediction": sel_row["fuel_tonnes"],
                "notes": f"Cost ${sel_row['cost_usd']:,.2f}, GHG {sel_row['ghg_tonnes']:.2f} t",
            },
        )
        st.success(f"Selected Solution #{selected_sol_idx+1} loaded into active fleet scenario.")
