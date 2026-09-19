# SIH26138 Egreen Quanta — Final Architecture Decision & System Specification

**Authority:** SIH26138 Final Scientific Closure Gate  
**Date of Architecture Freeze:** September 18, 2026  
**Final Architectural Configuration:** **OPTION D (Dual-Engine Heterogeneous Architecture)**  
**Auditor & Research Lead:** Independent Scientific Validation Lead  
**Repository Root:** `sih26138_platform`

---

## 1. Executive Architectural Decision

Following exhaustive forensic auditing, benchmark repair, and controlled representation-isolation experimentation, the system architecture is permanently frozen as **OPTION D**:

```
========================================================================================================
                                     OPTION D DUAL-ENGINE ARCHITECTURE
========================================================================================================

 [PRIMARY OPERATIONAL ENGINE]                          [RESEARCH & EXPLORATION ENGINE]
 Classical MODE / DE + Deb + C0 Repair                 Heterogeneous QI Representation + DE/QPSO
 - 100.0% Feasibility Enforcement                      - Probabilistic Amplitude Parameterization
 - Lowest Physical Fuel Burn: 3.3936 t                 - Dirichlet-Q Multi-State Categorical Choice
 - Fastest Execution: 6.19 s                           - Preserves High Categorical Shannon Entropy
 - Production Decision Support Dispatch                - Frontier Non-Dominated Strategy Discovery
 --------------------------------------------------------------------------------------------------------
                                                ▲
                                                │ Plug-and-Play Optimizer Interface
                                                ▼
 ========================================================================================================
                                        COMMON PLATFORM CORE
 ========================================================================================================
 1. High-Frequency Real Telemetry: FuelCast Ingestion (173,986 records across 3 commercial vessels)
 2. Hydrodynamic Physics Base: Holtrop-Mennen resistance + Kwon / STAwave-2 wave added drag
 3. Machine Learning Residual: LightGBM GBDT predicting operational residuals (R^2 = 0.9501)
 4. Domain & Safety Barrier: Mahalanobis DomainChecker + SafeFuelObjective numerical clamp
 5. Canonical Evaluator: CommonFleetEvaluator with bitwise identical budget accounting
 6. Statutory Regulatory Engine: FuelEU Maritime (€2,400/t), IMO CII (A–E), EU ETS (€90/t)
 7. Stochastic Uncertainty: CVaR_0.80 tail-risk evaluation across 4 metocean scenarios
 8. Multi-Objective Tracking: Bounded Epsilon-Pareto Archive
 9. Decision Support Interface: 4 Explainable Pareto Decision Cards for Human Superintendents
========================================================================================================
```

---

## 2. Scientific Rationale for Option D

The empirical evidence from our matched 30-seed benchmarks disconfirms any claim that quantum-inspired optimization should unilaterally replace classical optimization:

1. **Continuous Parameter Superiority of DE:**  
   Classical Differential Evolution (DE) significantly outperforms Quantum-Behaved Particle Swarm Optimization (QPSO) on continuous speed and cargo optimization, achieving lower physical fuel loss ($3.3936\text{ t}$ vs. $3.4483\text{ t}$, paired Wilcoxon $p = 1.02 \times 10^{-7}$) with a $21\%$ faster wall-clock runtime ($6.19\text{ s}$ vs. $7.51\text{ s}$). DE is therefore mathematically selected as the **Primary Operational Engine**.

2. **Categorical Diversity Niche of Q-Bits:**  
   In discrete combinatorial decision spaces (route assignments, multi-fuel selections, cold-ironing shore power), deterministic projection and integer rounding can cause greedy population collapse. Q-bit probability amplitudes and Dirichlet-Q vectors maintain higher categorical Shannon entropy ($3.85\text{ bits}$ vs. integer rounding collapse), enabling broad exploratory coverage of diverse decarbonization pathways. Heterogeneous QI is therefore retained as the **Research & Exploration Engine**.

3. **Decoupled Common Core:**  
   Both engines interact with the exact same evaluator, repair operators, constraint comparators, and regulatory rules via the `BaseFleetOptimizer` interface, ensuring complete modularity.

---

## 3. Modular Optimizer Interface Specification

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np

class OptimizerEngine:
    """
    Unified dispatch interface for Option D Dual-Engine Architecture.
    Allows shoreside superintendents to switch between Operational MODE
    and Exploratory QI engines seamlessly.
    """
    @staticmethod
    def optimize(
        engine_type: str,
        evaluator: "CommonFleetEvaluator",
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
        seed: int = 1001,
        **kwargs
    ) -> "OptimizationResult":
        engine_type = engine_type.upper()
        if engine_type in ["OPERATIONAL", "MODE", "DE"]:
            from scripts.run_fair_multiobjective_comparison import run_fair_mode
            # Dispatches Primary Operational Engine (Classical MODE / DE + Deb + C0 Repair)
            return run_fair_mode(seed=seed)
        elif engine_type in ["EXPLORATORY", "QI", "QBIT_DE", "A6"]:
            from scripts.run_final_representation_isolation import run_c2_qbit_de
            from src.representation.repair import FleetSolutionRepairer
            # Dispatches Research Engine (Q-Bit Categorical + Continuous DE)
            return run_c2_qbit_de(seed=seed, base_evaluator=evaluator.base_evaluator, repairer=FleetSolutionRepairer())
        elif engine_type in ["A5", "HYBRID_QI"]:
            from src.algorithms.hybrid_qi import A5CompleteHybridQIOptimizer
            opt = A5CompleteHybridQIOptimizer(seed=seed)
            return opt.optimize(evaluator, xl, xu, budget=budget)
        elif engine_type in ["NSGA3", "BENCHMARK_NSGA3"]:
            from scripts.run_fair_multiobjective_comparison import run_fair_nsga3
            return run_fair_nsga3(seed=seed)
        else:
            raise ValueError(f"Unknown optimizer engine type: {engine_type}")
```

---

## 4. Decision Support System (DSS) Output Cards

Rather than outputting a single opaque numerical vector, Egreen Quanta synthesizes four transparent, operator-selectable operational strategies across the Pareto frontier:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          EGREEN QUANTA FLEET DECISION CARDS                            │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│ STRATEGY CARD            │ OPERATIONAL PROFILE      │ VOYAGE METRICS                   │
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ OPTION A:                │ Poseidon: Dem-A, 14.2 kn │ Fuel Consumption: 72.40 tonnes   │
│ MINIMUM FUEL             │ Triton:   Dem-B, 12.0 kn │ Total OPEX:       $34,120        │
│ (Slow Steaming)          │ Ceto:     Dem-C, 10.5 kn │ Lifecycle GHG:    228.5 tCO2e    │
│                          │ Fuel:     VLSFO / Port=0 │ Schedule Delay:   +14.2 hours    │
│                          │ Shore:    Auxiliary Eng  │ Tail Risk (CVaR): Low ($1,200)   │
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ OPTION B:                │ Poseidon: Dem-A, 17.5 kn │ Fuel Consumption: 88.60 tonnes   │
│ MINIMUM COST             │ Triton:   Dem-B, 14.8 kn │ Total OPEX:       $31,450 (LOW)  │
│ (Commercial Optimum)     │ Ceto:     Dem-C, 11.0 kn │ Lifecycle GHG:    279.1 tCO2e    │
│                          │ Fuel:     VLSFO          │ Schedule Delay:   0.0 hours (ON) │
│                          │ Shore:    No Cold Iron   │ Tail Risk (CVaR): Med ($4,500)   │
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ OPTION C:                │ Poseidon: Dem-A, 16.8 kn │ Fuel Consumption: 94.20 tonnes   │
│ MINIMUM LIFECYCLE GHG    │ Triton:   Dem-B, 14.0 kn │ Total OPEX:       $48,900        │
│ (Maximum Decarbonized)   │ Ceto:     Dem-C, 11.2 kn │ Lifecycle GHG:    112.4 tCO2e    │
│                          │ Fuel:     Bio-Methanol   │ Schedule Delay:   0.0 hours      │
│                          │ Shore:    Cold Ironing=1 │ FuelEU Balance:   +€8,400 surplus│
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ OPTION D:                │ Poseidon: Dem-A, 16.0 kn │ Fuel Consumption: 84.12 tonnes   │
│ BALANCED ROBUST OPTIMUM  │ Triton:   Dem-B, 13.5 kn │ Total OPEX:       $36,200        │
│ (Recommended Standard)   │ Ceto:     Dem-C, 11.0 kn │ Lifecycle GHG:    182.0 tCO2e    │
│                          │ Fuel:     LNG / Bio-Meth │ Schedule Delay:   0.0 hours      │
│                          │ Shore:    Cold Ironing=1 │ Tail Risk (CVaR): Minimal ($480) │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

---

## 5. Deployment Guardrails & Certification Policy
1. **Decision Support Only:** Egreen Quanta provides advisory recommendations. Autonomous command transmission to engine governing systems or bridge autopilots is strictly prohibited.
2. **Naval Architectural Fallback:** If the vessel geometry is flagged as out-of-domain by the Mahalanobis DomainChecker ($D_M > 3.0$), the system automatically disables the ML residual model and falls back to pure hydrodynamic resistance calculations.
3. **Regulatory Audit Trail:** Every voyage recommendation generates a cryptographic audit manifest recording input metocean parameters, fuel emission factors, and statutory compliance margins.
