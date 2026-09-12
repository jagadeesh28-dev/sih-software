"""
Reproducible Experiment Suite for SIH26138.
EXP01: Fuel prediction benchmark (Physics vs ML vs Hybrid)
EXP02: Cross-vessel generalization
EXP03: Alternative fuel transition
EXP04: Weather / CVaR schedule delay risk
EXP05: Carbon price sensitivity sweep ($0 - $150/t)
EXP06: QPSO vs Classical optimization benchmark
"""

__all__ = [
    "exp01_prediction",
    "exp02_cross_vessel",
    "exp03_fuel_transition",
    "exp04_weather_risk",
    "exp05_carbon_sensitivity",
    "exp06_qpso_benchmark",
]
