# SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](tests/)

A scientifically defensible, reproducible engineering and research platform for maritime decarbonization developed for the **Smart India Hackathon 2026 (Problem Statement SIH26138)**.

---

## 1. Scientific Positioning & Research Question

### Core Research Question
> *"To what extent can an uncertainty-aware, prediction-in-the-loop green fleet optimization framework improve fuel efficiency, operational cost, lifecycle GHG emissions, and schedule robustness for heterogeneous maritime fleets, and what measurable advantage, if any, does a quantum-inspired QPSO-based optimizer provide over classical optimization methods under equal computational budgets?"*

### Scientific Guardrails
- **No Quantum Supremacy / QPU Claims**: The Quantum-behaved Particle Swarm Optimization (QPSO) algorithm is strictly formulated and implemented as a **quantum-inspired classical metaheuristic** executed on standard classical hardware. It leverages stochastic delta-potential well dynamics for enhanced exploration, not physical quantum mechanical entanglement or tunneling.
- **Fair Computational Budget**: QPSO is benchmarked against standard multi-objective evolutionary algorithms (NSGA-III, MOEA/D) and exact baselines (MILP) under identical evaluation budgets (50,000 function evaluations across 30 independent seeds, using common random numbers for metocean scenarios). **QPSO is allowed to lose.**
- **No Fabricated Data or Hard-coded KPIs**: Every metric displayed in benchmarks or the dashboard is derived from actual computational executions.
- **Dimensional & Regulatory Consistency**: Lifecycle GHG accounting follows IMO MEPC.391(81), IMO Carbon Intensity Indicator (CII) reduction factors (11% 2026 baseline), FuelEU Maritime intensity penalties, and dimensional methane slip ($g\,\text{CH}_4/\text{MJ}$).

---

## 2. Platform Architecture

```
DATA INGESTION (Schema validation, unit check, quality audit)
    ↓
PHYSICS RESISTANCE ENGINE (Holtrop-Mennen calm water + STAWAVE-2 added wave + wind)
    ↓
HYBRID FUEL PREDICTION (Physics baseline + ML residual + LightGBM Quantiles)
    ↓
UNCERTAINTY QUANTIFICATION (90% prediction intervals: q05, q50, q95, empirical PICP)
    ↓
LIFECYCLE GHG & COMPLIANCE (WtW LCA, IMO MEPC.391(81), IMO CII, FuelEU Maritime)
    ↓
STOCHASTIC FLEET OPTIMIZATION (Mixed-variable: speed, fuel, shore power, routing)
    ↓
BENCHMARK HARNESS (QPSO vs. NSGA-III vs. MOEA/D vs. MILP: 50k evals, 30 seeds)
    ↓
DECISION DASHBOARD (Streamlit multi-page interface, Pareto trade-offs, explainability)
```

---

## 3. Directory Layout

```
sih26138_platform/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── configs/               # Externalized system configurations
│   ├── physics.yaml       # Naval architecture & resistance constants
│   ├── fuels.yaml         # Well-to-Wake fuel pathway registry
│   ├── optimization.yaml  # Decision spaces, objectives & budgets
│   ├── scenarios.yaml     # Metocean, carbon price & fuel scenarios
│   └── benchmark.yaml     # 30-seed statistical evaluation protocol
│
├── evidence/              # Evidence ledger
│   └── claims.yaml        # Classified claims (FACT, HYPOTHESIS, TARGET, etc.)
│
├── common/                # Shared platform utilities
│   ├── config_loader.py   # YAML configuration parser
│   ├── logger.py          # Structured logging
│   └── reproducibility.py # Seed management & hardware/commit auditing
│
├── data/                  # Schema-first ingestion & validation
├── physics/               # Hydrodynamics & engine propulsion models
├── prediction/            # Physics + ML residual & quantile prediction
├── lca/                   # Lifecycle GHG, IMO CII, FuelEU & methane slip
├── optimization/          # Mixed-variable fleet problem, QPSO, NSGA-III, MOEA/D
├── scenarios/             # Weather, carbon price & fuel scenarios
├── benchmark/             # Comparative metrics, Wilcoxon tests, effect sizes
├── experiments/           # Reproducible experiments (EXP01 - EXP06)
├── dashboard/             # Streamlit decision application
├── tests/                 # Automated test suite
└── results/               # Experiment logs, CSVs, JSON summaries & figures
```

---

## 4. Getting Started

### Installation
Ensure Python 3.11+ is installed. Then install dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests
Execute the automated test suite:
```bash
python -m pytest tests -v
```

### Running the Smoke Test
```bash
python -m tests.smoke_test
```

---

## 5. Development Phases

- [x] **Phase 0**: Repository setup, configurations, logging, evidence ledger, and smoke test harness.
- [ ] **Phase 1**: Schema-first data ingestion and validation.
- [ ] **Phase 2**: Hydrodynamic physics engine.
- [ ] **Phase 3**: Physics-guided fuel prediction & quantile uncertainty.
- [ ] **Phase 4**: LCA, methane-slip accounting & regulatory compliance.
- [ ] **Phase 5**: Mixed-variable fleet optimization & CVaR risk.
- [ ] **Phase 6**: Quantum-inspired PSO (QPSO) implementation.
- [ ] **Phase 7**: Classical optimization baselines (NSGA-III, MOEA/D, MILP).
- [ ] **Phase 8**: Fair equal-budget benchmarking & statistical testing.
- [ ] **Phase 9**: Empirical case studies & carbon price sensitivity sweeps.
- [ ] **Phase 10**: Streamlit decision dashboard.
