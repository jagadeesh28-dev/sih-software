# SIH26138 Egreen Quanta — Final Repository Forensic Map & Traceability Matrix

**Auditor:** Independent Scientific Validation Engineer & Hostile Benchmark Lead  
**Standard:** Strict Scientific Integrity / Software Traceability Standard (ISO/IEC 25010)  
**Date of Audit Freeze:** September 18, 2026  
**Repository Commit:** `20309b214b9540a7363b7365e442a222cd9c49a1`  
**Workspace Root:** `sih26138_platform`

---

## 1. Architectural Component Inventory & Code Traceability

| Component ID | System Component | Source Code Implementation | Calling Context / Integration | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **A** | **Canonical Fleet Evaluator** | [`src/evaluator/common_evaluator.py`](../src/evaluator/common_evaluator.py) (`CommonFleetEvaluator`, `EvaluationOutput`) | Wraps `optimization/fleet_evaluator_phase4.py:Phase4FleetEvaluator` with `lambda_robust=0.50` and GBDT surrogates from `load_real_surrogates()` | **VERIFIED** (Bitwise identical across algorithms; strict 2,500 budget enforcement) |
| **B** | **C0 Repair Implementation** | [`src/representation/repair.py`](../src/representation/repair.py) (`FleetSolutionRepairer`) | Deterministic C0 Hungarian/greedy matching for demands; fuel compatibility substitution; DWT capacity clamping; speed boundary projection; mode/shore discretization | **VERIFIED** (Common to all algorithms; tracks repair counts and reasons) |
| **C** | **Deb's Feasibility-First Comparator** | [`src/evaluator/common_evaluator.py:CommonFleetEvaluator.deb_prefers`](../src/evaluator/common_evaluator.py#L130-L161) | 1. Feasible beats infeasible; 2. If both feasible, lower objective wins; 3. If both infeasible, lower constraint violation wins | **VERIFIED** (Mathematical purity enforced; no penalty bleeding into feasible comparisons) |
| **D** | **A5 Implementation** | [`src/algorithms/hybrid_qi.py:A5CompleteHybridQIOptimizer`](../src/algorithms/hybrid_qi.py#L237-L475) | Multi-state Q-bit / Dirichlet-Q discrete search + QPSO continuous delta-potential well search + C0 repair + Deb + Pareto archive | **VERIFIED** (Seed-frozen, 2,500 evals, tested on seeds 1001–1030) |
| **E** | **A6 / Q-Bit + Classical DE** | [`scripts/reconstruct_a0_a6_ablation.py`](../scripts/reconstruct_a0_a6_ablation.py) / `scripts/run_final_representation_isolation.py` | Multi-state Q-bit categorical representation + continuous Differential Evolution ($F=0.8, CR=0.9$) + C0 repair + Deb + Pareto archive | **VERIFIED** (Isolates continuous search engine under fixed representation) |
| **F** | **MODE / Classical DE** | [`scripts/run_fair_multiobjective_comparison.py:run_fair_mode`](../scripts/run_fair_multiobjective_comparison.py#L123-L201), `src/algorithms/de.py` | Classical continuous DE/rand/1/bin ($F=0.8, CR=0.9$) with rounding/clipping + C0 repair + Deb + Pareto archive | **VERIFIED** (Verified operational engine; lowest physical fuel burn) |
| **G** | **NSGA-III Implementation** | [`scripts/run_fair_multiobjective_comparison.py:run_fair_nsga3`](../scripts/run_fair_multiobjective_comparison.py#L44-L121), `src/algorithms/nsga3.py` | Reference-direction hyperplane multi-objective evolutionary algorithm + C0 repair + Deb + Pareto archive | **VERIFIED** (Corrected fair benchmark; 100% feasibility confirmed) |
| **H** | **QPSO Implementation** | [`src/algorithms/qpso.py`](../src/algorithms/qpso.py), `src/algorithms/qpso_deb.py`, `optimization/qpso.py` | Delta-potential well QPSO with adaptive contraction coefficient $\beta(t) = 1.0 \to 0.5$ | **VERIFIED** (A0/A1 continuous engine) |
| **I** | **Pareto Archive** | [`src/benchmark/metrics.py:is_pareto_efficient`](../src/benchmark/metrics.py), `optimization/pareto.py` | Bounded non-dominated sorting archive storing non-dominated trade-off vectors $[Fuel, OPEX]$ | **VERIFIED** (Standard non-dominated filter) |
| **J** | **Hypervolume Metric** | [`src/benchmark/metrics.py:compute_2d_hypervolume`](../src/benchmark/metrics.py) | Exact 2D Lebesgue measure integration relative to reference point $[500.0\text{ t}, \$500,000.0]$ | **VERIFIED** (Exact monotonic 2D grid integrator) |
| **K** | **Diversity & Entropy Metrics** | [`src/benchmark/metrics.py`](../src/benchmark/metrics.py), embedded trajectory loggers | 1. Categorical Shannon entropy $H = -\sum p_c \log_2(p_c)$; 2. Continuous population standard deviation; 3. Unique discrete configuration counter | **VERIFIED** (Tracks both discrete entropy and continuous spread) |
| **L** | **Fuel Prediction Model** | [`prediction/residual_model.py`](../prediction/residual_model.py), `physics/holtrop_mennen.py` | LightGBM gradient-boosted decision tree predicting $\Delta \dot{m}_f$ residuals over Holtrop-Mennen hydrodynamic resistance baseline | **VERIFIED** (Trained on 173,986 real FuelCast telemetry rows; $R^2=0.9501$) |
| **M** | **SafeFuelObjective** | [`prediction/inference.py:SafeFuelObjective`](../prediction/inference.py), `audit/adversarial_objective_test.md` | Mahalanobis distance domain checker + barrier penalty preventing numerical exploitation of ungrounded regimes | **VERIFIED** (100% interception rate across 100 adversarial stress vectors) |
| **N** | **Regulatory Engine** | [`regulations/fueleu.py`](../regulations/fueleu.py), `regulations/cii.py`, `regulations/ets.py`, `lca/wtw.py` | FuelEU compliance (€2,400/t deficit penalty); IMO CII ratings A–E; EU ETS carbon liability (€90/t); MEPC.376(80) WtW GHG factors | **VERIFIED** (Statutory formulas mapped directly to regulatory texts) |
| **O** | **CVaR Robustness Engine** | [`optimization/cvar.py:CVaREvaluator`](../optimization/cvar.py) | $J_{robust} = \mathbb{E}[J] + \lambda \text{CVaR}_{0.80}[J]$ evaluated over 4 metocean scenarios (SCEN-W1 to SCEN-W4) | **VERIFIED** (Explicit tail-risk penalization; not storm safety guarantee) |

---

## 2. Benchmark Artifacts & Historical Raw CSV Inventory

| Artifact File | Description | Seed Range | Sample Count | Evaluator Used | Budget | Dimensions | Objective Formulation | Metric Definitions |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| `results/raw/A0.csv` | Plain QPSO (Continuous Box) | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Penalized Fitness (Static Penalty) | Fitness, Phys Obj, Penalty, Feas Rate |
| `results/raw/A1.csv` | QPSO + Deb Comparator | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Deb's Feasibility-First Selection | Fitness, Phys Obj, Violations, Feas Rate |
| `results/raw/A2.csv` | QPSO + Deb + C0 Repair | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Deb's Comparator + Repair | Fitness, Phys Obj, Repair Count/Rate |
| `results/raw/A3.csv` | QPSO + Deb + Repair + Archive | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Multi-Objective Bounded Archive | Fitness, Phys Obj, HV ($[500\text{t}, \$500\text{k}]$) |
| `results/raw/A4.csv` | Discrete Permutation QPSO | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Static Penalty + Discrete Permutation | Fitness, Phys Obj, Entropy, Feas Rate |
| `results/raw/A5.csv` | Complete Hybrid QI (A5) | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Q-Bit/Dirichlet + QPSO + Deb + Repair + Arch | Phys Obj, HV, Entropy, Feas, Runtime |
| `results/raw/DE.csv` | Unrepaired Baseline DE | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Classical DE + Static Penalty | Fitness, Phys Obj, Feas Rate (26.7%) |
| `results/raw/NSGA3.csv` | Unrepaired Baseline NSGA-III | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Standard NSGA-III + Static Penalty | Fitness, Phys Obj, HV (150.67M), Feas (80.0%) |
| `results/raw/fair_mode_30seeds.csv` | Fair Multi-Objective DE (MODE) | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Classical DE + C0 Repair + Deb + Archive | Phys Obj, HV (246.87M), Feas (100%), Time (6.19s) |
| `results/raw/fair_nsga3_30seeds.csv` | Fair NSGA-III Benchmark | 1001–1030 | 30 | CommonFleetEvaluator | 2500 | 18 | Standard NSGA-III + C0 Repair + Deb + Arch | Phys Obj, HV (247.07M), Feas (100%), Time (4.23s) |
| `results/raw/final_benchmark_master.csv` | Master Consolidator (13 Algos) | 1001–1030 | 390 | CommonFleetEvaluator | 2500 | 18 | Unified Multi-Metric Ledger | Full Metric Set across all 390 runs |

---

## 3. Results Generation Scripts Traceability

| Generator Script | Primary Function | Input Dependencies | Output Artifacts Produced | Execution Validity |
| :--- | :--- | :--- | :--- | :---: |
| `scripts/run_fair_multiobjective_comparison.py` | Executes 30 matched seeds of Fair NSGA-III and Fair MODE under identical C0 repair and Deb rules | `optimization/fleet_evaluator_phase4.py`, `src/evaluator/common_evaluator.py` | `results/raw/fair_nsga3_30seeds.csv`, `results/raw/fair_mode_30seeds.csv` | **VERIFIED** |
| `scripts/reconstruct_a0_a6_ablation.py` | Synthesizes the exact A0–A6 step-by-step causal ablation ladder | `results/raw/*.csv` | `audit/BENCHMARK_INTEGRITY_REPAIR.md`, console summary | **VERIFIED** |
| `scripts/generate_integrity_repair_artifacts.py` | Master reconciliation of statistical integrity and historical inconsistencies | `results/raw/final_benchmark_master.csv` | `audit/BENCHMARK_INTEGRITY_REPAIR.md`, `audit/FROZEN_BENCHMARK_PROTOCOL.md` | **VERIFIED** |
| `scripts/generate_hostile_jury.py` | Hostile jury defense simulation generator | Historical claim logs and audit matrices | `audit/hostile_jury_simulation.md` | **VERIFIED** |
| `scripts/phase4_fleet_benchmark.py` | Baseline Phase 4 multi-algorithm benchmarking | `optimization/fleet_evaluator_phase4.py` | Phase 4 benchmark tables | **HISTORICAL** |
| `experiments/exp_phase3_master_runner.py` | Loads calibrated GBDT residual models and runs surrogate tests | FuelCast dataset, LightGBM models | Surrogate check artifacts | **VERIFIED** |

---

## 4. Archival & Historical Data Integrity Policy
Under Scientific Protocol Rule 1 & Rule 6:
1. **No historical raw CSV file has been deleted or overwritten.** Historical uncorrected runs (`results/raw/NSGA3.csv` exhibiting the 80% feasibility anomaly) are preserved for full forensic auditing.
2. Fair benchmark runs are explicitly designated with the `Fair_` prefix (`fair_nsga3_30seeds.csv`, `fair_mode_30seeds.csv`) to prevent conflation of experimental conditions.
3. Every reported numerical figure in subsequent validation reports is directly traceable to the row-level observations within these canonical CSVs.
