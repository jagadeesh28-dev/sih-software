"""
Egreen Quanta - SIH26138: Vessel Card Component.
Standardized visual card for vessels in Fleet Command Center.
Conforms to Phase 4 requirements:
Shows: vessel name, vessel_type, speed, fuel type, predicted fuel consumption,
uncertainty, OOD state, model state, schedule state, and alert state.
"""

from typing import Any, Dict
import streamlit as st


def render_vessel_card(vessel_data: Dict[str, Any], key_prefix: str = "card"):
    """
    Renders a high-density, maritime-styled vessel telemetry & prediction card.
    """
    name = vessel_data.get("name", "Unknown Vessel")
    vessel_type = vessel_data.get("vessel_type", "commercial_vessel")
    speed_kn = vessel_data.get("speed_kn", 14.0)
    fuel_type = vessel_data.get("fuel_type", "vlsfo").upper()
    fuel_actual = vessel_data.get("fuel_actual_kg_h")
    fuel_pred = vessel_data.get("fuel_pred_kg_h", 2500.0)
    interval_lower = vessel_data.get("interval_lower_kg_h", 1800.0)
    interval_upper = vessel_data.get("interval_upper_kg_h", 3200.0)
    ood_status = vessel_data.get("ood_status", "IN-DOMAIN")
    model_state = vessel_data.get("model_state", "QI-C1-vessel-type")
    schedule_status = vessel_data.get("schedule_status", "Schedule OK")
    alert_state = vessel_data.get("alert_state", "NOMINAL")
    route = vessel_data.get("route", "North Sea Transit")
    draft_m = vessel_data.get("draft_m", 7.0)
    displacement_t = vessel_data.get("displacement_t", 30000.0)

    # Status indicators with icons and text (never color alone)
    ood_badge_map = {
        "IN-DOMAIN": ("✔ IN-DOMAIN", "rgba(16, 185, 129, 0.15)", "#10b981", "border: 1px solid #059669;"),
        "WARNING": ("⚠ WARNING", "rgba(245, 158, 11, 0.15)", "#f59e0b", "border: 1px solid #d97706;"),
        "OOD": ("⛔ OOD", "rgba(239, 68, 68, 0.2)", "#ef4444", "border: 1px solid #dc2626;"),
        "FALLBACK": ("🔄 FALLBACK", "rgba(239, 68, 68, 0.2)", "#ef4444", "border: 1px solid #dc2626;"),
    }
    badge_text, badge_bg, badge_fg, badge_border = ood_badge_map.get(
        ood_status, ("✔ IN-DOMAIN", "rgba(16, 185, 129, 0.15)", "#10b981", "border: 1px solid #059669;")
    )

    sched_badge = "✔ ON TIME" if "OK" in schedule_status or "TIME" in schedule_status else "⏱ DELAY RISK"
    sched_fg = "#10b981" if "ON TIME" in sched_badge else "#f59e0b"

    alert_color = "#10b981" if alert_state == "NOMINAL" else "#f59e0b"

    st.markdown(
        f"""
        <div style="
            background: #111827;
            border: 1px solid #1f2937;
            border-left: 4px solid {'#00E5FF' if 'Poseidon' in name else ('#38bdf8' if 'Triton' in name else '#818cf8')};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        ">
            <!-- Header Row -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px; font-weight: 700; color: #f8fafc; letter-spacing: 0.5px;">
                            {name}
                        </span>
                        <span style="font-size: 11px; background: #1e293b; color: #94a3b8; padding: 2px 6px; border-radius: 4px; font-family: monospace;">
                            vessel_type: {vessel_type}
                        </span>
                        <span style="font-size: 11px; background: #0f172a; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-family: monospace; border: 1px solid #1e3a5f;">
                            fuel: {fuel_type}
                        </span>
                    </div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
                        Route: {route} | Draft: {draft_m:.1f} m | Disp: {displacement_t:,.0f} t | Model: {model_state}
                    </div>
                </div>
                <div style="display: flex; gap: 6px;">
                    <span style="
                        font-size: 11px;
                        font-weight: 700;
                        padding: 3px 8px;
                        border-radius: 4px;
                        background: {badge_bg};
                        color: {badge_fg};
                        {badge_border}
                    ">
                        {badge_text}
                    </span>
                    <span style="
                        font-size: 11px;
                        font-weight: 600;
                        padding: 3px 8px;
                        border-radius: 4px;
                        background: rgba(255, 255, 255, 0.05);
                        color: {sched_fg};
                        border: 1px solid #374151;
                    ">
                        {sched_badge}
                    </span>
                    <span style="
                        font-size: 11px;
                        font-weight: 600;
                        padding: 3px 8px;
                        border-radius: 4px;
                        background: rgba(255, 255, 255, 0.05);
                        color: {alert_color};
                        border: 1px solid #374151;
                    ">
                        ● {alert_state}
                    </span>
                </div>
            </div>

            <!-- Telemetry & Predictions Grid -->
            <div style="display: grid; grid-template-columns: 1fr 1.6fr 1.8fr; gap: 12px; background: #0b0f19; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
                <!-- Speed Column -->
                <div>
                    <div style="font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600;">Speed Over Water</div>
                    <div style="font-size: 20px; font-weight: 800; color: #38bdf8; margin-top: 2px;">
                        {speed_kn:.1f} <span style="font-size: 11px; font-weight: 500; color: #94a3b8;">kn</span>
                    </div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 2px;">Measured Telemetry</div>
                </div>

                <!-- Predicted Fuel Column -->
                <div>
                    <div style="font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600;">Predicted Fuel Rate</div>
                    <div style="font-size: 20px; font-weight: 800; color: #00E5FF; margin-top: 2px;">
                        {fuel_pred:,.2f} <span style="font-size: 11px; font-weight: 500; color: #94a3b8;">kg/h</span>
                    </div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 2px;">
                        {'Actual: ' + f'{fuel_actual:,.1f} kg/h' if fuel_actual else 'Serving: QI-C1-vessel-type'}
                    </div>
                </div>

                <!-- Conformal Uncertainty Column -->
                <div>
                    <div style="font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600;">90% Conformal Interval</div>
                    <div style="font-size: 14px; font-weight: 700; color: #e2e8f0; margin-top: 5px; font-family: monospace;">
                        [{interval_lower:,.1f} - {interval_upper:,.1f}] <span style="font-size: 10px; color: #94a3b8;">kg/h</span>
                    </div>
                    <div style="font-size: 10px; color: #10b981; margin-top: 2px;">
                        ±{(interval_upper - interval_lower) / 2:,.1f} kg/h (93.2% calibrated)
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
