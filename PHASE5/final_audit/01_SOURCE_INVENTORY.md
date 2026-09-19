# AUDIT #1: COMPLETE SOURCE INVENTORY & TRACEABILITY LEDGER
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §4 Source Inventory & Traceability  
**Auditor:** Senior Reproducibility Auditor & Scientific Validation Engineer  
**Date:** September 15, 2026  

---

## 1. Environment & Software Metadata

| Parameter | Observed Environment Value | Provenance Check |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Enterprise (Build 26100.3194 / 64-bit) | Verified |
| **CPU Hardware** | Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz (4 physical cores, 8 vCPUs) | Verified |
| **System Memory** | 16.0 GB DDR4 | Verified |
| **Python Runtime** | Python 3.14.0 (CPython 64-bit) | Verified |
| **Virtual Env / Path**| Global user workspace packages (`AppData/Roaming/Python/Python314`) | Verified |
| **Git Commit Reference** | Frozen working tree state at Phase 5 completion | Verified |

### Core Package Dependencies & Versions
- `numpy`: 2.2.3
- `scipy`: 1.15.2
- `pandas`: 2.2.3
- `pyarrow`: 19.0.1
- `matplotlib`: 3.10.1
- `seaborn`: 0.13.2
- `pytest`: 8.3.4
- `pyyaml`: 6.0.2

---

## 2. Telemetry Datasets & Checksum Matrix

| Dataset Artifact | Path | Format | SHA-256 Checksum | Provenance |
| :--- | :--- | :--- | :--- | :--- |
| `CPS_Poseidon.parquet` | `scratch/fuelcast/CPS_Poseidon.parquet` | Apache Parquet | `e2b7e1fa42e185ab9d87baef9271630b701bcbf53fca8552631cf247f111f181` | Real DTU Telemetry |
| `CPS_Triton.parquet` | `scratch/fuelcast/CPS_Triton.parquet` | Apache Parquet | `102fc2d8c366e4a2d8d867c293739775f0a0e5bfa76722d57279bc98ea91e7ee` | Real DTU Telemetry |
| `OSS_Ceto.parquet` | `scratch/fuelcast/OSS_Ceto.parquet` | Apache Parquet | `2495b4105bfa79f61b0fa55b853549fbfe560fa3ce97e3fef570bc6c31826019` | Real DTU Telemetry |
| `phase5_parameters.json`| `configs/phase5_parameters.json` | JSON | `dfa43878ccbf15b94e09f583561a03f44358a9e29a8d9b1c7f53a1a9e9a4f472` | Frozen Tuning Config |

---

## 3. Source Code Inventory

### 3.1 Optimization Algorithms (`src/algorithms/`)
- `base.py`: Base class `BaseFleetOptimizer` and `OptimizationResult` data container.
- `qpso.py`: Canonical continuous QPSO (`PlainQPSOOptimizer`, A0 baseline).
- `qpso_deb.py`: QPSO with Deb's feasibility-first comparison rule (`QPSODebOptimizer`, A1).
- `qpso_decoder.py`: QPSO with deterministic assignment repair (`QPSODecoderOptimizer`, A2).
- `discrete_qpso.py`: Discrete-operator QPSO using CPMPSO probability transitions (`DiscreteQPSOOptimizer`, A3).
- `hybrid_qi.py`: `A4HeterogeneousQIOptimizer` (Q-bit + QPSO penalty-only) and `A5CompleteHybridQIOptimizer` (Complete Hybrid QI-HFO).
- `de.py`: Classical Differential Evolution baseline (`DEOptimizer`, DE/rand/1/bin).
- `pso.py`: Classical continuous Particle Swarm Optimization (`PSOOptimizer`).
- `ga.py`: Canonical Genetic Algorithm (`GAOptimizer`).
- `random_search.py`: Uniform stochastic sampling baseline (`RandomSearchOptimizer`).
- `nsga3.py`: Reference Multi-Objective Evolutionary Algorithm (`NSGA3Optimizer`).

### 3.2 Representation & Domain Decoders (`src/representation/`)
- `variable_types.py`: Decision variable partitions (Discrete, Integer, Binary, Continuous).
- `qbit_representation.py`: `QBit` quantum probability state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, rotation gate $R(\Delta\theta)$, and `DirichletQVector`.
- `repair.py`: `FleetSolutionRepairer` domain decoder enforcing bijective demand allocation and engine-fuel compatibility.

### 3.3 Evaluation Engine (`src/evaluator/`)
- `common_evaluator.py`: `CommonFleetEvaluator` wrapping `Phase4FleetEvaluator`. Strictly increments evaluation counter and implements `deb_prefers()` comparator.
- `optimization/fleet_evaluator_phase4.py`: High-fidelity multi-scenario surrogate evaluator incorporating weather uncertainty, IMO CII ratings, and FuelEU compliance.

### 3.4 Benchmarking, Statistics & Validation
- `src/benchmark/runner.py`: Benchmark harness orchestrating 30 matched seeds across all optimizers.
- `src/benchmark/statistics.py`: Statistical computation module (Wilcoxon, Holm, Permutation, Hodges-Lehmann, Bootstrap).
- `src/benchmark/metrics.py`: Pareto non-dominated sorting and Hypervolume calculation.
- `src/validation/small_exact.py`: Level 1 small-scale exhaustive grid enumeration engine.
- `src/validation/failure_analysis.py`: 10-class failure taxonomy analyzer.
- `src/validation/scalability.py`: Fleet dimension scalability benchmark ($D=30$ to $D=600$).
- `src/visualization/plots.py`: Publication visualization rendering engine (Figures 01–18).

---

## 4. End-to-End Traceability Chains

| Key Reported Result | Source Code Origin | Experiment Script | Raw CSV Source | Statistical Processing | Reported In | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A0 Feasibility = 80.0%** | `src/algorithms/qpso.py` | `scripts/run_phase5_master.py` | `PHASE5/results/A0.csv` | Mean of `is_feasible` | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **A1 Feasibility = 100.0%** | `src/algorithms/qpso_deb.py` | `scripts/run_phase5_master.py` | `PHASE5/results/A1.csv` | Mean of `is_feasible` | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **A2 Diversity = 5.75** | `src/algorithms/qpso_decoder.py` | `scripts/run_phase5_master.py` | `PHASE5/results/A2.csv` | Mean of `population_diversity` | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **A4 Diversity = 189.54** | `src/algorithms/hybrid_qi.py` | `scripts/run_phase5_master.py` | `PHASE5/results/A4.csv` | Mean of `population_diversity` | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **A5 Hypervolume = 247.11M** | `src/algorithms/hybrid_qi.py` | `scripts/run_phase5_master.py` | `PHASE5/results/A5.csv` | 2D exact hypervolume | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **NSGA-III HV = 150.67M** | `src/algorithms/nsga3.py` | `scripts/run_phase5_master.py` | `PHASE5/results/NSGA3.csv` | 2D exact hypervolume | `A5_ABLATION_TABLE.csv` | **VERIFIED** |
| **A5 vs. DE Wilcoxon p < 1e-5** | `src/benchmark/statistics.py` | `scripts/run_phase5_master.py` | `A5.csv` & `DE.csv` | Wilcoxon signed-rank | `statistics.csv` | **VERIFIED** |
| **D=600 A5 Speedup = 2.67x** | `src/validation/scalability.py` | `scripts/run_phase5_master.py` | `scalability.csv` | Ratio of mean runtimes | `scalability.csv` | **VERIFIED** |
| **Small-Scale J* = 873.23** | `src/validation/small_exact.py` | `scripts/run_phase5_master.py` | `small_exact.csv` | Exhaustive grid search | `small_exact.csv` | **AUDIT FLAGGED (Scale Mismatch)** |

---

## 5. Traceability Conclusion
All reported benchmark metrics, feasibility counts, runtime measurements, and statistical tests have 100% traceable origins from source code through raw seed CSVs. A single critical anomaly was flagged for deeper forensic auditing in Audit #3: the formulation scale mismatch in `small_exact.py`.
