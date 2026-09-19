"""
Constraint System for Green Fleet Optimization.
Implements formal separation between Hard Constraints (strict feasibility rejection)
and Soft Constraints (smooth quadratic objective penalization).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class ConstraintAuditResult:
    is_feasible: bool
    hard_violations: List[str] = field(default_factory=list)
    soft_penalties: Dict[str, float] = field(default_factory=dict)
    total_penalty_value: float = 0.0

    def summary(self) -> str:
        if self.is_feasible:
            return "FEASIBLE"
        return f"INFEASIBLE: {'; '.join(self.hard_violations)}"


class FleetConstraintManager:
    """
    Validates physical, operational, and regulatory constraints.
    """

    def __init__(
        self,
        penalty_multiplier: float = 1e5,
        boundary_soft_penalty: float = 25.0,
    ):
        self.penalty_multiplier = penalty_multiplier
        self.boundary_soft_penalty = boundary_soft_penalty

    def validate_candidate(
        self,
        vessel_id: str,
        vessel_profile: Dict[str, Any],
        speed_knots: float,
        cargo_allocation: float,
        fuel_type: str,
        domain_status: str,
        envelope_distance: float,
        voyage_duration_hours: float,
        schedule_deadline_hours: float,
        required_cargo_demand: float = 0.0,
        cii_rating: str = "C",
        fueleu_compliant: bool = True,
    ) -> ConstraintAuditResult:
        """
        Evaluate all constraints for a candidate solution.
        """
        hard_violations = []
        soft_penalties = {}
        total_penalty = 0.0

        # 1. HARD: Domain Validity Envelope
        if domain_status in ["OUT_OF_DOMAIN", "PHYSICALLY_INVALID"]:
            hard_violations.append(
                f"Domain violation: status={domain_status}, envelope_distance={envelope_distance:.2f}"
            )
            total_penalty += self.penalty_multiplier * (1.0 + envelope_distance)

        # 2. HARD: Speed Boundaries
        min_spd = vessel_profile.get("min_speed_knots", 4.0)
        max_spd = vessel_profile.get("max_speed_knots", 22.0)
        if speed_knots < min_spd or speed_knots > max_spd:
            hard_violations.append(
                f"Speed violation: {speed_knots:.1f} kn outside [{min_spd}, {max_spd}]"
            )
            total_penalty += self.penalty_multiplier * 0.5

        # 3. HARD: Cargo Capacity
        max_cap = vessel_profile.get("deadweight_tonnes", vessel_profile.get("max_teu_capacity", 10000.0))
        if cargo_allocation > max_cap:
            hard_violations.append(
                f"Capacity overload: {cargo_allocation:.1f} > max {max_cap:.1f}"
            )
            total_penalty += self.penalty_multiplier * 0.5

        # 4. HARD: Fuel Compatibility
        compat_fuels = vessel_profile.get("compatible_fuels", ["vlsfo"])
        if fuel_type.lower() not in [f.lower() for f in compat_fuels]:
            hard_violations.append(
                f"Fuel incompatibility: {fuel_type} not in {compat_fuels}"
            )
            total_penalty += self.penalty_multiplier * 0.5

        # 5. SOFT: Domain Boundary Proximity
        if domain_status == "NEAR_BOUNDARY":
            b_pen = self.boundary_soft_penalty * max(0.0, envelope_distance)
            soft_penalties["boundary_proximity"] = b_pen
            total_penalty += b_pen

        # 6. SOFT: Schedule Delay
        if voyage_duration_hours > schedule_deadline_hours:
            delay_h = voyage_duration_hours - schedule_deadline_hours
            s_pen = 1000.0 * (delay_h ** 1.5)  # Progressive delay penalty
            soft_penalties["schedule_delay"] = s_pen
            total_penalty += s_pen

        # 7. SOFT: Regulatory Non-Compliance
        if cii_rating in ["D", "E"]:
            c_pen = 5000.0 if cii_rating == "D" else 15000.0
            soft_penalties["cii_non_compliance"] = c_pen
            total_penalty += c_pen

        if not fueleu_compliant:
            soft_penalties["fueleu_deficit"] = 2500.0
            total_penalty += 2500.0

        is_feasible = (len(hard_violations) == 0)
        return ConstraintAuditResult(
            is_feasible=is_feasible,
            hard_violations=hard_violations,
            soft_penalties=soft_penalties,
            total_penalty_value=total_penalty,
        )
