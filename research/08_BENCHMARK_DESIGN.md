# 08 — BENCHMARK DESIGN: SCIENTIFIC VALIDITY
## RQ10: How Should the Benchmark Be Designed for Defensible Comparison?

---

## 1. Benchmark Design Principles

A scientifically defensible algorithm comparison requires:

1. **Equal computational budget** — same number of fitness evaluations across all algorithms
2. **Multiple independent seeds** — minimum 30 per algorithm (our Phase 4: exactly 30, satisfactory)
3. **Consistent problem instances** — same seeds generate same random problem instances
4. **Unambiguous metrics** — primary and secondary metrics clearly defined before experiments
5. **Appropriate statistical tests** — non-parametric for non-normal distributions; FWER correction for multiple comparisons
6. **Honest negative reporting** — if algorithm A loses to B, report it as such

---

## 2. Current Benchmark Assessment (Phase 4)

### 2.1 What Phase 4 Did Correctly

| Criterion | Phase 4 Status | Evidence |
|:---|:---:|:---|
| Equal evaluation budget | ✅ | Both algorithms: 50 particles × 200 iterations = 10,000 evaluations |
| Seed count ≥ 30 | ✅ | 30 seeds per algorithm |
| Consistent seeding | ✅ | `np.random.seed(seed)` at start of each run |
| Non-parametric statistics | ✅ | Wilcoxon rank-sum for primary comparison |
| FWER correction | ✅ | Holm-Bonferroni applied across all claims |
| Effect size | ✅ | Hodges-Lehmann estimator reported |
| Bootstrap CI | ✅ | 95% BCa bootstrap confidence intervals |
| Negative results preserved | ✅ | QPSO infeasibility rate reported honestly |

### 2.2 What Phase 4 Did Imperfectly

| Criterion | Phase 4 Status | Improvement for Phase 5 |
|:---|:---:|:---|
| Multiple problem instances | ⚠️ Single benchmark | Add 3–5 problem instances of varying scale |
| Heterogeneous fleet scaling | ⚠️ Fixed 6-vessel fleet | Test with 4, 6, 8, 12 vessels |
| Weather scenario sampling | ⚠️ Fixed 4 scenarios | Monte Carlo over 50+ weather scenarios |
| Algorithm parameter sensitivity | ⚠️ Default parameters | Sensitivity analysis ($\pm 20$% parameter perturbation) |
| Alternative fuel scenarios | ⚠️ Fixed fuel costs | Uncertainty analysis over fuel price ranges |

---

## 3. Scientifically Defensible Claims From Phase 4

Based on Phase 4 data and statistical tests:

### Claim 1 (CONFIRMED, Evidence Class A):
> "Under a 10,000-evaluation budget on the SIH26138 6-vessel heterogeneous fleet benchmark, DE achieves 100% feasibility while QPSO achieves 86.7% feasibility (95% CI: [70.3%, 96.7%])."

**Supported by:** Binomial exact test on feasibility rates; no FWER issue (single claim).

### Claim 2 (CONFIRMED with caveats, Evidence Class A):
> "QPSO and DE are statistically comparable in objective value quality among feasible solutions (Wilcoxon p = 0.23 after Holm-Bonferroni, Hodges-Lehmann: $\Delta = -\$241$ [95% BCa CI: $-\$1{,}847$, $+\$1{,}124$])."

**Caveats:**
- QPSO objective quality is only measured over 26/30 feasible runs
- If infeasible runs were included with full penalty, QPSO's mean objective would be substantially worse
- The comparison is conditional on feasibility

### Claim 3 (CONFIRMED, Evidence Class A):
> "The primary cause of QPSO infeasibility is Penalty Inversion: the hard penalty ($50k) is dominated by soft delay penalties (~$109k) in the infeasible region, making infeasible configurations falsely attractive to the swarm attractor."

**Supported by:** Phase 4.1 forensic audit; Claim Ledger entries B, C, D.

---

## 4. Benchmark Metadata Standards

For reproducibility, every benchmark run must record:

```yaml
benchmark_metadata:
  version: "SIH26138-Phase4-v1.0"
  timestamp: "ISO 8601"
  git_commit: "full SHA"
  python_version: "3.11.x"
  numpy_version: "1.26.x"
  scipy_version: "1.11.x"
  algorithm: "QPSO | DE | QIEA | Hybrid"
  seed: integer
  n_particles: integer
  n_iterations: integer
  n_evaluations: integer  # particles × iterations
  n_vessels: 6
  n_demand_units: 8
  n_fuel_modes: 4
  weather_scenarios: 4
  result_objective: float  # USD
  result_feasible: boolean
  result_feasibility_rate: float  # over n_seeds
  cii_compliance: boolean
  fueleu_compliance: boolean
  runtime_seconds: float
```

---

## 5. Benchmark Difficulty Calibration

The SIH26138 problem qualifies as "Level 4" heterogeneous fleet benchmark based on:

| Difficulty Dimension | Score (1–5) | Justification |
|:---|:---:|:---|
| Variable type heterogeneity | 5 | Binary + categorical + continuous in single formulation |
| Constraint complexity | 4 | Assignment + capacity + regulatory + port-fuel |
| Objective complexity | 4 | Multi-objective: cost + GHG + CII + CVaR |
| Problem scale | 3 | 6 vessels, moderate; could scale to 12 |
| Data quality | 4 | Real telemetry-calibrated surrogates |
| Regulatory realism | 5 | IMO CII + FuelEU Maritime 2025 |

**Overall: Hard research benchmark, not a toy problem.** Suitable for SIH 2026 and publishable as a benchmark paper.

---

## 6. Benchmark Extension for Phase 5 (Future Work)

When Phase 5 begins, the benchmark should be extended to include:

1. **Scaling study:** 4, 6, 8, 12, 20 vessels; report how feasibility rate and objective quality scale
2. **Alternative fuel scenarios:** High/medium/low methanol supply; measure impact on algorithm-specific feasibility
3. **Weather uncertainty sweep:** Monte Carlo over 50 ECMWF weather scenarios; report CVaR convergence
4. **Pareto analysis:** Multi-objective formulation (cost vs. GHG); report hypervolume indicator
5. **Algorithm parameter sensitivity:** $\pm 20$% perturbation in QPSO $\beta$, QIEA rotation rate, DE F/CR; report robustness

This extension maintains scientific rigor while demonstrating breadth of the platform.
