# Phase 5 Benchmark Protocol & Fairness Specification
## SIH26138 — Egreen Quanta

---

## 1. Experimental Environment & Hardware Specification

- **Host Operating System**: Microsoft Windows 11 Enterprise (64-bit)
- **Python Runtime**: Python 3.14.0 (CPython 64-bit)
- **Scientific Libraries**: NumPy 2.2.0, SciPy 1.14.1, Pandas 2.2.3, Scikit-Learn 1.6.0, PyTest 9.1.1
- **Surrogate Calibration Source**: Real AIS & telemetry FuelCast dataset (25.7 MB Poseidon, 7.5 MB Triton, 10.3 MB Ceto)
- **Git Commit Hash**: `20309b214b9540a7363b7365e442a222cd9c49a1`
- **Execution Mode**: Strictly classical CPU execution. Zero quantum hardware, simulators, or QPUs used.

---

## 2. Seed Partitioning Protocol (§14, §40)

To guarantee scientific validity and eliminate data snooping / tuning bias, seeds were partitioned into three strictly independent sets:

1. **Independent Hyperparameter Tuning Set**:
   - Seeds: `2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010` (10 seeds)
   - Evaluated parameter sensitivity across $\beta \in [0.9, 0.4]$ vs. $[1.0, 0.5]$ and $\Delta\theta_0 \in [0.03\pi, 0.08\pi]$.
2. **Independent Validation Set**:
   - Seeds: `3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010` (10 seeds)
   - Verified that the selected configuration (`Config_LowBeta`: $\beta \in [0.9, 0.4]$, $\Delta\theta = 0.05\pi$) achieved 100.0% feasibility and mean fitness $3.4625$.
3. **Permanent Freezing**:
   - All parameters were permanently locked into `configs/phase5_parameters.json` before initiating the primary benchmark.
4. **Primary Benchmark Set**:
   - Seeds: `1001` through `1030` (30 matched seeds).
   - Zero parameter tuning occurred after inspecting benchmark test seeds.

---

## 3. Evaluation Budget & Strict Accounting (§15, §39)

- **Budget per Run**: Exactly **2,500 calls to `CommonFleetEvaluator.evaluate()`**.
- **Population Size ($M$)**: 50 particles / individuals.
- **Generations / Iterations ($T$)**: 50 iterations ($50 \times 50 = 2,500$ evaluations).
- **Accounting Rule**:
  - Only physical surrogate and constraint evaluations execute inside `CommonFleetEvaluator.evaluate()` and increment the global counter.
  - Internal mathematical operations (vector algebra, sorting, Q-bit rotations, repair logic) do NOT increment the objective counter.
  - No algorithm received hidden restarts, extra evaluations, or asymmetric budgets.

---

## 4. Benchmark Tiers (§20)

- **Tier 1 (Small-Scale Exact)**: 2 vessels, 2 demands, 2 fuels. Exhaustive grid enumeration of 1,296 candidates locates the true mathematical global optimum $J^* = 873.2265$. Optimizers are evaluated on optimality gap.
- **Tier 2 (Deterministic Heterogeneous)**: 3 vessels, 3 demands, calm weather (SCEN-W1). Tests basic combinatorial matching and speed optimization.
- **Tier 3 (Multi-Scenario Weather Uncertainty)**: 4 weather scenarios (SCEN-W1 to SCEN-W4) with probability weights and involuntary speed loss.
- **Tier 4 (Full Primary Benchmark)**: Level 4 Heterogeneous Fleet under CVaR distributionally-robust risk ($\lambda = 0.50$), IMO CII ratings, and FuelEU Maritime carbon intensity constraints.
