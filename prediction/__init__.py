"""
Fuel consumption prediction engine:
Physics-only, ML-only, Physics+ML residual hybrid, QPSO & Random Search model selection,
quantile uncertainty estimation, and diagnostic error analysis.
"""

from .physics_predictor import PhysicsFuelPredictor
from .ml_baseline import PureMLPredictor
from .residual_model import HybridResidualPredictor
from .qpso_model_selection import QPSOModelSelector, RandomSearchModelSelector
from .quantile_model import QuantileUncertaintyPredictor
from .error_analysis import DiagnosticErrorAnalyzer
from .evaluate import evaluate_predictions, evaluate_quantiles, compute_pinball_loss

from .domain_checker import DomainChecker
from .safe_objective import SafeFuelObjective

# Aliases for Phase 0 backwards compatibility
PhysicsOnlyPredictor = PhysicsFuelPredictor
PureMLBaselinePredictor = PureMLPredictor
HybridPhysicsMLPredictor = HybridResidualPredictor

__all__ = [
    "PhysicsFuelPredictor",
    "PureMLPredictor",
    "HybridResidualPredictor",
    "QPSOModelSelector",
    "RandomSearchModelSelector",
    "QuantileUncertaintyPredictor",
    "DiagnosticErrorAnalyzer",
    "DomainChecker",
    "SafeFuelObjective",
    "evaluate_predictions",
    "evaluate_quantiles",
    "compute_pinball_loss",
    "PhysicsOnlyPredictor",
    "PureMLBaselinePredictor",
    "HybridPhysicsMLPredictor",
]
