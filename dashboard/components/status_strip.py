"""
Egreen Quanta - SIH26138: Bottom Status Strip Component.
Persistent global footer conforming to Section 5:
[BOTTOM STATUS: data freshness | model state | OOD state | last recommendation]
"""

from datetime import datetime, timezone
import streamlit as st


def render_status_strip():
    """Renders the persistent bottom status bar."""
    now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

    # State values
    data_freshness = st.session_state.get("data_freshness", "Real-time Telemetry (<10s)")
    model_state = st.session_state.get("active_routing_state", "NORMAL: QI-C1-vessel-type")
    ood_state = st.session_state.get("ood_state", "IN-DOMAIN (d_env=0.384)")
    last_action = st.session_state.get("last_recommendation_status", "ADVISORY READY — Awaiting Operator Confirmation")
    
    is_ood = "OOD" in ood_state or "REJECTED" in ood_state
    is_fallback = "FALLBACK" in model_state or "EMERGENCY" in model_state
    is_accepted = "ACCEPTED" in last_action

    ood_color = "#ef4444" if is_ood else ("#f59e0b" if "WARNING" in ood_state else "#10b981")
    model_color = "#ef4444" if is_fallback else "#38bdf8"
    action_color = "#10b981" if is_accepted else "#94a3b8"

    st.markdown(
        f"""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #090e1a;
            border-top: 1px solid #1e293b;
            padding: 6px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: #94a3b8;
            z-index: 9999;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.5);
        ">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div>
                    <span style="color: #64748b;">DATA FRESHNESS:</span>
                    <span style="color: #e2e8f0; font-weight: 600; margin-left: 4px;">{data_freshness}</span>
                </div>
                <span style="color: #334155;">|</span>
                <div>
                    <span style="color: #64748b;">MODEL ROUTING:</span>
                    <span style="color: {model_color}; font-weight: 700; margin-left: 4px;">
                        {'⚠ ' if is_fallback else '✔ '}{model_state}
                    </span>
                </div>
                <span style="color: #334155;">|</span>
                <div>
                    <span style="color: #64748b;">OOD GUARD:</span>
                    <span style="color: {ood_color}; font-weight: 700; margin-left: 4px;">
                        {'⛔ ' if is_ood else '✔ '}{ood_state}
                    </span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px;">
                <div>
                    <span style="color: #64748b;">DECISION SUPPORT:</span>
                    <span style="color: {action_color}; font-weight: 600; margin-left: 4px;">
                        {last_action}
                    </span>
                </div>
                <span style="color: #334155;">|</span>
                <div style="font-family: monospace; color: #64748b;">
                    HEARTBEAT: {now_utc}
                </div>
            </div>
        </div>
        <div style="height: 32px;"></div>
        """,
        unsafe_allow_html=True,
    )
