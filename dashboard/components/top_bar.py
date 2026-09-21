"""
Egreen Quanta - SIH26138: Top Bar Component.
Global navigation and status header for the Maritime Operator UI/HMI.
Strictly conforms to Section 5 of the Operator UI Master Requirements:
[TOP BAR: Egreen Quanta | mode | fleet | model | scenario | time]
"""

from datetime import datetime, timezone
import streamlit as st


def render_top_bar():
    """Renders the persistent global top navigation bar."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Session state defaults
    if "system_mode" not in st.session_state:
        st.session_state.system_mode = "SIMULATION"
    if "active_scenario_name" not in st.session_state:
        st.session_state.active_scenario_name = "Baseline Voyage (North Sea)"
    if "active_model_id" not in st.session_state:
        st.session_state.active_model_id = "QI-C1-vessel-type (v1.1.0)"

    mode_color = {
        "LIVE": ("rgba(16, 185, 129, 0.2)", "#34d399", "#059669"),
        "SIMULATION": ("rgba(245, 158, 11, 0.2)", "#fbbf24", "#d97706"),
        "DEMO / JURY AUDIT": ("rgba(139, 92, 246, 0.25)", "#c084fc", "#7c3aed"),
    }.get(st.session_state.system_mode, ("rgba(245, 158, 11, 0.2)", "#fbbf24", "#d97706"))

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #0b132b 0%, #1c2541 60%, #0b132b 100%);
            border: 1px solid #1e3a5f;
            border-radius: 8px;
            padding: 10px 18px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        ">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">⚓</span>
                    <span style="font-size: 16px; font-weight: 800; letter-spacing: 1.2px; color: #00E5FF;">
                        EGREEN QUANTA
                    </span>
                    <span style="font-size: 11px; background: rgba(0, 229, 255, 0.15); color: #38bdf8; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(0, 229, 255, 0.3); font-weight: 600;">
                        SIH26138
                    </span>
                </div>
                <span style="color: #475569;">|</span>
                <div>
                    <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Mode:</span>
                    <span style="
                        font-size: 11px;
                        font-weight: 700;
                        padding: 2px 8px;
                        border-radius: 4px;
                        margin-left: 4px;
                        background: {mode_color[0]};
                        color: {mode_color[1]};
                        border: 1px solid {mode_color[2]};
                    ">
                        ● {st.session_state.system_mode}
                    </span>
                </div>
                <span style="color: #475569;">|</span>
                <div>
                    <span style="font-size: 11px; color: #94a3b8;">Fleet:</span>
                    <span style="font-size: 11px; font-weight: 600; color: #f8fafc; margin-left: 4px;">
                        3 Vessels (173,974 Records)
                    </span>
                </div>
                <span style="color: #475569;">|</span>
                <div>
                    <span style="font-size: 11px; color: #94a3b8;">Model:</span>
                    <span style="font-size: 11px; font-weight: 600; color: #38bdf8; margin-left: 4px;">
                        {st.session_state.active_model_id}
                    </span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px;">
                <div>
                    <span style="font-size: 11px; color: #94a3b8;">Scenario:</span>
                    <span style="font-size: 11px; font-weight: 600; color: #e2e8f0; margin-left: 4px;">
                        {st.session_state.active_scenario_name}
                    </span>
                </div>
                <span style="color: #475569;">|</span>
                <div style="font-family: monospace; font-size: 11px; color: #94a3b8;">
                    🕒 {now_utc}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
