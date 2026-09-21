"""
Egreen Quanta — SIH26138: Operator UI / HMI Master Application.
Maritime Decision-Support Platform for Quantum-Inspired Fuel Prediction
and Green Fleet Multi-Objective Optimization.

Conforms to all 20 Phases of Master UI Requirements:
- 12 Dedicated Screens following primary operator decision flow.
- Exposes verified backend calculations and frozen models (QI-C1, MODEL-REAL-04).
- Zero autonomous control: strictly human-in-the-loop advisory decision support.
- Mandatory labeling on alternative fuels: SCENARIO ESTIMATE.
- Professional high-contrast maritime engineering aesthetic.
"""

import sys
from pathlib import Path
import streamlit as st

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.components.top_bar import render_top_bar
from dashboard.components.status_strip import render_status_strip
from dashboard.pages.fleet_overview import render_fleet_overview
from dashboard.pages.vessel_detail import render_vessel_detail
from dashboard.pages.prediction_trust import render_prediction_trust
from dashboard.pages.scenario_lab import render_scenario_lab
from dashboard.pages.operational_cost import render_operational_cost
from dashboard.pages.lifecycle_ghg import render_lifecycle_ghg
from dashboard.pages.alternative_fuels import render_alternative_fuels
from dashboard.pages.fleet_optimizer import render_fleet_optimizer
from dashboard.pages.pareto_tradeoffs import render_pareto_tradeoffs
from dashboard.pages.alerts_safety import render_alerts_safety
from dashboard.pages.audit_reports import render_audit_reports
from dashboard.pages.demo_mode import render_demo_mode


# Configure Streamlit Page
st.set_page_config(
    page_title="Egreen Quanta — SIH26138 Maritime Operator HMI",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Aesthetic Maritime Engineering Dark Theme CSS
st.markdown(
    """
    <style>
        /* Base Dark Maritime Theme */
        .stApp {
            background-color: #080d1a;
            color: #f1f5f9;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0d1527;
            border-right: 1px solid #1e293b;
        }

        /* Sidebar Navigation Radio */
        [data-testid="stSidebar"] .stRadio label {
            color: #cbd5e1 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 6px 10px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(56, 189, 248, 0.1) !important;
            color: #38bdf8 !important;
        }

        /* Inputs and Selects */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #0f172a !important;
            border-color: #334155 !important;
            color: #f8fafc !important;
        }
        .stSlider {
            padding-top: 6px;
            padding-bottom: 6px;
        }

        /* Primary Action Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.2s ease;
        }
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: 1px solid #38bdf8;
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
        }
        .stButton>button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
            border-color: #00E5FF;
            box-shadow: 0 4px 12px rgba(0, 229, 255, 0.4);
        }

        /* Tables and Dataframes */
        [data-testid="stTable"] table {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            color: #e2e8f0;
            font-size: 12px;
        }
        [data-testid="stTable"] th {
            background-color: #1e293b;
            color: #94a3b8;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }

        /* Metric card styling */
        [data-testid="stMetricValue"] {
            color: #00E5FF !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            font-weight: 600 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    # Persistent Session State Initialization
    if "current_page" not in st.session_state:
        st.session_state.current_page = "1. Fleet Command Center"
    if "system_mode" not in st.session_state:
        st.session_state.system_mode = "LIVE"
    if "audit_ledger" not in st.session_state:
        st.session_state.audit_ledger = []
    if "last_recommendation_status" not in st.session_state:
        st.session_state.last_recommendation_status = "ADVISORY READY — Awaiting Operator Confirmation"

    # Render Persistent Global Top Bar
    render_top_bar()

    # Left Navigation Sidebar (12 Dedicated Screens in Primary Operator Flow)
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1e293b; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 24px;">⚓</span>
                    <div>
                        <div style="font-size: 15px; font-weight: 800; color: #00E5FF; letter-spacing: 1px;">
                            EGREEN QUANTA
                        </div>
                        <div style="font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
                            Maritime Operator HMI
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_pages = [
            "1. Fleet Command Center",
            "2. Vessel Intelligence",
            "3. Prediction & Trust",
            "4. Scenario Lab",
            "5. Operational Cost",
            "6. Lifecycle GHG",
            "7. Alternative Fuels",
            "8. Fleet Optimizer",
            "9. Pareto / Trade-offs",
            "10. Alerts & Safety",
            "11. Audit / Reports",
            "12. Demo Center",
        ]

        # Determine current index
        clean_current = st.session_state.current_page
        matching_idx = 0
        for i, p_title in enumerate(nav_pages):
            if clean_current in p_title or p_title.endswith(clean_current) or p_title == clean_current:
                matching_idx = i
                break

        selected_nav = st.radio(
            "OPERATOR WORKSPACE",
            options=nav_pages,
            index=matching_idx,
            label_visibility="visible",
        )

        st.session_state.current_page = selected_nav

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: #090e1a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px; font-size: 11px; color: #64748b;">
                <strong style="color: #94a3b8;">Human-in-the-Loop Protocol:</strong><br>
                This platform is an advisory decision-support layer. Autonomous vessel or engine actuation is strictly prohibited.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Route to Appropriate Screen
    page = st.session_state.current_page

    if "Fleet Command Center" in page:
        render_fleet_overview()
    elif "Vessel Intelligence" in page:
        render_vessel_detail()
    elif "Prediction & Trust" in page:
        render_prediction_trust()
    elif "Scenario Lab" in page:
        render_scenario_lab()
    elif "Operational Cost" in page:
        render_operational_cost()
    elif "Lifecycle GHG" in page:
        render_lifecycle_ghg()
    elif "Alternative Fuels" in page:
        render_alternative_fuels()
    elif "Fleet Optimizer" in page:
        render_fleet_optimizer()
    elif "Pareto" in page:
        render_pareto_tradeoffs()
    elif "Alerts & Safety" in page:
        render_alerts_safety()
    elif "Audit / Reports" in page:
        render_audit_reports()
    elif "Demo Center" in page:
        render_demo_mode()
    else:
        render_fleet_overview()

    # Render Persistent Global Bottom Status Strip
    render_status_strip()


if __name__ == "__main__":
    main()
