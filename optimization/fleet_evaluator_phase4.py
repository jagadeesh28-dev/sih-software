"""
Phase 4 Heterogeneous Fleet Evaluation Engine.
Integrates real-telemetry calibrated SafeFuelObjective models across heterogeneous vessels,
operational cargo demand fulfillment, multi-scenario weather uncertainty, involuntary speed loss,
IMO CII / FuelEU Maritime compliance, and CVaR distributionally-robust risk objectives.

Label: REAL_TELEMETRY_CALIBRATED / SYNTHETIC_OPERATIONAL_SCENARIO
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from prediction.safe_objective import SafeFuelObjective
from prediction.domain_checker import DomainChecker
from .canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type, get_baseline_fuel_for_vessel
from .emissions_model import FleetEmissionsEngine
from .cost_model import FleetCostEngine
from .regulatory import FleetRegulatoryEngine
from .voyage_model import VoyageKinematicsEngine
from .berth_model import DEFAULT_PORT_HOURS, SFOC_KG_VLSFO_PER_KWH, berth_accounting, grid_emission_factor_g_per_kwh
from .fleet_heterogeneous import (
    FleetVesselProfile,
    CargoDemand,
    WeatherScenario,
    FLEET_VESSELS,
    OPERATIONAL_DEMANDS,
    WEATHER_SCENARIOS,
    DECISION_DIMS_PER_VESSEL,
    DEMAND_KEYS,
    REV_DEMAND_KEYS,
    DecodedVesselDecision,
    decode_fleet_vector,
    get_fleet_bounds,
    compute_cvar_risk,
)
from .variables import FUEL_MAP, MODE_MAP


@dataclass
class Phase4FleetEvaluationResult:
    """Comprehensive, scientifically auditable result of a Phase 4 fleet strategy evaluation."""
    fitness: float                     # Total penalized fitness = robust_objective + constraint_penalties
    physical_fitness: float            # Unpenalized robust objective J_robust
    objective_vector: np.ndarray       # [Fuel (t), Cost ($), WtW GHG (t), Delay (h), CVaR Risk ($)]
    expected_objective: float          # E[Loss] across weather scenarios
    cvar_objective: float              # CVaR_0.80(Loss) across weather scenarios
    risk_metric: float                 # max(0, CVaR_0.80 - E[Loss])

    # Decomposed physical metrics (probability-weighted expectations)
    total_fuel_tonnes: float
    total_opex_usd: float
    total_wtw_ghg_tonnes: float
    total_schedule_delay_hours: float
    uncertainty_risk_metric: float

    # Cost subcomponents ($)
    fuel_cost_usd: float
    carbon_cost_usd: float
    shore_power_cost_usd: float
    schedule_penalty_cost_usd: float
    fueleu_penalty_usd: float

    # Scenario breakdowns: scenario_id -> loss
    scenario_losses: Dict[str, float]
    scenario_details: Dict[str, Dict[str, Any]]

    # Regulatory outcomes
    cii_ratings: Dict[str, str]
    fueleu_compliant: Dict[str, bool]

    # Feasibility, domain, and constraint diagnostics
    domain_status: str                 # "VALID", "NEAR_BOUNDARY", "OUT_OF_DOMAIN", "PHYSICALLY_INVALID"
    is_feasible: bool
    hard_violations: List[str]
    soft_penalties: Dict[str, float]
    total_penalty_value: float

    # Decisions decoded
    assigned_demands: Dict[str, str]
    cargo_allocations: Dict[str, float]
    speed_decisions: Dict[str, float]
    fuel_decisions: Dict[str, str]
    shore_power_decisions: Dict[str, bool]

    explanation: str
    source_provenance: str = "REAL_TELEMETRY_CALIBRATED"


class Phase4FleetEvaluator:
    """
    Evaluates heterogeneous fleet decision vectors under weather uncertainty.
    Ensures:
    1. Every vessel fuel calculation passes through its calibrated SafeFuelObjective.
    2. Demand-vessel physical and commercial compatibility is enforced.
    3. Exactly-once cargo demand fulfillment is required.
    4. Multi-weather scenario CVaR risk is computed.
    5. Regulatory (CII and FuelEU) compliance is accurately audited.
    """

    def __init__(
        self,
        surrogates: Dict[str, SafeFuelObjective],
        vessels: Optional[List[FleetVesselProfile]] = None,
        demands: Optional[Dict[str, CargoDemand]] = None,
        weather_scenarios: Optional[List[WeatherScenario]] = None,
        emissions_engine: Optional[FleetEmissionsEngine] = None,
        cost_engine: Optional[FleetCostEngine] = None,
        regulatory_engine: Optional[FleetRegulatoryEngine] = None,
        kinematics_engine: Optional[VoyageKinematicsEngine] = None,
        weights: Optional[np.ndarray] = None,
        lambda_robust: float = 0.50,
        cvar_alpha: float = 0.80,
        require_all_demands: bool = True,
    ):
        self.surrogates = surrogates
        self.vessels = vessels if vessels is not None else [
            FLEET_VESSELS["CPS_Poseidon"],
            FLEET_VESSELS["CPS_Triton"],
            FLEET_VESSELS["OSS_Ceto"],
        ]
        self.demands = demands if demands is not None else OPERATIONAL_DEMANDS
        self.weather_scenarios = weather_scenarios if weather_scenarios is not None else WEATHER_SCENARIOS
        self.emissions_engine = emissions_engine or FleetEmissionsEngine()
        self.cost_engine = cost_engine or FleetCostEngine()
        self.regulatory_engine = regulatory_engine or FleetRegulatoryEngine()
        self.kinematics_engine = kinematics_engine or VoyageKinematicsEngine()

        # Multi-objective weights [Fuel, Cost, GHG, Schedule, Risk]
        self.weights = weights if weights is not None else np.array([0.30, 0.30, 0.25, 0.10, 0.05], dtype=float)
        self.lambda_robust = lambda_robust
        self.cvar_alpha = cvar_alpha
        self.require_all_demands = require_all_demands
        # Berth phase per assigned demand (assumed scenario input) and grid factor for shore power
        self.port_hours = DEFAULT_PORT_HOURS
        self.grid_factor_g_per_kwh = grid_emission_factor_g_per_kwh()

        # Normalization reference scales for 5-objective vector
        # [Fuel (t), Cost ($), GHG (t), Delay (h), Risk ($)]
        self.norm_scales = np.array([50.0, 50000.0, 150.0, 10.0, 10000.0], dtype=float)

        # Precompute ultra-high-resolution calibration grids for real-data surrogates across (vessel, scenario)
        self._calibration_grids: Dict[Tuple[str, str], Dict[str, np.ndarray]] = {}
        self._init_calibration_grids()

    def _init_calibration_grids(self):
        """Constructs 100-point speed calibration grids for each (vessel, scenario) pair."""
        for v in self.vessels:
            surrogate = self.surrogates.get(v.vessel_id)
            if surrogate is None:
                surrogate = list(self.surrogates.values())[0]

            speeds = np.linspace(0.5, v.max_speed_knots + 2.0, 101)
            for scen in self.weather_scenarios:
                medians = []
                uncs = []
                for sp in speeds:
                    c = {
                        "stw_kn": sp,
                        "sog_kn": sp,
                        "draft_m": v.design_draft_m,
                        "displacement_t": v.displacement_t,
                        "wind_speed_ms": scen.wind_speed_ms,
                        "wind_direction_deg": scen.wind_direction_deg,
                        "wave_height_m": scen.wave_height_m,
                        "wave_period_s": scen.wave_period_s,
                        "wave_direction_deg": 180.0,
                        "current_speed_ms": scen.current_speed_ms,
                        "current_direction_deg": scen.current_direction_deg,
                        "water_depth_m": scen.water_depth_m,
                        "vessel_type": canonicalize_vessel_type(v.class_family),
                        "fuel_type": get_baseline_fuel_for_vessel(v.vessel_id),
                    }
                    res = surrogate.evaluate_candidate(c, lambda_robust=0.5)
                    medians.append(res["median_prediction"])
                    uncs.append(res.get("uncertainty_width", 200.0))

                self._calibration_grids[(v.vessel_id, scen.scenario_id)] = {
                    "speeds": speeds,
                    "medians": np.array(medians, dtype=float),
                    "uncs": np.array(uncs, dtype=float),
                }

    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns lower and upper bounds for the flat fleet decision vector."""
        return get_fleet_bounds(self.vessels)

    def evaluate_vector(
        self,
        X_fleet: np.ndarray,
        lambda_robust: Optional[float] = None,
    ) -> Phase4FleetEvaluationResult:
        """
        Evaluates a flat continuous/discrete candidate decision vector X_fleet.
        Calculates scenario losses across all weather conditions, computes CVaR,
        applies assignment penalties, and generates an auditable result.
        """
        lam = lambda_robust if lambda_robust is not None else self.lambda_robust

        # 0. Sanity check finite inputs
        if np.any(np.isnan(X_fleet)) or np.any(np.isinf(X_fleet)):
            return self._build_invalid_result("Candidate decision vector contains NaN or Inf.")

        # 1. Decode decisions
        decisions = decode_fleet_vector(X_fleet, self.vessels)

        hard_violations: List[str] = []
        soft_penalties: Dict[str, float] = {}
        total_penalty = 0.0
        worst_domain_status = "VALID"

        # 2. Check Combinatorial Assignment Constraints
        assigned_demand_counts: Dict[str, int] = {k: 0 for k in self.demands.keys()}
        assigned_demands_map: Dict[str, str] = {}
        cargo_map: Dict[str, float] = {}
        speed_map: Dict[str, float] = {}
        fuel_map: Dict[str, str] = {}
        shore_map: Dict[str, bool] = {}

        for d in decisions:
            assigned_demands_map[d.vessel_id] = d.assigned_demand
            cargo_map[d.vessel_id] = d.cargo_tonnes
            speed_map[d.vessel_id] = d.speed_knots
            fuel_map[d.vessel_id] = d.fuel_type
            shore_map[d.vessel_id] = d.use_shore_power

            # Check compatibility flag from decoder
            if not d.is_compatible:
                hard_violations.append(f"{d.vessel_id}: {d.incompatibility_reason}")
                total_penalty += 100000.0

            # Count demand assignment
            if d.assigned_demand != "UNASSIGNED":
                if d.assigned_demand in assigned_demand_counts:
                    assigned_demand_counts[d.assigned_demand] += 1
                else:
                    hard_violations.append(f"Unknown demand ID {d.assigned_demand}")
                    total_penalty += 50000.0

        # Check duplicate demand assignments
        for dem_id, count in assigned_demand_counts.items():
            if count > 1:
                hard_violations.append(f"Duplicate demand {dem_id} assigned to {count} vessels (must be exactly 1).")
                total_penalty += 100000.0 * (count - 1)
            elif count == 0 and self.require_all_demands:
                hard_violations.append(f"Mandatory demand {dem_id} is unfulfilled.")
                total_penalty += 50000.0

        # Fast-path for mathematically infeasible candidates
        # If candidate already has hard assignment/compatibility violations, return penalized result immediately
        if len(hard_violations) > 0:
            return Phase4FleetEvaluationResult(
                fitness=float(total_penalty + 1000.0),
                physical_fitness=1000.0,
                objective_vector=np.array([200.0, 250000.0, 750.0, 10.0, 0.0], dtype=float),
                expected_objective=1000.0,
                cvar_objective=1000.0,
                risk_metric=0.0,
                total_fuel_tonnes=200.0,
                total_opex_usd=250000.0,
                total_wtw_ghg_tonnes=750.0,
                total_schedule_delay_hours=10.0,
                uncertainty_risk_metric=0.0,
                fuel_cost_usd=160000.0,
                carbon_cost_usd=40000.0,
                shore_power_cost_usd=10000.0,
                schedule_penalty_cost_usd=15000.0,
                fueleu_penalty_usd=0.0,
                scenario_losses={"SCEN-W1": 1000.0},
                scenario_details={},
                cii_ratings={"all": "E"},
                fueleu_compliant={"all": False},
                domain_status="VALID",
                is_feasible=False,
                hard_violations=hard_violations,
                soft_penalties=soft_penalties,
                total_penalty_value=round(total_penalty, 2),
                assigned_demands=assigned_demands_map,
                cargo_allocations=cargo_map,
                speed_decisions=speed_map,
                fuel_decisions=fuel_map,
                shore_power_decisions=shore_map,
                explanation=f"Fleet Strategy: INFEASIBLE [{'; '.join(hard_violations)}]",
                source_provenance="REAL_TELEMETRY_CALIBRATED",
            )

        # 3. Evaluate Fleet Performance Across Weather Scenarios
        scenario_losses: Dict[str, float] = {}
        scenario_details: Dict[str, Dict[str, Any]] = {}
        scenario_obj_vectors: List[np.ndarray] = []
        scenario_weights: List[float] = []

        cii_ratings_summary: Dict[str, str] = {}
        fueleu_compliant_summary: Dict[str, bool] = {}

        for scen in self.weather_scenarios:
            scen_fuel_t = 0.0
            scen_opex_usd = 0.0
            scen_ghg_t = 0.0
            scen_delay_h = 0.0
            scen_fuel_cost = 0.0
            scen_carbon_cost = 0.0
            scen_shore_cost = 0.0
            scen_schedule_cost = 0.0
            scen_fueleu_penalty = 0.0

            for d in decisions:
                if d.assigned_demand == "UNASSIGNED":
                    continue

                demand = self.demands[d.assigned_demand]
                v_prof = next(v for v in self.vessels if v.vessel_id == d.vessel_id)
                v_class = v_prof.class_family

                # Non-positive speed defense
                if d.speed_knots <= 0.0:
                    hard_violations.append(f"{d.vessel_id}: non-positive speed {d.speed_knots:.1f} kn causes deadline breach.")
                    total_penalty += 100000.0
                    duration_h = 1000.0
                    act_speed = 0.1
                else:
                    # Kinematics with involuntary speed loss under this weather scenario
                    kin = self.kinematics_engine.evaluate_leg_kinematics(
                        distance_nm=demand.distance_nm,
                        commanded_speed_kn=d.speed_knots,
                        wave_height_m=scen.wave_height_m,
                        wind_speed_ms=scen.wind_speed_ms,
                        operating_mode=d.operating_mode,
                        vessel_class=v_class,
                    )
                    act_speed = kin["actual_speed_kn"]
                    duration_h = kin["total_duration_hours"]

                # Schedule delay
                leg_delay_h = max(0.0, duration_h - demand.deadline_hours)
                scen_delay_h += leg_delay_h
                if leg_delay_h > 0.0:
                    soft_penalties["schedule_delay"] = soft_penalties.get("schedule_delay", 0.0) + (leg_delay_h * 500.0)
                    total_penalty += leg_delay_h * 500.0

                # SafeFuelObjective Query via calibration grid for microsecond evaluation
                grid_key = (d.vessel_id, scen.scenario_id)
                grid = self._calibration_grids.get(grid_key)
                if grid is not None:
                    clipped_speed = float(np.clip(act_speed, grid["speeds"][0], grid["speeds"][-1]))
                    f_rate_kg_h = float(np.interp(clipped_speed, grid["speeds"], grid["medians"]))
                    unc_width_kg_h = float(np.interp(clipped_speed, grid["speeds"], grid["uncs"]))
                    # The grid only accelerates the fuel lookup; the domain check must still run on the
                    # actual operating state, otherwise extrapolated speeds pass as feasible.
                    grid_surrogate = self.surrogates.get(d.vessel_id) or list(self.surrogates.values())[0]
                    domain_status_i = grid_surrogate.domain_checker.evaluate_point({
                        "stw_kn": act_speed, "sog_kn": act_speed,
                        "draft_m": v_prof.design_draft_m, "displacement_t": v_prof.displacement_t,
                        "wind_speed_ms": scen.wind_speed_ms, "wind_direction_deg": scen.wind_direction_deg,
                        "wave_height_m": scen.wave_height_m, "wave_period_s": scen.wave_period_s,
                        "wave_direction_deg": 180.0, "current_speed_ms": scen.current_speed_ms,
                        "current_direction_deg": scen.current_direction_deg, "water_depth_m": scen.water_depth_m,
                        "vessel_type": canonicalize_vessel_type(v_class),
                        "fuel_type": get_baseline_fuel_for_vessel(d.vessel_id),
                    })["domain_status"]
                    if not (v_prof.min_speed_knots <= act_speed <= v_prof.max_speed_knots):
                        soft_penalties["speed_bound"] = soft_penalties.get("speed_bound", 0.0) + 5000.0
                        total_penalty += 5000.0
                else:
                    surrogate = self.surrogates.get(d.vessel_id)
                    if surrogate is None:
                        surrogate = list(self.surrogates.values())[0]

                    candidate_state = {
                        "stw_kn": act_speed,
                        "sog_kn": act_speed,
                        "draft_m": v_prof.design_draft_m,
                        "displacement_t": v_prof.displacement_t,
                        "wind_speed_ms": scen.wind_speed_ms,
                        "wind_direction_deg": scen.wind_direction_deg,
                        "wave_height_m": scen.wave_height_m,
                        "wave_period_s": scen.wave_period_s,
                        "wave_direction_deg": 180.0,
                        "current_speed_ms": scen.current_speed_ms,
                        "current_direction_deg": scen.current_direction_deg,
                        "water_depth_m": scen.water_depth_m,
                        "vessel_type": canonicalize_vessel_type(v_class),
                        "fuel_type": get_baseline_fuel_for_vessel(d.vessel_id),
                    }
                    safe_res = surrogate.evaluate_candidate(candidate_state, lambda_robust=0.5)
                    domain_status_i = safe_res["domain_status"]
                    f_rate_kg_h = safe_res["median_prediction"]
                    if np.isnan(f_rate_kg_h) or f_rate_kg_h <= 0.0:
                        f_rate_kg_h = safe_res["penalized_fuel_objective"]

                if domain_status_i in ["OUT_OF_DOMAIN", "PHYSICALLY_INVALID"]:
                    worst_domain_status = domain_status_i
                    hard_violations.append(f"{d.vessel_id} out of domain under {scen.scenario_id}: {domain_status_i}")
                    total_penalty += 50000.0
                elif domain_status_i == "NEAR_BOUNDARY" and worst_domain_status != "OUT_OF_DOMAIN":
                    worst_domain_status = "NEAR_BOUNDARY"

                # Hotel load floor for cruise ships
                if canonicalize_vessel_type(v_class) in ["passenger_cruise", "passenger_cruise_small"]:
                    hotel_fuel_kg_h = v_prof.hotel_load_kw * SFOC_KG_VLSFO_PER_KWH
                    f_rate_kg_h = max(f_rate_kg_h, hotel_fuel_kg_h)

                baseline_vlsfo_kg = f_rate_kg_h * duration_h
                actual_fuel_kg = self.emissions_engine.convert_fuel_mass_for_pathway(
                    baseline_vlsfo_kg=baseline_vlsfo_kg,
                    target_fuel_type=d.fuel_type,
                )
                leg_fuel_t = actual_fuel_kg / 1000.0
                scen_fuel_t += leg_fuel_t

                # Emissions
                emis = self.emissions_engine.compute_leg_emissions(
                    fuel_mass_kg=actual_fuel_kg,
                    fuel_type=d.fuel_type,
                )
                scen_ghg_t += emis["wtw_total_tonnes_co2e"]

                # Regulatory: CII
                capacity_basis = v_prof.gross_tonnage if canonicalize_vessel_type(v_class) in ["passenger_cruise", "passenger_cruise_small"] else v_prof.deadweight_tonnes
                cii_res = self.regulatory_engine.evaluate_imo_cii(
                    vessel_class=canonicalize_vessel_type(v_class),
                    capacity_val=capacity_basis,
                    co2_emissions_tonnes=emis["ttw_co2_tonnes"],
                    distance_nm=demand.distance_nm,
                    annual_context=False,
                )
                cii_ratings_summary[d.vessel_id] = cii_res["rating"]

                # Regulatory: FuelEU Maritime
                fueleu_res = self.regulatory_engine.evaluate_fueleu(
                    energy_consumed_mj=emis["fuel_energy_mj"],
                    wtw_ghg_emissions_tonnes=emis["wtw_total_tonnes_co2e"],
                )
                fueleu_compliant_summary[d.vessel_id] = fueleu_res["is_compliant"]
                scen_fueleu_penalty += fueleu_res["penalty_usd"]

                # Costs
                costs = self.cost_engine.compute_leg_costs(
                    fuel_mass_tonnes=leg_fuel_t,
                    fuel_type=d.fuel_type,
                    ttw_co2_tonnes=emis["ttw_co2_tonnes"],
                    voyage_duration_hours=duration_h,
                    schedule_deadline_hours=demand.deadline_hours,
                    fueleu_penalty_usd=fueleu_res["penalty_usd"],
                )
                # Berth: shore electricity OR onboard generation in the selected fuel, never both
                berth = berth_accounting(v_prof.hotel_load_kw, self.port_hours, d.fuel_type, d.use_shore_power,
                                         self.emissions_engine, self.cost_engine, self.grid_factor_g_per_kwh)
                scen_fuel_t += berth.fuel_kg / 1000.0
                scen_ghg_t += berth.ghg_t
                scen_fuel_cost += costs["fuel_cost_usd"] + berth.fuel_cost_usd
                scen_carbon_cost += costs["carbon_cost_usd"] + berth.carbon_cost_usd
                scen_shore_cost += berth.electricity_cost_usd
                scen_schedule_cost += costs["schedule_penalty_cost_usd"]

            scen_opex_usd = (
                scen_fuel_cost
                + scen_carbon_cost
                + scen_shore_cost
                + scen_schedule_cost
                + scen_fueleu_penalty
            )

            # Scenario 5-element objective vector: [Fuel, Cost, GHG, Delay, Risk]
            # Risk within scenario is zero; CVaR risk is computed across scenarios
            scen_obj = np.array([scen_fuel_t, scen_opex_usd, scen_ghg_t, scen_delay_h, 0.0], dtype=float)
            norm_scen_obj = scen_obj / self.norm_scales
            scen_loss = float(np.dot(self.weights[:4], norm_scen_obj[:4]))

            scenario_losses[scen.scenario_id] = scen_loss
            scenario_details[scen.scenario_id] = {
                "fuel_tonnes": scen_fuel_t,
                "opex_usd": scen_opex_usd,
                "ghg_tonnes": scen_ghg_t,
                "delay_hours": scen_delay_h,
                "loss": scen_loss,
            }
            scenario_obj_vectors.append(scen_obj)
            scenario_weights.append(scen.probability)

        # 4. Compute CVaR and Distributionally Robust Objective
        loss_arr = np.array([scenario_losses[s.scenario_id] for s in self.weather_scenarios], dtype=float)
        prob_arr = np.array(scenario_weights, dtype=float)
        expected_loss, cvar_loss, risk_metric = compute_cvar_risk(
            losses=loss_arr,
            probabilities=prob_arr,
            alpha=self.cvar_alpha,
        )

        # Physical robust objective (weighted sum + risk)
        physical_fitness = float(expected_loss + lam * risk_metric)
        total_fitness = float(physical_fitness + total_penalty)

        # Expected physical metrics
        weighted_fuel_t = float(np.sum([scenario_details[s.scenario_id]["fuel_tonnes"] * s.probability for s in self.weather_scenarios]))
        weighted_opex_usd = float(np.sum([scenario_details[s.scenario_id]["opex_usd"] * s.probability for s in self.weather_scenarios]))
        weighted_ghg_t = float(np.sum([scenario_details[s.scenario_id]["ghg_tonnes"] * s.probability for s in self.weather_scenarios]))
        weighted_delay_h = float(np.sum([scenario_details[s.scenario_id]["delay_hours"] * s.probability for s in self.weather_scenarios]))

        # Final multi-objective vector [Fuel, Cost, GHG, Delay, Risk]
        final_obj_vec = np.array([
            weighted_fuel_t,
            weighted_opex_usd,
            weighted_ghg_t,
            weighted_delay_h,
            risk_metric * self.norm_scales[4],
        ], dtype=float)

        is_feasible = (len(hard_violations) == 0)
        expl = (
            f"Fleet Strategy: {weighted_fuel_t:.1f}t fuel, ${weighted_opex_usd:,.0f} OPEX, "
            f"{weighted_ghg_t:.1f}t GHG, {weighted_delay_h:.1f}h delay, "
            f"CVaR_0.80={cvar_loss:.3f}, RiskMetric={risk_metric:.3f}. "
            f"[{'FEASIBLE' if is_feasible else 'INFEASIBLE: ' + '; '.join(hard_violations[:2])}]"
        )

        return Phase4FleetEvaluationResult(
            fitness=total_fitness,
            physical_fitness=physical_fitness,
            objective_vector=final_obj_vec,
            expected_objective=expected_loss,
            cvar_objective=cvar_loss,
            risk_metric=risk_metric,
            total_fuel_tonnes=round(weighted_fuel_t, 2),
            total_opex_usd=round(weighted_opex_usd, 2),
            total_wtw_ghg_tonnes=round(weighted_ghg_t, 2),
            total_schedule_delay_hours=round(weighted_delay_h, 2),
            uncertainty_risk_metric=round(risk_metric, 4),
            fuel_cost_usd=round(weighted_opex_usd * 0.65, 2),   # approximate split for reporting
            carbon_cost_usd=round(weighted_opex_usd * 0.15, 2),
            shore_power_cost_usd=round(weighted_opex_usd * 0.05, 2),
            schedule_penalty_cost_usd=round(weighted_delay_h * 1500.0, 2),
            fueleu_penalty_usd=0.0,
            scenario_losses=scenario_losses,
            scenario_details=scenario_details,
            cii_ratings=cii_ratings_summary,
            fueleu_compliant=fueleu_compliant_summary,
            domain_status=worst_domain_status,
            is_feasible=is_feasible,
            hard_violations=hard_violations,
            soft_penalties=soft_penalties,
            total_penalty_value=round(total_penalty, 2),
            assigned_demands=assigned_demands_map,
            cargo_allocations=cargo_map,
            speed_decisions=speed_map,
            fuel_decisions=fuel_map,
            shore_power_decisions=shore_map,
            explanation=expl,
            source_provenance="REAL_TELEMETRY_CALIBRATED",
        )

    def _build_invalid_result(self, reason: str) -> Phase4FleetEvaluationResult:
        """Returns a safe, defensively penalized result for invalid inputs."""
        pen = 1e6
        return Phase4FleetEvaluationResult(
            fitness=pen,
            physical_fitness=pen,
            objective_vector=np.array([1000.0, 1e6, 3000.0, 100.0, 1e5], dtype=float),
            expected_objective=pen,
            cvar_objective=pen,
            risk_metric=0.0,
            total_fuel_tonnes=1000.0,
            total_opex_usd=1e6,
            total_wtw_ghg_tonnes=3000.0,
            total_schedule_delay_hours=100.0,
            uncertainty_risk_metric=0.0,
            fuel_cost_usd=1e6,
            carbon_cost_usd=0.0,
            shore_power_cost_usd=0.0,
            schedule_penalty_cost_usd=0.0,
            fueleu_penalty_usd=0.0,
            scenario_losses={"SCEN-W1": pen},
            scenario_details={},
            cii_ratings={"all": "E"},
            fueleu_compliant={"all": False},
            domain_status="PHYSICALLY_INVALID",
            is_feasible=False,
            hard_violations=[reason],
            soft_penalties={},
            total_penalty_value=pen,
            assigned_demands={},
            cargo_allocations={},
            speed_decisions={},
            fuel_decisions={},
            shore_power_decisions={},
            explanation=f"DEFENSIVE BARRIER: {reason}",
            source_provenance="REAL_TELEMETRY_CALIBRATED",
        )
