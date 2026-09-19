"""
Quantum-Inspired Prediction Engine (SIH26138 - Phase 6).
Provides genuine quantum-inspired algorithms and matched classical controls for
maritime fuel and energy prediction.
"""

from .qiea import QIEAFeatureSelector, QBitChromosome
from .qpso import QPSOOptimizer, ClassicalPSOOptimizer, RandomSearchOptimizer
from .mps_predictor import QIMPSPredictor, ClassicalPolyPredictor
from .feature_selection import FeatureSelectionBenchmark
from .validation import ValidationHarness
from .statistics import PredictionStatisticsEngine

__all__ = [
    "QIEAFeatureSelector",
    "QBitChromosome",
    "QPSOOptimizer",
    "ClassicalPSOOptimizer",
    "RandomSearchOptimizer",
    "QIMPSPredictor",
    "ClassicalPolyPredictor",
    "FeatureSelectionBenchmark",
    "ValidationHarness",
    "PredictionStatisticsEngine",
]
