# PHASE 3 SYSTEM ARCHITECTURE
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Phase 3 Architecture & Interface Design  
**Date:** 2026-09-12  
**Status:** ARCHITECTURE DESIGN LOCKED  

---

## 1. End-to-End System Pipeline

The Phase 3 platform implements an unbroken, defensive chain from verified real telemetry to Pareto decision support:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           1. REAL TELEMETRY INGESTION                            │
│  FuelCast (173,974 records across CPS_Poseidon, CPS_Triton, OSS_Ceto)             │
│  Direct Coriolis mass flow (kg/s -> kg/h), Acoustic Doppler STW, GPS SOG, Metocean│
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                 2. VESSEL-CLASS CALIBRATED SURROGATE LAYER                        │
│  - MODEL-REAL-04: Hybrid Physics (Holtrop-Mennen) + ML Residual (alpha=1.0)       │
│  - Quantile Predictor: Pinball loss uncertainty [q05, q50, q95]                   │
│  - Vessel Class Isolation: Cruise Family vs. Offshore DP vs. Cargo Feeder         │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    3. SAFEFUELOBJECTIVE DEFENSIVE INTERFACE                       │
│  - DomainChecker: Statistical P01-P99 empirical bounding envelope                │
│  - Physical Sanity Auditor: Mode-aware speed/power/draft checks                  │
│  - Distance Proportional Penalty: Smooth quadratic repulsion outside envelope     │
│  - Disagreement Classifier: Flags physics-ML divergence                           │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                4. EMISSION, COST & REGULATORY COMPLIANCE ENGINES                  │
│  - IMO MEPC.391(81) Well-to-Wake LCA: WtT + TtW + Methane Slip                   │
│  - IMO CII Module: Attained vs. Required CII, Operational Ratings A-E             │
│  - FuelEU Maritime: GHG Intensity Balance (89.34 g/MJ target), Statutory Penalties│
│  - OPEX Cost Model: Fuel + EU ETS Carbon Tax ($90/t) + Cold Ironing + Demurrage   │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     5. CONSTRAINED OPTIMIZATION SUITE                             │
│  - Quantum-Behaved PSO (QPSO): Classical delta-well contraction-expansion         │
│  - Benchmark Baselines: Canonical PSO, Genetic Algorithm, Differential Evolution  │
│  - Control Baseline: Uniform Random Search                                        │
│  - Multi-Objective Engines: Weighted-Sum, Epsilon-Constraint, Q-MOEA/D, NSGA-III   │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                 6. PARETO DECISION SUPPORT & EXPLAINABILITY                       │
│  - Multi-Objective Non-Dominated Sorting & Front Generation                       │
│  - Operational Compromise Presets: Fuel Priority, Cost Priority, Green, Balanced  │
│  - SIH Interactive Trade-Off Visualizer & Natural-Language Explainability         │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                   7. SCIENTIFIC BENCHMARKING & AUDITING                           │
│  - Equal Evaluation Budgets (N_eval = 50,000 across 30 matched seeds)             │
│  - Paired Wilcoxon Signed-Rank Testing & Effect Size Calculations                 │
│  - Hypervolume, Generational Distance, Inverted Generational Distance, Spacing    │
│  - Adversarial Stress Suite & Safety Ablation Analysis                            │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Repository Modular Organization

Phase 3 introduces clean modular separation within `sih26138_platform/` without disturbing frozen Phase 2/2.3 modules:

```
sih26138_platform/
├── configs/
│   ├── fuels.yaml                     # IMO MEPC.391(81) certified fuel pathways
│   ├── regulations.yaml               # FuelEU, IMO CII, and EU ETS statutory parameters
│   └── fleet_profiles.yaml            # Vessel class hydrostatic and operational envelopes
│
├── optimization/
│   ├── __init__.py                    # Public API exports
│   ├── variables.py                   # Chromosome representation & decision vectors
│   ├── evaluator.py                   # FleetEvaluationEngine wrapping SafeFuelObjective
│   ├── constraints.py                 # Hard & soft constraint validation system
│   ├── qpso.py                        # Quantum-Behaved PSO implementation
│   ├── pso.py                         # Canonical Particle Swarm Optimization
│   ├── genetic_algorithm.py           # Real-coded Genetic Algorithm (SBX / poly mutation)
│   ├── differential_evolution.py      # Differential Evolution (DE/rand/1/bin)
│   ├── random_search.py               # Random Search baseline
│   ├── pareto.py                      # Non-dominated sorting, HV, GD, IGD metrics
│   ├── voyage_model.py                # Voyage leg transit time and weather speed loss
│   ├── cost_model.py                  # Transparent OPEX accounting (Fuel, ETS, Shore)
│   ├── emissions_model.py             # WtW GHG and verified methane slip accounting
│   ├── regulatory.py                  # FuelEU and IMO CII compliance interfaces
│   └── scenarios.py                   # Standard benchmark and SIH demonstration scenarios
│
├── experiments/
│   ├── exp_opt_01_single_fuel.py      # EXP-OPT-01: Single-objective fuel minimization
│   ├── exp_opt_02_fuel_cost.py        # EXP-OPT-02: Fuel + Cost bi-objective optimization
│   ├── exp_opt_03_fuel_ghg.py         # EXP-OPT-03: Fuel + GHG bi-objective optimization
│   ├── exp_opt_04_pareto_fleet.py     # EXP-OPT-04: Full multi-objective Pareto front
│   ├── exp_opt_05_qpso_vs_pso.py      # EXP-OPT-05: 30-seed QPSO vs PSO benchmark
│   ├── exp_opt_06_qpso_vs_ga.py       # EXP-OPT-06: 30-seed QPSO vs GA benchmark
│   ├── exp_opt_07_qpso_vs_de.py       # EXP-OPT-07: 30-seed QPSO vs DE benchmark
│   ├── exp_opt_08_qpso_vs_random.py   # EXP-OPT-08: 30-seed QPSO vs Random Search
│   ├── exp_opt_09_uncertainty.py      # EXP-OPT-09: Risk sensitivity (lambda in {0..2})
│   ├── exp_opt_10_fuel_price_sens.py  # EXP-OPT-10: Fuel price sensitivity
│   ├── exp_opt_11_carbon_price_sens.py# EXP-OPT-11: EU ETS carbon price sensitivity
│   ├── exp_opt_12_weather_sens.py     # EXP-OPT-12: Metocean wave/wind sensitivity
│   ├── exp_opt_13_schedule_sens.py    # EXP-OPT-13: Deadline tight vs relaxed sensitivity
│   ├── exp_opt_14_vessel_class.py     # EXP-OPT-14: Vessel-class isolated optimization
│   ├── exp_opt_15_adversarial.py      # EXP-OPT-15: Adversarial SafeFuelObjective audit
│   ├── exp_opt_16_scalability.py      # EXP-OPT-16: Computational scaling (5 to 100 ships)
│   └── exp_phase3_master_runner.py    # Master runner executing all experiments
│
├── results/
│   ├── experiments/optimization/      # CSV tabular results for all 16 experiments
│   └── figures/optimization/          # High-resolution publication & demo plots
│
└── tests/
    ├── test_optimization.py           # Core evaluator & algorithm test
    ├── test_constraints.py            # Hard/soft constraint validation tests
    ├── test_emissions.py              # WtW LCA & methane slip equation verification
    ├── test_regulatory.py             # FuelEU & CII compliance calculation tests
    ├── test_qpso.py                   # QPSO quantum dynamics & determinism tests
    ├── test_benchmark_fairness.py     # Equal evaluation budget & seed pairing tests
    └── test_adversarial_optimization.py# Optimization safety barrier tests
```

---

## 3. Detailed Component Interfaces & Data Flow

### 3.1 Evaluator Interface (`FleetEvaluationEngine`)
The core bridge connecting optimizers to the predictive physics and regulatory layers:

```python
class FleetEvaluationEngine:
    def __init__(
        self,
        safe_objective: SafeFuelObjective,
        fuel_registry: FuelPathwayRegistry,
        regulatory_config: Dict[str, Any],
        vessel_class: str = "cruise",
        lambda_robust: float = 0.5,
        carbon_price_usd_tonne: float = 90.0,
    ): ...

    def evaluate_chromosome(
        self,
        chromosome: SolutionChromosome,
        scenario: VoyageScenario,
    ) -> EvaluationResult:
        """
        1. Decode chromosome decisions.
        2. Compute involuntary weather speed loss and transit duration.
        3. Form operational state query for SafeFuelObjective.
        4. Receive fuel flow (median, q05, q95), domain status, penalty.
        5. Compute WtW emissions, methane slip, and auxiliary power.
        6. Compute operational costs (Fuel, Carbon, Shore, Demurrage).
        7. Evaluate FuelEU and IMO CII compliance status.
        8. Check all hard and soft constraints.
        9. Return structured EvaluationResult with objective vector and diagnostics.
        """
```

### 3.2 Chromosome Data Structure (`SolutionChromosome`)
```python
@dataclass
class LegDecision:
    leg_id: str
    vessel_id: str
    commanded_speed_kn: float
    fuel_type: str
    cargo_teu: float
    operating_mode: str
    use_shore_power: bool

@dataclass
class SolutionChromosome:
    decisions: List[LegDecision]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 3.3 Evaluation Result Contract (`EvaluationResult`)
Every function evaluation produces a fully transparent record:
```python
@dataclass
class EvaluationResult:
    # Scalarized and vector objectives
    fitness: float
    objective_vector: np.ndarray  # [Fuel, Cost, GHG, Delay, Risk]
    
    # Physical and operational metrics
    total_fuel_tonnes: float
    total_opex_usd: float
    total_wtw_ghg_tonnes_co2e: float
    voyage_duration_hours: float
    schedule_delay_hours: float
    uncertainty_dispersion_tonnes: float
    
    # Regulatory statuses
    cii_rating: str               # 'A', 'B', 'C', 'D', 'E'
    cii_margin_pct: float
    fueleu_compliant: bool
    fueleu_penalty_usd: float
    
    # Defensive auditing
    domain_status: str            # 'VALID', 'NEAR_BOUNDARY', 'OUT_OF_DOMAIN', 'PHYSICALLY_INVALID'
    is_feasible: bool
    constraint_violations: List[str]
    penalty_value: float
    explanation: str
```

---

## 4. Defensive Boundaries & Anti-Exploitation Mechanics

To guarantee that metaheuristics do not find ungrounded local minima:
1. **Double Barrier Defense**:
   - `DomainChecker`: Bounding envelope check (P01–P99) + mode-aware physical sanity checks.
   - `SafeFuelObjective`: If domain status is `OUT_OF_DOMAIN` or `PHYSICALLY_INVALID`, the fuel rate is overridden with a massive penalty ($10,000\text{ kg/h} \times (1 + d_{\text{env}})$ or $100,000\text{ kg/h}$).
2. **Smooth Quadratic Exterior Penalties**:
   - For soft constraint violations (schedule delay, boundary proximity), smooth quadratic penalties provide gradient signals that guide swarm particles back toward feasible space.
3. **Hard Rejection in Pareto Archives**:
   - Non-dominated sorting archives immediately discard any candidate with `is_feasible == False`, guaranteeing that Pareto fronts contain only valid, certified solutions.
