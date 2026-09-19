"""
Common Optimizer Interface and Result Structure for Phase 5 Benchmark.
Every optimizer (A0-A5, DE, PSO, GA, Random) implements this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


@dataclass
class OptimizationResult:
    """Comprehensive, scientifically auditable result of a benchmark optimization run."""
    algorithm: str
    seed: int
    run_id: str
    runtime_seconds: float
    objective_evaluations: int
    iterations: int

    # Best solution found
    best_x: np.ndarray
    best_fitness: float
    best_physical_objective: float
    best_penalty: float
    feasible_at_end: bool
    best_output: Optional[EvaluationOutput] = None

    # Feasibility tracking
    first_feasible_evaluation: int = -1
    first_feasible_iteration: int = -1
    number_of_feasible_evaluations: int = 0
    candidate_level_feasibility_rate: float = 0.0

    # Constraint violations
    constraint_violation_total: float = 0.0
    hard_violations: List[str] = field(default_factory=list)

    # Diagnostics & Diversity
    convergence_trajectory: List[float] = field(default_factory=list)
    eval_trajectory: List[int] = field(default_factory=list)
    population_diversity: List[float] = field(default_factory=list)
    categorical_entropy: List[float] = field(default_factory=list)
    repair_count: int = 0
    repair_rate: float = 0.0
    unique_solution_count: int = 0

    # Multi-objective & Pareto metrics
    pareto_archive_size: int = 0
    pareto_hypervolume: float = 0.0

    # Operational decisions
    assigned_demands: Dict[str, str] = field(default_factory=dict)
    fuel_decisions: Dict[str, str] = field(default_factory=dict)
    speed_decisions: Dict[str, float] = field(default_factory=dict)


class BaseFleetOptimizer(ABC):
    """Abstract base class for all fleet optimization algorithms."""

    def __init__(self, name: str, seed: int = 42):
        self.name = name
        self.seed = seed

    @abstractmethod
    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        """Executes optimization within strict evaluation budget."""
        pass
