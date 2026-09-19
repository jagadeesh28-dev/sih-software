"""
Master Fleet Evaluation Engine.
Integrates SafeFuelObjective, DomainChecker, FleetEmissionsEngine, FleetCostEngine,
FleetRegulatoryEngine, VoyageKinematicsEngine, and FleetConstraintManager.
Guarantees defensive evaluation: candidate states never bypass SafeFuelObjective.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from prediction.safe_objective import SafeFuelObjective
from prediction.domain_checker import DomainChecker
from .emissions_model import FleetEmissionsEngine
from .cost_model import FleetCostEngine
from .regulatory import FleetRegulatoryEngine
from .voyage_model import VoyageKinematicsEngine
from .constraints import FleetConstraintManager, ConstraintAuditResult
from .variables import SolutionChromosome, VesselAssignmentDecision
from .canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type, get_baseline_fuel_for_vessel


@dataclass
class FleetEvaluationResult:
    """Complete, transparent record of a candidate strategy evaluation."""
    fitness: float
    objective_vector: np.ndarray  # [Fuel (t), Cost ($), WtW GHG (t), Delay (h), Risk (t)]

    # Detailed metrics
    total_fuel_tonnes: float
    total_opex_usd: float
    total_wtw_ghg_tonnes: float
    voyage_duration_hours: float
    schedule_delay_hours: float
    uncertainty_risk_tonnes: float

    # Sub-components
    fuel_cost_usd: float
    carbon_cost_usd: float
    shore_power_cost_usd: float
    schedule_penalty_cost_usd: float
    fueleu_penalty_usd: float

    # Regulatory outcomes
    cii_rating: str
    cii_margin_pct: float
    fueleu_compliant: bool
    fueleu_intensity_g_mj: float

    # Feasibility and diagnostics
    domain_status: str
    is_feasible: bool
    hard_violations: List[str]
    soft_penalties: Dict[str, float]
    total_penalty_value: float
    explanation: str


class FleetEvaluationEngine:
    """
    Evaluates candidate fleet operating strategies.
    Every fuel query is routed through SafeFuelObjective to intercept out-of-domain exploits.
    """

    def __init__(
        self,
        safe_objective: SafeFuelObjective,
        emissions_engine: Optional[FleetEmissionsEngine] = None,
        cost_engine: Optional[FleetCostEngine] = None,
        regulatory_engine: Optional[FleetRegulatoryEngine] = None,
        kinematics_engine: Optional[VoyageKinematicsEngine] = None,
        constraint_manager: Optional[FleetConstraintManager] = None,
        fleet_profiles: Optional[Dict[str, Any]] = None,
        weights: Optional[np.ndarray] = None,
        lambda_robust: float = 0.5,
    ):
        self.safe_objective = safe_objective
        self.emissions_engine = emissions_engine or FleetEmissionsEngine()
        self.cost_engine = cost_engine or FleetCostEngine()
        self.regulatory_engine = regulatory_engine or FleetRegulatoryEngine()
        self.kinematics_engine = kinematics_engine or VoyageKinematicsEngine()
        self.constraint_manager = constraint_manager or FleetConstraintManager()
        self.fleet_profiles = fleet_profiles or {}
        self.weights = weights if weights is not None else np.array([0.30, 0.30, 0.25, 0.10, 0.05])
        self.lambda_robust = lambda_robust

        # Cache reference normalization scales
        self.norm_scales = np.array([50.0, 50000.0, 150.0, 10.0, 15.0])

    def _get_vessel_profile(self, vessel_id: str) -> Dict[str, Any]:
        """Look up vessel profile or provide sensible maritime defaults."""
        for c_name, c_data in self.fleet_profiles.get("vessel_classes", {}).items():
            if vessel_id in c_data.get("vessels", {}):
                prof = dict(c_data["vessels"][vessel_id])
                prof["class_family"] = canonicalize_vessel_type(c_name)
                return prof

        # Defaults for known FuelCast ships
        if "poseidon" in vessel_id.lower():
            return {
                "class_family": "passenger_cruise",
                "gross_tonnage": 70000.0,
                "deadweight_tonnes": 8500.0,
                "design_draft_m": 7.5,
                "displacement_t": 42000.0,
                "min_speed_knots": 8.0,
                "max_speed_knots": 22.0,
                "hotel_load_baseline_kw": 6500.0,
                "compatible_fuels": ["vlsfo", "bio_methanol", "fossil_lng"],
            }
        elif "triton" in vessel_id.lower():
            return {
                "class_family": "passenger_cruise_small",
                "gross_tonnage": 11000.0,
                "deadweight_tonnes": 1800.0,
                "design_draft_m": 5.0,
                "displacement_t": 8500.0,
                "min_speed_knots": 6.0,
                "max_speed_knots": 18.0,
                "hotel_load_baseline_kw": 1800.0,
                "compatible_fuels": ["vlsfo", "bio_methanol"],
            }
        elif "ceto" in vessel_id.lower():
            return {
                "class_family": "offshore_supply",
                "gross_tonnage": 24000.0,
                "deadweight_tonnes": 5200.0,
                "design_draft_m": 6.0,
                "displacement_t": 6000.0,
                "min_speed_knots": 4.0,
                "max_speed_knots": 15.0,
                "hotel_load_baseline_kw": 800.0,
                "compatible_fuels": ["vlsfo", "mgo", "bio_methanol", "green_ammonia"],
            }
        else:
            return {
                "class_family": "cargo_feeder",
                "gross_tonnage": 12000.0,
                "deadweight_tonnes": 14000.0,
                "design_draft_m": 8.5,
                "displacement_t": 20000.0,
                "min_speed_knots": 10.0,
                "max_speed_knots": 19.0,
                "hotel_load_baseline_kw": 600.0,
                "compatible_fuels": ["vlsfo", "fossil_lng", "bio_methanol", "green_ammonia", "liquid_hydrogen"],
            }

    def evaluate_chromosome(
        self,
        chromosome: SolutionChromosome,
        voyage_distance_nm: float,
        schedule_deadline_hours: float,
        wave_height_m: float = 1.5,
        wave_period_s: float = 7.5,
        wind_speed_ms: float = 8.0,
        current_speed_ms: float = 0.5,
        water_depth_m: float = 100.0,
        cargo_demand_tonnes: float = 0.0,
        lambda_robust: Optional[float] = None,
    ) -> FleetEvaluationResult:
        """
        Evaluate candidate strategy chromosome across all legs and vessels.
        """
        lam = lambda_robust if lambda_robust is not None else self.lambda_robust
        total_fuel_t = 0.0
        total_fuel_cost = 0.0
        total_carbon_cost = 0.0
        total_shore_cost = 0.0
        total_schedule_cost = 0.0
        total_fueleu_penalty = 0.0
        total_wtw_ghg_t = 0.0
        total_dispersion_t = 0.0
        max_duration_h = 0.0
        worst_domain_status = "VALID"
        all_hard_violations = []
        all_soft_penalties = {}
        total_constraint_penalty = 0.0
        primary_cii_rating = "C"
        primary_fueleu_intensity = 0.0
        primary_fueleu_compliant = True

        for decision in chromosome.assignments:
            if not decision.assigned:
                continue

            v_prof = self._get_vessel_profile(decision.vessel_id)
            v_class = v_prof.get("class_family", "cruise_passenger")

            # 1. Kinematics & Involuntary Speed Loss
            kin = self.kinematics_engine.evaluate_leg_kinematics(
                distance_nm=voyage_distance_nm,
                commanded_speed_kn=decision.speed_knots,
                wave_height_m=wave_height_m,
                wind_speed_ms=wind_speed_ms,
                operating_mode=decision.operating_mode,
                vessel_class=v_class,
            )
            act_speed = kin["actual_speed_kn"]
            leg_duration_h = kin["total_duration_hours"]
            max_duration_h = max(max_duration_h, leg_duration_h)

            # 2. SafeFuelObjective Predictive Evaluation
            candidate_state = {
                "stw_kn": act_speed,
                "sog_kn": act_speed,
                "draft_m": v_prof.get("design_draft_m", 7.5),
                "displacement_t": v_prof.get("displacement_t", v_prof.get("gross_tonnage", 20000.0) * 1.2),
                "wind_speed_ms": wind_speed_ms,
                "wind_direction_deg": 180.0,
                "wave_height_m": wave_height_m,
                "wave_period_s": wave_period_s,
                "wave_direction_deg": 180.0,
                "current_speed_ms": current_speed_ms,
                "current_direction_deg": 180.0,
                "water_depth_m": water_depth_m,
                "vessel_type": canonicalize_vessel_type(v_class),
                "fuel_type": get_baseline_fuel_for_vessel(decision.vessel_id),
            }

            safe_res = self.safe_objective.evaluate_candidate(
                candidate_state,
                lambda_robust=lam,
            )

            # Extract predicted fuel rate (kg/h)
            f_rate_kg_h = safe_res["median_prediction"]
            if np.isnan(f_rate_kg_h) or f_rate_kg_h <= 0.0:
                f_rate_kg_h = safe_res["penalized_fuel_objective"]

            # Hotel baseline correction for cruise ships
            hotel_kw = v_prof.get("hotel_load_baseline_kw", 0.0)
            if canonicalize_vessel_type(v_class) in ["passenger_cruise", "passenger_cruise_small"]:
                # Ensure minimum auxiliary electrical baseline fuel (~220 g/kWh)
                hotel_fuel_kg_h = (hotel_kw * 0.220)
                f_rate_kg_h = max(f_rate_kg_h, hotel_fuel_kg_h)

            leg_vlsfo_kg = f_rate_kg_h * leg_duration_h

            # Convert to alternative fuel mass equivalent if not VLSFO
            target_fuel = decision.fuel_type.lower()
            actual_fuel_kg = self.emissions_engine.convert_fuel_mass_for_pathway(
                baseline_vlsfo_kg=leg_vlsfo_kg,
                target_fuel_type=target_fuel,
            )
            leg_fuel_t = actual_fuel_kg / 1000.0
            total_fuel_t += leg_fuel_t

            # Epistemic/aleatoric dispersion
            unc_width_kg_h = safe_res.get("uncertainty_width", 200.0)
            leg_disp_t = (unc_width_kg_h * leg_duration_h) / 1000.0
            total_dispersion_t += leg_disp_t

            # 3. Emissions Accounting
            emis = self.emissions_engine.compute_leg_emissions(
                fuel_mass_kg=actual_fuel_kg,
                fuel_type=target_fuel,
            )
            total_wtw_ghg_t += emis["wtw_total_tonnes_co2e"]

            # 4. Regulatory Compliance
            # IMO CII
            v_canon = canonicalize_vessel_type(v_class)
            capacity_basis = v_prof.get("gross_tonnage" if v_canon in ["passenger_cruise", "passenger_cruise_small"] else "deadweight_tonnes", 10000.0)
            cii_res = self.regulatory_engine.evaluate_imo_cii(
                vessel_class=v_canon,
                capacity_val=capacity_basis,
                co2_emissions_tonnes=emis["ttw_co2_tonnes"],
                distance_nm=voyage_distance_nm,
                annual_context=False,
            )
            primary_cii_rating = cii_res["rating"]

            # FuelEU Maritime
            fueleu_res = self.regulatory_engine.evaluate_fueleu(
                energy_consumed_mj=emis["fuel_energy_mj"],
                wtw_ghg_emissions_tonnes=emis["wtw_total_tonnes_co2e"],
            )
            primary_fueleu_compliant = fueleu_res["is_compliant"]
            primary_fueleu_intensity = fueleu_res["attained_intensity_g_co2e_per_mj"]
            leg_fueleu_penalty = fueleu_res["penalty_usd"]
            total_fueleu_penalty += leg_fueleu_penalty

            # 5. Cost Accounting
            costs = self.cost_engine.compute_leg_costs(
                fuel_mass_tonnes=leg_fuel_t,
                fuel_type=target_fuel,
                ttw_co2_tonnes=emis["ttw_co2_tonnes"],
                voyage_duration_hours=leg_duration_h,
                schedule_deadline_hours=schedule_deadline_hours,
                use_shore_power=decision.use_shore_power_at_dest,
                port_hours=2.0,
                hotel_load_kw=hotel_kw,
                fueleu_penalty_usd=leg_fueleu_penalty,
            )
            total_fuel_cost += costs["fuel_cost_usd"]
            total_carbon_cost += costs["carbon_cost_usd"]
            total_shore_cost += costs["shore_power_cost_usd"]
            total_schedule_cost += costs["schedule_penalty_cost_usd"]

            # 6. Constraints Validation
            c_audit = self.constraint_manager.validate_candidate(
                vessel_id=decision.vessel_id,
                vessel_profile=v_prof,
                speed_knots=decision.speed_knots,
                cargo_allocation=decision.cargo_allocation_teu,
                fuel_type=target_fuel,
                domain_status=safe_res["domain_status"],
                envelope_distance=safe_res["envelope_distance"],
                voyage_duration_hours=leg_duration_h,
                schedule_deadline_hours=schedule_deadline_hours,
                cii_rating=primary_cii_rating,
                fueleu_compliant=primary_fueleu_compliant,
            )

            if not c_audit.is_feasible:
                all_hard_violations.extend(c_audit.hard_violations)
            for k_p, v_p in c_audit.soft_penalties.items():
                all_soft_penalties[k_p] = all_soft_penalties.get(k_p, 0.0) + v_p
            total_constraint_penalty += c_audit.total_penalty_value

            if safe_res["domain_status"] in ["OUT_OF_DOMAIN", "PHYSICALLY_INVALID"]:
                worst_domain_status = safe_res["domain_status"]
            elif safe_res["domain_status"] == "NEAR_BOUNDARY" and worst_domain_status != "OUT_OF_DOMAIN":
                worst_domain_status = "NEAR_BOUNDARY"

        # Total OPEX
        total_opex = (
            total_fuel_cost
            + total_carbon_cost
            + total_shore_cost
            + total_schedule_cost
            + total_fueleu_penalty
        )

        schedule_delay_h = max(0.0, max_duration_h - schedule_deadline_hours)

        # Objective Vector
        obj_vec = np.array([
            total_fuel_t,
            total_opex,
            total_wtw_ghg_t,
            schedule_delay_h,
            total_dispersion_t,
        ], dtype=float)

        # Normalized scalar fitness
        norm_obj = obj_vec / self.norm_scales
        scalar_fitness = float(np.dot(self.weights, norm_obj) + total_constraint_penalty)

        # Explanation synthesis
        is_feasible = (len(all_hard_violations) == 0)
        expl = (
            f"Strategy evaluated: {total_fuel_t:.1f}t fuel (${total_opex:,.0f} OPEX), "
            f"{total_wtw_ghg_t:.1f}t WtW GHG, {max_duration_h:.1f}h transit "
            f"(Delay: {schedule_delay_h:.1f}h). Status: {worst_domain_status} "
            f"[{'FEASIBLE' if is_feasible else 'INFEASIBLE'}]"
        )

        return FleetEvaluationResult(
            fitness=scalar_fitness,
            objective_vector=obj_vec,
            total_fuel_tonnes=round(total_fuel_t, 2),
            total_opex_usd=round(total_opex, 2),
            total_wtw_ghg_tonnes=round(total_wtw_ghg_t, 2),
            voyage_duration_hours=round(max_duration_h, 2),
            schedule_delay_hours=round(schedule_delay_h, 2),
            uncertainty_risk_tonnes=round(total_dispersion_t, 2),
            fuel_cost_usd=round(total_fuel_cost, 2),
            carbon_cost_usd=round(total_carbon_cost, 2),
            shore_power_cost_usd=round(total_shore_cost, 2),
            schedule_penalty_cost_usd=round(total_schedule_cost, 2),
            fueleu_penalty_usd=round(total_fueleu_penalty, 2),
            cii_rating=primary_cii_rating,
            cii_margin_pct=0.0,
            fueleu_compliant=primary_fueleu_compliant,
            fueleu_intensity_g_mj=round(primary_fueleu_intensity, 2),
            domain_status=worst_domain_status,
            is_feasible=is_feasible,
            hard_violations=all_hard_violations,
            soft_penalties=all_soft_penalties,
            total_penalty_value=round(total_constraint_penalty, 2),
            explanation=expl,
        )
