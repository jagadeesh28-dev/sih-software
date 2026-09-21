"""
SIH26138 — Egreen Quanta: SIH Multi-Objective Operational Cost & Lifecycle GHG Engine.
Integrates transparent, configuration-driven formulations for:
1. Operational Cost Minimization (Fuel + Shore Power + Carbon Levy + Demurrage)
2. Lifecycle GHG Minimization (IMO MEPC.391(81) Well-to-Wake: WtT + TtW + Methane Slip)
3. Multi-Objective Trade-Off & Pareto Frontier Evaluation

Mathematical Formulations:
- C_total = C_fuel + C_electricity + C_OPS + C_carbon + C_schedule_penalty
    C_fuel = m_fuel * fuel_price
    C_OPS  = (P_aux * t_berth * electricity_price) + connection_fee  (if shore power enabled, else 0)
    C_carbon = fossil_CO2_TtW * carbon_price * ets_scope
    C_schedule = max(0, t_voyage - t_deadline) * demurrage_rate

- GHG_WtW = sum_legs ( E_fuel * WtT_intensity + TtW_GHG_direct + Methane_Slip_GWP )
    E_fuel = m_fuel * LHV_fuel
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import yaml

from common.config_loader import load_config
from lca.fuel_registry import FuelPathwayRegistry
from optimization.cost_model import FleetCostEngine
from optimization.emissions_model import FleetEmissionsEngine


@dataclass
class SIHOptimizationObjectives:
    """Standardized multi-objective metrics vector for SIH26138."""
    fuel_tonnes: float
    operational_cost_usd: float
    lifecycle_ghg_tonnes: float
    schedule_delay_hours: float
    total_penalty: float = 0.0
    is_feasible: bool = True

    # Itemized cost breakdown
    fuel_cost_usd: float = 0.0
    carbon_cost_usd: float = 0.0
    shore_power_cost_usd: float = 0.0
    schedule_penalty_usd: float = 0.0
    fueleu_penalty_usd: float = 0.0

    # Itemized emission breakdown
    wtt_ghg_tonnes: float = 0.0
    ttw_ghg_tonnes: float = 0.0
    methane_slip_tonnes: float = 0.0

    # Decoded decisions
    vessel_id: str = ""
    vessel_type: str = ""
    fuel_type: str = ""
    speed_knots: float = 0.0
    use_shore_power: bool = False

    def as_vector(self, mode: str = "FULL") -> np.ndarray:
        """
        Extract numeric objective vector for optimization.
        Modes:
        - 'FUEL_ONLY': [Fuel (t)]
        - 'COST_ONLY': [Cost ($)]
        - 'GHG_ONLY':  [GHG (t)]
        - 'FUEL_COST': [Fuel (t), Cost ($)]
        - 'FUEL_GHG':  [Fuel (t), GHG (t)]
        - 'TRI_OBJECTIVE': [Fuel (t), Cost ($), GHG (t)]
        - 'FULL': [Fuel (t), Cost ($), GHG (t), Delay (h)]
        """
        m = mode.upper()
        if m == "FUEL_ONLY":
            return np.array([self.fuel_tonnes], dtype=float)
        elif m == "COST_ONLY":
            return np.array([self.operational_cost_usd], dtype=float)
        elif m == "GHG_ONLY":
            return np.array([self.lifecycle_ghg_tonnes], dtype=float)
        elif m == "FUEL_COST":
            return np.array([self.fuel_tonnes, self.operational_cost_usd], dtype=float)
        elif m == "FUEL_GHG":
            return np.array([self.fuel_tonnes, self.lifecycle_ghg_tonnes], dtype=float)
        elif m == "TRI_OBJECTIVE":
            return np.array([self.fuel_tonnes, self.operational_cost_usd, self.lifecycle_ghg_tonnes], dtype=float)
        else:
            return np.array([
                self.fuel_tonnes,
                self.operational_cost_usd,
                self.lifecycle_ghg_tonnes,
                self.schedule_delay_hours,
            ], dtype=float)


class SIHObjectiveEngine:
    """
    Executable SIH Objective Evaluator managing Fuel, Operational Cost, and Lifecycle GHG.
    Reads official scenario prices and emission factors dynamically from configuration.
    """

    def __init__(
        self,
        fuels_config: Optional[Dict[str, Any]] = None,
        carbon_price_usd_tonne: float = 90.0,
        demurrage_rate_usd_hour: float = 1000.0,
        shore_power_tariff_usd_kwh: float = 0.18,
        shore_power_connect_fee_usd: float = 500.0,
        ets_scope: float = 1.0,
        bunker_price_overrides: Optional[Dict[str, float]] = None,
    ):
        self.fuels_config = fuels_config or load_config("fuels.yaml")
        self.registry = FuelPathwayRegistry(config=self.fuels_config)
        self.emissions_engine = FleetEmissionsEngine(registry=self.registry)

        # Build bunker price dictionary from configuration
        self.bunker_prices: Dict[str, float] = {}
        for f_key, p_data in self.registry.pathways.items():
            self.bunker_prices[f_key.lower()] = float(p_data.get("price_usd_per_tonne", 650.0))

        if bunker_price_overrides:
            for k, v in bunker_price_overrides.items():
                self.bunker_prices[k.lower()] = float(v)

        # Shore power config
        sp_conf = self.fuels_config.get("shore_power", {})
        self.shore_power_tariff = float(sp_conf.get("price_usd_per_kwh", shore_power_tariff_usd_kwh))
        self.shore_power_connect_fee = float(sp_conf.get("connection_fee_usd_per_call", shore_power_connect_fee_usd))
        self.shore_power_grid_emission_factor = float(sp_conf.get("grid_emission_factor_g_co2e_kwh", 450.0))

        self.cost_engine = FleetCostEngine(
            registry=self.registry,
            carbon_price_usd_tonne=carbon_price_usd_tonne,
            demurrage_rate_usd_hour=demurrage_rate_usd_hour,
            shore_power_tariff_usd_kwh=self.shore_power_tariff,
            shore_power_connect_fee_usd=self.shore_power_connect_fee,
            ets_scope=ets_scope,
            bunker_prices_usd_tonne=self.bunker_prices,
        )

    def evaluate_voyage(
        self,
        vessel_id: str,
        vessel_type: str,
        speed_knots: float,
        voyage_distance_nm: float,
        schedule_deadline_hours: float,
        baseline_fuel_rate_kg_h: float,
        fuel_type: str = "vlsfo",
        use_shore_power: bool = False,
        port_hours: float = 0.0,
        hotel_load_kw: float = 0.0,
        fueleu_penalty_usd: float = 0.0,
    ) -> SIHOptimizationObjectives:
        """
        Evaluate single voyage leg across Fuel, Operational Cost, and Lifecycle GHG.
        """
        from optimization.canonical_mapper import canonicalize_fuel_type
        try:
            f_type = canonicalize_fuel_type(fuel_type)
        except Exception:
            f_type = "vlsfo"
        if f_type not in self.registry.pathways:
            f_type = "vlsfo"
        if speed_knots <= 0.0:
            voyage_hours = 1000.0
            leg_delay_h = 1000.0
            fuel_mass_kg = 0.0
        else:
            voyage_hours = voyage_distance_nm / speed_knots
            leg_delay_h = max(0.0, voyage_hours - schedule_deadline_hours)

            # Convert baseline VLSFO kg to target fuel equivalent
            vlsfo_leg_kg = baseline_fuel_rate_kg_h * voyage_hours
            fuel_mass_kg = self.emissions_engine.convert_fuel_mass_for_pathway(
                baseline_vlsfo_kg=vlsfo_leg_kg,
                target_fuel_type=f_type,
            )

        fuel_tonnes = fuel_mass_kg / 1000.0

        # 1. Lifecycle Emissions Calculation
        emissions_res = self.emissions_engine.compute_leg_emissions(
            fuel_mass_kg=fuel_mass_kg,
            fuel_type=f_type,
        )

        wtw_ghg_t = emissions_res["wtw_total_tonnes_co2e"]
        ttw_co2_t = emissions_res["ttw_co2_tonnes"]

        # Shore power grid emissions if cold ironing at berth
        if use_shore_power and port_hours > 0.0 and hotel_load_kw > 0.0:
            shore_kwh = hotel_load_kw * port_hours
            shore_ghg_t = (shore_kwh * self.shore_power_grid_emission_factor) / 1e6
            wtw_ghg_t += shore_ghg_t

        # 2. Operational Cost Calculation
        costs_res = self.cost_engine.compute_leg_costs(
            fuel_mass_tonnes=fuel_tonnes,
            fuel_type=f_type,
            ttw_co2_tonnes=ttw_co2_t,
            voyage_duration_hours=voyage_hours,
            schedule_deadline_hours=schedule_deadline_hours,
            use_shore_power=use_shore_power,
            port_hours=port_hours,
            hotel_load_kw=hotel_load_kw,
            fueleu_penalty_usd=fueleu_penalty_usd,
        )

        # 3. Feasibility check
        is_feas = bool(leg_delay_h == 0.0 and speed_knots > 0.0)
        penalty = 500.0 * leg_delay_h if leg_delay_h > 0.0 else 0.0

        return SIHOptimizationObjectives(
            fuel_tonnes=round(fuel_tonnes, 4),
            operational_cost_usd=round(costs_res["total_opex_usd"], 2),
            lifecycle_ghg_tonnes=round(wtw_ghg_t, 4),
            schedule_delay_hours=round(leg_delay_h, 2),
            total_penalty=round(penalty, 2),
            is_feasible=is_feas,
            fuel_cost_usd=round(costs_res["fuel_cost_usd"], 2),
            carbon_cost_usd=round(costs_res["carbon_cost_usd"], 2),
            shore_power_cost_usd=round(costs_res["shore_power_cost_usd"], 2),
            schedule_penalty_usd=round(costs_res["schedule_penalty_cost_usd"], 2),
            fueleu_penalty_usd=round(costs_res["fueleu_penalty_usd"], 2),
            wtt_ghg_tonnes=round(emissions_res["wtt_tonnes_co2e"], 4),
            ttw_ghg_tonnes=round(emissions_res["ttw_total_tonnes_co2e"], 4),
            methane_slip_tonnes=round(emissions_res["methane_slip_tonnes_co2e"], 4),
            vessel_id=vessel_id,
            vessel_type=vessel_type,
            fuel_type=f_type,
            speed_knots=speed_knots,
            use_shore_power=use_shore_power,
        )

    @staticmethod
    def is_pareto_efficient(costs: np.ndarray) -> np.ndarray:
        """
        Find the Pareto-efficient points along a multi-objective cost matrix.
        costs: (n_points, n_objectives) array where all objectives are to be MINIMIZED.
        Returns boolean array of shape (n_points,).
        """
        is_efficient = np.ones(costs.shape[0], dtype=bool)
        for i, c in enumerate(costs):
            if is_efficient[i]:
                # Keep any point with a lower cost in at least one dimension
                is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)
                is_efficient[i] = True
        return is_efficient

    @staticmethod
    def compute_hypervolume_2d(points: np.ndarray, ref_point: np.ndarray) -> float:
        """
        Exact 2D hypervolume computation for 2-objective minimization.
        points: (N, 2) array
        ref_point: (2,) array representing upper bound (nadir)
        """
        if len(points) == 0:
            return 0.0
        # Filter points that strictly dominate ref_point
        valid = points[np.all(points <= ref_point, axis=1)]
        if len(valid) == 0:
            return 0.0
        # Sort by first objective ascending
        sorted_idx = np.argsort(valid[:, 0])
        sorted_pts = valid[sorted_idx]

        hv = 0.0
        prev_y = ref_point[1]
        for pt in sorted_pts:
            if pt[1] < prev_y:
                width = ref_point[0] - pt[0]
                height = prev_y - pt[1]
                hv += width * height
                prev_y = pt[1]
        return float(hv)
