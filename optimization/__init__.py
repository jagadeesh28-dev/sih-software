"""
Mixed-Variable Stochastic Fleet Optimization and Benchmarking.
Implements QPSO, Canonical PSO, GA, DE, Random Search, Pareto Analysis,
FleetEvaluationEngine, emissions, regulatory, cost, and voyage kinematics.
"""

from .variables import (
    VesselAssignmentDecision,
    SolutionChromosome,
    FUEL_MAP,
    REV_FUEL_MAP,
    MODE_MAP,
    REV_MODE_MAP,
)
from .qpso import QPSOOptimizer
from .pso import CanonicalPSOOptimizer
from .genetic_algorithm import GeneticAlgorithmOptimizer
from .differential_evolution import DifferentialEvolutionOptimizer
from .random_search import RandomSearchOptimizer
from .pareto import (
    non_dominated_sort,
    compute_hypervolume_2d,
    compute_generational_distance,
    compute_inverted_generational_distance,
    compute_spacing_metric,
    select_compromise_presets,
)
from .emissions_model import FleetEmissionsEngine
from .cost_model import FleetCostEngine
from .regulatory import FleetRegulatoryEngine
from .voyage_model import VoyageKinematicsEngine
from .constraints import FleetConstraintManager, ConstraintAuditResult
from .evaluator import FleetEvaluationEngine, FleetEvaluationResult
from .scenarios import VoyageScenario, BENCHMARK_SCENARIOS, create_baseline_policy

# Legacy exports for backwards compatibility
from .problem import MaritimeFleetProblem
from .objective import evaluate_fleet_objectives
from .cvar import compute_schedule_delay_cvar
from .nsga3 import NSGA3Optimizer
from .moead import MOEADOptimizer
from .milp_baseline import SmallInstanceMILPBaseline

__all__ = [
    "VesselAssignmentDecision",
    "SolutionChromosome",
    "FUEL_MAP",
    "REV_FUEL_MAP",
    "MODE_MAP",
    "REV_MODE_MAP",
    "QPSOOptimizer",
    "CanonicalPSOOptimizer",
    "GeneticAlgorithmOptimizer",
    "DifferentialEvolutionOptimizer",
    "RandomSearchOptimizer",
    "non_dominated_sort",
    "compute_hypervolume_2d",
    "compute_generational_distance",
    "compute_inverted_generational_distance",
    "compute_spacing_metric",
    "select_compromise_presets",
    "FleetEmissionsEngine",
    "FleetCostEngine",
    "FleetRegulatoryEngine",
    "VoyageKinematicsEngine",
    "FleetConstraintManager",
    "ConstraintAuditResult",
    "FleetEvaluationEngine",
    "FleetEvaluationResult",
    "VoyageScenario",
    "BENCHMARK_SCENARIOS",
    "create_baseline_policy",
    "MaritimeFleetProblem",
    "evaluate_fleet_objectives",
    "compute_schedule_delay_cvar",
    "NSGA3Optimizer",
    "MOEADOptimizer",
    "SmallInstanceMILPBaseline",
]
