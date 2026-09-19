"""
Unit tests for FleetConstraintManager: hard rejection and soft penalty evaluation.
"""

import pytest
from optimization.constraints import FleetConstraintManager


def test_hard_constraint_domain_rejection():
    """Verify that OUT_OF_DOMAIN states trigger hard infeasibility."""
    mgr = FleetConstraintManager(penalty_multiplier=1e5)
    v_prof = {"min_speed_knots": 8.0, "max_speed_knots": 22.0, "deadweight_tonnes": 8500.0, "compatible_fuels": ["vlsfo"]}

    res = mgr.validate_candidate(
        vessel_id="CPS_Poseidon",
        vessel_profile=v_prof,
        speed_knots=18.0,
        cargo_allocation=5000.0,
        fuel_type="vlsfo",
        domain_status="OUT_OF_DOMAIN",
        envelope_distance=2.5,
        voyage_duration_hours=20.0,
        schedule_deadline_hours=24.0,
    )

    assert res.is_feasible is False
    assert len(res.hard_violations) > 0
    assert any("Domain violation" in v for v in res.hard_violations)
    assert res.total_penalty_value >= 1e5


def test_hard_constraint_fuel_incompatibility():
    """Verify that incompatible fuel assignments trigger hard infeasibility."""
    mgr = FleetConstraintManager()
    v_prof = {"min_speed_knots": 8.0, "max_speed_knots": 22.0, "deadweight_tonnes": 8500.0, "compatible_fuels": ["vlsfo"]}

    res = mgr.validate_candidate(
        vessel_id="CPS_Poseidon",
        vessel_profile=v_prof,
        speed_knots=18.0,
        cargo_allocation=5000.0,
        fuel_type="green_ammonia",  # Not compatible
        domain_status="VALID",
        envelope_distance=0.0,
        voyage_duration_hours=20.0,
        schedule_deadline_hours=24.0,
    )

    assert res.is_feasible is False
    assert any("Fuel incompatibility" in v for v in res.hard_violations)


def test_soft_constraint_schedule_delay_penalty():
    """Verify that schedule delays incur smooth soft penalties without hard infeasibility."""
    mgr = FleetConstraintManager()
    v_prof = {"min_speed_knots": 8.0, "max_speed_knots": 22.0, "deadweight_tonnes": 8500.0, "compatible_fuels": ["vlsfo"]}

    res = mgr.validate_candidate(
        vessel_id="CPS_Poseidon",
        vessel_profile=v_prof,
        speed_knots=18.0,
        cargo_allocation=5000.0,
        fuel_type="vlsfo",
        domain_status="VALID",
        envelope_distance=0.0,
        voyage_duration_hours=28.0,  # 4 hours late
        schedule_deadline_hours=24.0,
    )

    assert res.is_feasible is True  # Soft constraint does not invalidate feasibility
    assert "schedule_delay" in res.soft_penalties
    assert res.soft_penalties["schedule_delay"] > 0.0
