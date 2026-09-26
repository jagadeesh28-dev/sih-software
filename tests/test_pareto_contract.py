"""
Optimizer formulation and Pareto-front contract.

- Stationary modes (port / dp) cannot complete an assigned voyage leg.
- The carried cargo of an assigned vessel is the assigned demand's quantity.
- NSGA-III is a real multi-objective search whose archive only holds penalty-free plans.
- Every stored Pareto point is hard-feasible, penalty-free, in its speed band, uses a compatible
  fuel, is mutually non-dominated, and re-evaluates to its stored objectives.
"""

import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from experiments.exp_phase3_master_runner import load_real_surrogates
from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
from optimization.fleet_heterogeneous import FLEET_VESSELS, OPERATIONAL_DEMANDS, decode_fleet_vector
from optimization.variables import REV_MODE_MAP
from src.algorithms.nsga3 import NSGA3Optimizer
from src.benchmark.metrics import is_pareto_efficient
from src.evaluator.common_evaluator import CommonFleetEvaluator

FRONT = Path(__file__).resolve().parents[1] / "results" / "pareto_front.csv"
VESSELS = [FLEET_VESSELS["CPS_Poseidon"], FLEET_VESSELS["CPS_Triton"], FLEET_VESSELS["OSS_Ceto"]]


@pytest.fixture(scope="module")
def evaluator():
    ev = Phase4FleetEvaluator(surrogates=load_real_surrogates())
    ev.weights = np.array([0.35, 0.35, 0.30, 0.0, 0.0])
    return ev


@pytest.fixture(scope="module")
def front():
    return pd.read_csv(FRONT)


def _front_vector(front):
    return np.asarray(json.loads(front.iloc[0]["x_vector"]), dtype=float)


@pytest.mark.parametrize("mode", ["port", "dp"])
def test_stationary_mode_cannot_complete_assigned_leg(evaluator, front, mode):
    x = _front_vector(front)
    x[4] = REV_MODE_MAP[mode]  # CPS_Poseidon operating mode
    res = evaluator.evaluate_vector(x)
    assert not res.is_feasible
    assert any("cannot complete" in h for h in res.hard_violations)


def test_carried_cargo_is_the_assigned_demand(front):
    x = _front_vector(front)
    x[1] = 0.0  # raw cargo gene is inert
    for d in decode_fleet_vector(x, VESSELS):
        assert d.cargo_tonnes == OPERATIONAL_DEMANDS[d.assigned_demand].cargo_quantity_tonnes


def test_nsga3_archive_is_penalty_free_and_population_evolves(evaluator):
    xl, xu = evaluator.get_bounds()
    opt = NSGA3Optimizer(seed=1001, population_size=50, max_generations=20, init="structured")
    res = opt.optimize(CommonFleetEvaluator(copy.deepcopy(evaluator), max_budget=1000), xl, xu, budget=1000)
    assert res.objective_evaluations == 1000
    assert opt.pareto_archive, "structured NSGA-III found no penalty-free plan in 1,000 evaluations"
    assert all(o.is_feasible and o.penalty <= 0.0 for _, _, o in opt.pareto_archive)
    # selection must improve on the initial population (the old implementation never replaced it)
    assert res.convergence_trajectory[-1] < res.convergence_trajectory[0]


def test_stored_front_contract(evaluator, front):
    assert len(front) >= 1
    assert front["is_feasible"].astype(str).str.lower().eq("true").all()
    assert (front["penalty"] <= 0.0).all()
    objs = front[["fuel_tonnes", "cost_usd", "ghg_tonnes"]].values
    assert is_pareto_efficient(objs).all()
    assert len(np.unique(objs, axis=0)) == len(front)
    ce = CommonFleetEvaluator(copy.deepcopy(evaluator), max_budget=len(front))
    for _, row in front.iterrows():
        out = ce.evaluate(np.asarray(json.loads(row["x_vector"]), dtype=float))
        assert out.is_feasible and out.penalty <= 0.0
        assert abs(out.fuel_tonnes - row["fuel_tonnes"]) <= 0.01
        assert abs(out.opex_usd - row["cost_usd"]) <= 0.01
        assert abs(out.ghg_tonnes - row["ghg_tonnes"]) <= 0.01
        for v in VESSELS:
            assert v.min_speed_knots <= out.speed_decisions[v.vessel_id] <= v.max_speed_knots
            assert out.fuel_decisions[v.vessel_id] in v.compatible_fuels
