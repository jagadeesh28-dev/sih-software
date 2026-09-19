# SIH26138 Egreen Quanta — Final Frozen Benchmark Protocol

**Freeze Date:** September 18, 2026  
**Auditor:** Independent Scientific Validation & Benchmarking Lead  
**Authority:** SIH26138 Scientific Validation Gate  
**Repository Root:** `sih26138_platform`  
**Git Commit Hash:** `20309b214b9540a7363b7365e442a222cd9c49a1`

---

## 1. Frozen Benchmark Configuration

| Parameter | Frozen Specification | Rationale & Strict Constraints |
| :--- | :--- | :--- |
| **Random Seeds** | `1001, 1002, ..., 1030` (30 matched seeds) | Paired statistical design; identical seed sequences across all competing algorithms |
| **Evaluation Budget** | Exactly 2,500 objective evaluations | Strictly enforced via `CommonFleetEvaluator`; counts calls to `evaluate(x)` |
| **Population Size ($N$)** | 50 candidate vectors | Fixed across all evolutionary and swarm algorithms |
| **Generations / Iterations ($T$)**| 50 iterations | $N \times T = 50 \times 50 = 2,500$ evaluations total (including initialization) |
| **Canonical Evaluator** | `CommonFleetEvaluator` | Wraps `Phase4FleetEvaluator` with `lambda_robust=0.50` and real GBDT surrogates |
| **Canonical Fleet Problem** | SIH26138 Heterogeneous Fleet | 3 real-calibrated commercial vessels (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`) |
| **Problem Dimension ($D$)** | $D = 18$ variables ($3\text{ vessels} \times 6\text{ variables}$) | Assignment, cargo, speed, fuel, operating mode, shore power |
| **Constraint Comparator** | Deb's Feasibility-First Tournament Rule | Feasible strictly dominates infeasible; ties broken by constraint violation magnitude |
| **Repair Operator** | C0 Hungarian / Greedy Repair Heuristic | Deterministic repair of assignment, fuel compatibility, DWT, and speed boundaries |
| **Hypervolume Reference Point** | $[500.0\text{ tonnes}, \$500,000.0]$ | Fixed reference point in unnormalized $[Fuel, OPEX]$ objective space |
| **Pareto Archive** | Bounded Non-Dominated Archive | Stores all feasible, non-dominated trade-off vectors discovered throughout the run |

---

## 2. Decision Space & Variable Encodings

For each vessel $v \in \{0, 1, 2\}$:
1. **$x_{6v+0}$ — Route / Demand Assignment**: Discrete categorical $\{0, 1, 2, 3\}$ (0: Unassigned, 1: Demand-A, 2: Demand-B, 3: Demand-C). Bound: $[0.0, 3.0]$.
2. **$x_{6v+1}$ — Cargo Quantity**: Continuous $[0.0, \text{DWT}_v]$ in metric tonnes. Bounds: Poseidon: $[0, 5000\text{t}]$; Triton: $[0, 2500\text{t}]$; Ceto: $[0, 3500\text{t}]$.
3. **$x_{6v+2}$ — Sailing Speed**: Continuous $[v_{\min}, v_{\max}]$ in knots. Bounds: Poseidon: $[12.0, 22.0\text{ kn}]$; Triton: $[10.0, 18.0\text{ kn}]$; Ceto: $[10.0, 16.0\text{ kn}]$.
4. **$x_{6v+3}$ — Fuel Choice**: Discrete categorical $\{0, 1, 2, 3, 4\}$ (0: VLSFO, 1: MGO, 2: LNG, 3: Methanol, 4: Biofuel). Bound: $[0.0, 4.0]$.
5. **$x_{6v+4}$ — Operating Mode**: Discrete categorical $\{0, 1, 2, 3\}$ (0: Eco, 1: Standard, 2: Fast, 3: Port Maneuvering). Bound: $[0.0, 3.0]$.
6. **$x_{6v+5}$ — Shore Power Status**: Binary $\{0, 1\}$ (0: Auxiliary diesel in port, 1: Cold ironing OPS). Bound: $[0.0, 1.0]$.

---

## 3. Objective Formulations & Hierarchy

1. **Objective 1 — Fuel Consumption ($f_1$)**: Total voyage fuel burn across all fleet vessels in metric tonnes ($t$).
2. **Objective 2 — Operational Expenditure ($f_2$)**: Total voyage OPEX in USD ($) including fuel costs, carbon taxes (EU ETS at €90/t), FuelEU Maritime penalties (€2,400/t deficit), shore electricity tariffs, and port demurrage.
3. **Objective 3 — Lifecycle Well-to-Wake GHG ($f_3$)**: Total cradle-to-wake greenhouse gas emissions in $\text{tCO}_2\text{e}$ evaluated under IMO MEPC.376(80) LCA guidelines.
4. **Objective 4 — Schedule Reliability / Delay ($f_4$)**: Total cumulative schedule delay across fleet arrivals in hours ($h$).
5. **Objective 5 — Uncertainty & Weather Risk ($f_5$)**: Conditional Value-at-Risk ($\text{CVaR}_{0.80}$) of voyage fuel/cost evaluated over 4 metocean scenarios (SCEN-W1 to SCEN-W4).

Scalar Single-Objective Evaluation Formulation:
$$J_{\text{scalar}} = \mathbb{E}[f_2] + \lambda_{\text{robust}} \text{CVaR}_{0.80}[f_2] + \sum_{j} \text{Penalty}_j$$
where $\lambda_{\text{robust}} = 0.50$. In Deb-enabled comparisons, penalties are treated strictly as constraint violation magnitude $V(x)$, not added into feasible physical objectives.

---

## 4. Execution Sequence Rules

1. **Candidate Vector Generation**: The algorithm produces candidate $x \in \mathbb{R}^{18}$.
2. **Repair Sequence**:
   - Step A: Discrete rounding / decoding of assignment, fuel, mode, and shore power.
   - Step B: Combinatorial bipartite matching to guarantee every mandatory demand is covered by a compatible vessel without collision.
   - Step C: Verification of engine-fuel technical compatibility (fallback to default compatible baseline).
   - Step D: Clamping of cargo to demand requirement and vessel DWT.
   - Step E: Speed boundary clipping to $[v_{\min}, v_{\max}]$.
3. **Evaluator Invocation**: Repaired $x$ is passed to `CommonFleetEvaluator.evaluate(x)`. Budget counter increments by 1.
4. **Deb's Selection**: Feasibility and constraint violation magnitude are processed via `CommonFleetEvaluator.deb_prefers(out_trial, out_parent)`.
5. **Archive Ingestion**: If $x$ is feasible, non-dominated criteria are evaluated, and $x$ is ingested into the Pareto archive.

---

## 5. Computing Environment & Reproducibility Metadata

| Item | Frozen Value |
| :--- | :--- |
| **Operating System** | Windows-11-10.0.26200-SP0 |
| **Processor Architecture** | Intel64 Family 6 Model 183 Stepping 1, GenuineIntel (x86_64) |
| **Execution Threading** | Single CPU thread per run (serial deterministic execution) |
| **Python Version** | Python 3.14.0 (tags/v3.14.0:ebf955d, Oct 7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)] |
| **NumPy Version** | 2.2.6 |
| **SciPy Version** | 1.17.0 |
| **LightGBM Version** | 4.7.0 |
| **Scikit-Learn Version**| 1.8.0 |
| **Pandas Version** | 2.2.3 |
| **Git Commit Hash** | `20309b214b9540a7363b7365e442a222cd9c49a1` |
| **Random Number Gen** | `numpy.random.default_rng(seed)` |
