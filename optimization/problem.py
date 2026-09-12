"""
Maritime Fleet Optimization Problem Definition.
Compatible with pymoo Problem interface and standalone metaheuristic evaluators.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from pymoo.core.problem import ElementwiseProblem

from .variables import SolutionChromosome, VesselAssignmentDecision
from .repair import SolutionRepairOperator
from .objective import evaluate_fleet_objectives
from physics.resistance_model import VesselResistanceModel
from lca.fuel_registry import FuelPathwayRegistry
from common.config_loader import load_config


class MaritimeFleetProblem(ElementwiseProblem):
    """
    Multi-objective mixed-variable optimization formulation.
    Objectives: [Fuel (tonnes), OPEX (USD), WtW GHG (tonnes CO2e)]
    Constraint: CVaR_0.95(schedule delay) <= max_allowable_cvar_delay_hours
    """

    def __init__(
        self,
        vessel_ids: Optional[List[str]] = None,
        leg_id: str = "route_mumbai_colombo",
        carbon_price: float = 50.0,
        weather_scenario_keys: Optional[List[str]] = None,
    ):
        self.vessel_ids = vessel_ids or ["Vessel_1", "Vessel_2", "Vessel_3"]
        self.leg_id = leg_id
        self.carbon_price = carbon_price
        self.n_vessels = len(self.vessel_ids)

        # Configs
        opt_cfg = load_config("optimization.yaml")
        scen_cfg = load_config("scenarios.yaml")
        self.route_cfg = scen_cfg["routes"][self.leg_id]
        self.weather_cfg = scen_cfg["weather_scenarios"]["scenarios"]

        # Weather scenario list for common random scenario evaluation
        keys = weather_scenario_keys or ["calm", "moderate", "monsoon"]
        self.active_weather = [self.weather_cfg[k] for k in keys]

        self.registry = FuelPathwayRegistry()
        self.vessel_model = VesselResistanceModel()
        self.repair = SolutionRepairOperator(
            min_speed_knots=opt_cfg["decision_space"]["cruising_speed_knots"]["min"],
            max_speed_knots=opt_cfg["decision_space"]["cruising_speed_knots"]["max"],
            max_vessel_capacity_teu=1000.0,
            total_cargo_demand_teu=self.route_cfg["cargo_demand_teu"],
        )
        self.max_cvar_delay = opt_cfg["objectives"]["max_allowable_cvar_delay_hours"]

        # 2 continuous variables per vessel (speed, cargo)
        n_var = self.n_vessels * 2
        xl = np.array([10.0, 0.0] * self.n_vessels)
        xu = np.array([20.0, 1000.0] * self.n_vessels)

        super().__init__(
            n_var=n_var,
            n_obj=3,
            n_ieq_constr=1,
            xl=xl,
            xu=xu,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        chrom = SolutionChromosome.from_flat_vector(x, self.vessel_ids, self.leg_id)
        chrom = self.repair.repair_chromosome(chrom)

        res = evaluate_fleet_objectives(
            chromosome=chrom,
            voyage_distance_nm=self.route_cfg["distance_nautical_miles"],
            deadline_hours=self.route_cfg["target_transit_time_hours"],
            carbon_price_usd_per_tonne=self.carbon_price,
            weather_scenarios=self.active_weather,
            registry=self.registry,
            vessel_model=self.vessel_model,
        )

        f1 = res["total_fuel_consumption_tonnes"]
        f2 = res["total_operational_cost_usd"]
        f3 = res["well_to_wake_ghg_emissions_tonnes_co2e"]

        # CVaR delay constraint: CVaR - max_delay <= 0
        g1 = res["cvar_schedule_delay_hours"] - self.max_cvar_delay

        out["F"] = [f1, f2, f3]
        out["G"] = [g1]
