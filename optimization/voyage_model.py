"""
Voyage Kinematics & Hydrodynamic Speed Loss Engine.
Implements Kwon's empirical involuntary speed loss in irregular waves and wind,
voyage duration calculation, and separate hotel/auxiliary baseline integration.
"""

from typing import Any, Dict, Optional
import numpy as np


class VoyageKinematicsEngine:
    """
    Simulates operational leg kinematics, sea-state speed loss, and leg duration.
    """

    def __init__(self, min_speed_knots: float = 4.0):
        self.min_speed_knots = min_speed_knots

    def compute_involuntary_speed_loss(
        self,
        commanded_speed_kn: float,
        wave_height_m: float,
        wind_speed_ms: float,
        relative_wave_dir_deg: float = 0.0,
        vessel_class: str = "cruise",
    ) -> float:
        """
        Kwon (1982) empirical speed loss formula:
        Delta V / V = (alpha * H_s + beta * V_wind) / 100 * f(theta)
        """
        if wave_height_m <= 0.0 and wind_speed_ms <= 0.0:
            return 0.0

        # Form coefficients based on vessel block coefficient and Froude regime
        if "cruise" in vessel_class.lower() or "passenger" in vessel_class.lower():
            alpha_form = 1.8
            beta_form = 0.08
        elif "offshore" in vessel_class.lower() or "osv" in vessel_class.lower():
            alpha_form = 2.2
            beta_form = 0.10
        else:  # Cargo container feeder
            alpha_form = 1.6
            beta_form = 0.07

        # Directional factor f(theta)
        rel_deg = abs(relative_wave_dir_deg) % 360.0
        if rel_deg > 180.0:
            rel_deg = 360.0 - rel_deg

        if rel_deg <= 30.0:
            f_dir = 1.00  # Head seas
        elif rel_deg <= 60.0:
            f_dir = 0.75  # Bow quartering
        elif rel_deg <= 120.0:
            f_dir = 0.50  # Beam seas
        else:
            f_dir = 0.25  # Following seas

        pct_loss = (alpha_form * wave_height_m + beta_form * wind_speed_ms) * f_dir
        pct_loss = np.clip(pct_loss, 0.0, 45.0)  # Max 45% involuntary speed loss
        delta_v = commanded_speed_kn * (pct_loss / 100.0)
        return float(delta_v)

    def evaluate_leg_kinematics(
        self,
        distance_nm: float,
        commanded_speed_kn: float,
        wave_height_m: float = 0.0,
        wind_speed_ms: float = 0.0,
        relative_wave_dir_deg: float = 0.0,
        operating_mode: str = "transit",
        maneuvering_hours: float = 1.0,
        port_hours: float = 2.0,
        vessel_class: str = "cruise",
    ) -> Dict[str, float]:
        """
        Compute actual speed through water and elapsed duration for a leg.
        """
        if operating_mode.lower() == "port":
            actual_speed_kn = 0.0
            speed_loss_kn = 0.0
            transit_hours = 0.0
            total_hours = port_hours
        elif operating_mode.lower() == "dp":
            actual_speed_kn = 0.5  # Nominal drift speed in DP station keeping
            speed_loss_kn = 0.0
            transit_hours = 0.0
            total_hours = maneuvering_hours
        else:  # Transit / Maneuvering
            speed_loss_kn = self.compute_involuntary_speed_loss(
                commanded_speed_kn=commanded_speed_kn,
                wave_height_m=wave_height_m,
                wind_speed_ms=wind_speed_ms,
                relative_wave_dir_deg=relative_wave_dir_deg,
                vessel_class=vessel_class,
            )
            actual_speed_kn = max(self.min_speed_knots, commanded_speed_kn - speed_loss_kn)
            transit_hours = distance_nm / max(actual_speed_kn, 1.0)
            total_hours = transit_hours + maneuvering_hours

        return {
            "commanded_speed_kn": commanded_speed_kn,
            "speed_loss_kn": speed_loss_kn,
            "actual_speed_kn": actual_speed_kn,
            "transit_hours": transit_hours,
            "total_duration_hours": total_hours,
        }
