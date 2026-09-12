"""
Unified vessel hydrodynamic resistance model.
Aggregates calm-water, wave, and wind resistance for arbitrary vessel geometries and sea states.
"""

from typing import Dict, Any, Optional
from common.config_loader import load_config
from .holtrop_mennen import calculate_calm_water_resistance
from .stawave2 import calculate_added_wave_resistance
from .wind_resistance import calculate_wind_resistance
from .propulsion import calculate_propulsion_power, calculate_fuel_rate


class VesselResistanceModel:
    """
    Evaluates total hydrodynamic resistance and fuel consumption for a given vessel geometry.
    """

    def __init__(self, vessel_type: str = "container_feeder", config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = load_config("physics.yaml")
        self.config = config
        self.vessel_params = self.config["reference_vessels"][vessel_type]
        self.env = self.config["environment"]
        self.prop = self.config["propulsion"]
        self.engine = self.config["engine"]

    def compute_total_resistance(
        self,
        speed_knots: float,
        wave_height_m: float = 0.0,
        wave_period_s: float = 0.0,
        wave_direction_deg: float = 0.0,
        wind_speed_m_s: float = 0.0,
        wind_direction_deg: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Compute all resistance components and resulting fuel rate.

        Inputs:
            speed_knots: Vessel speed in knots (1 knot = 0.514444 m/s)
            wave_height_m: Significant wave height Hs (m)
            wave_period_s: Peak wave period Tp (s)
            wave_direction_deg: Wave encounter angle (0 deg = head sea)
            wind_speed_m_s: Apparent wind speed (m/s)
            wind_direction_deg: Apparent wind angle (0 deg = head wind)

        Returns:
            Dict of hydrodynamic resistance, power, and fuel flow results.
        """
        import math
        speed_m_s = speed_knots * 0.514444
        wave_dir_rad = math.radians(wave_direction_deg)
        wind_dir_rad = math.radians(wind_direction_deg)

        # 1. Calm water resistance
        r_calm = calculate_calm_water_resistance(
            speed_m_s=speed_m_s,
            lwl_m=self.vessel_params["lwl"],
            beam_m=self.vessel_params["beam"],
            draft_m=self.vessel_params["draft"],
            displacement_m3=self.vessel_params["displacement"] / (self.env["seawater_density"] / 1000.0),
            wetted_surface_m2=self.vessel_params["wetted_surface_m2"],
            block_coefficient_cb=self.vessel_params["block_coefficient_cb"],
            gravity_m_s2=self.env["gravity"],
            seawater_density_kg_m3=self.env["seawater_density"],
            kinematic_viscosity_m2_s=self.env["seawater_viscosity"],
        )

        # 2. Added wave resistance
        r_wave = calculate_added_wave_resistance(
            wave_height_m=wave_height_m,
            wave_period_s=wave_period_s,
            wave_direction_rad=wave_dir_rad,
            beam_m=self.vessel_params["beam"],
            lwl_m=self.vessel_params["lwl"],
            draft_m=self.vessel_params["draft"],
            speed_m_s=speed_m_s,
            gravity_m_s2=self.env["gravity"],
            seawater_density_kg_m3=self.env["seawater_density"],
        )

        # 3. Wind resistance
        transverse_area = self.vessel_params["beam"] * 15.0  # Approx superstructure frontal area
        r_wind = calculate_wind_resistance(
            relative_wind_speed_m_s=wind_speed_m_s,
            relative_wind_direction_rad=wind_dir_rad,
            transverse_area_m2=transverse_area,
            lateral_area_m2=transverse_area * 3.5,
            air_density_kg_m3=self.env["air_density"],
        )

        r_total = r_calm["rt_calm_newtons"] + r_wave["r_wave_added_newtons"] + r_wind["r_wind_longitudinal_newtons"]

        # 4. Propulsion power
        power = calculate_propulsion_power(
            total_resistance_newtons=r_total,
            speed_m_s=speed_m_s,
            eta_0=self.prop["propeller_open_water_efficiency_nominal"],
            eta_h=self.prop["hull_efficiency_nominal"],
            eta_r=self.prop["relative_rotative_efficiency_nominal"],
            eta_s=self.prop["shaft_transmission_efficiency"],
        )

        # 5. Fuel flow rate
        fuel = calculate_fuel_rate(
            brake_power_kw=power["pb_kw"],
            nominal_sfc_g_kwh=self.engine["nominal_sfc_g_kwh"],
            mcr_kw=self.engine["nominal_mcr_kw"],
            auxiliary_power_kw=self.engine["auxiliary_power_baseline_kw"],
            boiler_rate_kg_h=self.engine["boiler_fuel_rate_kg_h"],
        )

        return {
            "speed_knots": speed_knots,
            "speed_m_s": speed_m_s,
            "r_calm_newtons": r_calm["rt_calm_newtons"],
            "r_wave_newtons": r_wave["r_wave_added_newtons"],
            "r_wind_newtons": r_wind["r_wind_longitudinal_newtons"],
            "r_total_newtons": r_total,
            "power": power,
            "fuel": fuel,
        }
