# PHASE 4 FAILURE MODES & ADVERSARIAL SAFEGUARDS
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Heterogeneous Fleet Optimization Failure Modes, Risk Mitigation & Adversarial Safeguards  
**Date:** 2026-09-14  
**Status:** COMPLETE & AUDITED  

---

## 1. Introduction & Taxonomy of Failure Modes

In Phase 4, the optimization complexity is elevated from single-vessel continuous routing to a **heterogeneous, multi-vessel, mixed-integer combinatorial, uncertainty-aware fleet allocation problem**.

This structural elevation introduces combinatorial, operational, and physical failure modes that do not exist in single-vessel settings. This document systematically specifies these failure modes, their detection mechanisms, and the mathematical barriers implemented to prevent optimizer exploitation.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 4 FAILURE MODES TAXONOMY                                │
├──────────────────────────┬───────────────────────────┬─────────────────────────────────┤
│     FAILURE DOMAIN       │      SPECIFIC HAZARD      │       MITIGATION BARRIER        │
├──────────────────────────┼───────────────────────────┼─────────────────────────────────┤
│ 1. Combinatorial         │ Demand Collision / Split  │ Exact Unique Matching Filter    │
│ 2. Vessel Capability     │ Deadweight Overload       │ $m_{\text{cargo}} \le \text{DWT}│
│ 3. Fuel Safety           │ Toxic Fuel on Passenger   │ Incompatibility Matrix Barrier  │
│ 4. Hydrodynamic Domain   │ Out-of-Envelope Speed     │ DomainChecker + Hard Barrier    │
│ 5. Environmental Domain  │ Severe Weather Extrapol.  │ Wave Height Cap ($H_s \le 3.5$) │
│ 6. Schedule Feasibility  │ Involuntary Speed Loss    │ Weather Margin + Late Demurrage │
│ 7. Statistical Fallacy   │ Zero-Diff Pseudo-p-values │ $10^{-5}$ Absolute Threshold    │
│ 8. High-D Scalability    │ Penalty Dominance         │ Decomposed Objective Reporting  │
│ 9. Risk Modeling         │ Risk Metric Pathologies   │ Distributionally Robust CVaR    │
│ 10. Multi-Objective      │ Infeasible Pareto Points  │ Feasible-Only Non-Dominated Sort│
└──────────────────────────┴───────────────────────────┴─────────────────────────────────┘
```

---

## 2. Detailed Failure Modes & Adversarial Defenses

### FM-01: Combinatorial Demand Collisions
- **Hazard**: The optimizer assigns multiple vessels to the same cargo demand ($u_{i, k} = 1$ and $u_{j, k} = 1$ for $i \ne j$), double-counting cargo delivery and under-allocating operational transport work.
- **Root Cause**: Independent continuous decision variables rounded to discrete demand indices without mutual exclusion constraints.
- **Safeguard**: Decoded assignments are passed through a unique demand validator. Any collision triggers an immediate hard penalty ($P_{\text{comb}} = 50,000 \times N_{\text{collisions}}$) before surrogate invocation.

### FM-02: Structural Deadweight & Capacity Violations
- **Hazard**: A vessel is assigned a cargo demand exceeding its maximum structural deadweight ($m_{\text{cargo}} > \text{DWT}_{\max}$) or passenger passenger capacity.
- **Root Cause**: Bounded continuous search space where upper cargo bound exceeds specific vessel limits.
- **Safeguard**: Explicit capacity checks ($m_{\text{cargo}, v} \le \text{DWT}_{\text{allowable}, v}$). Violations incur a quadratic deadweight penalty:
  $$P_{\text{DWT}} = 10,000 \times \left( \frac{m_{\text{cargo}} - \text{DWT}_{\max}}{\text{DWT}_{\max}} \right)^2$$

### FM-03: Toxic / Incompatible Alternative Fuel Selection
- **Hazard**: Ammonia ($\text{NH}_3$) assigned to cruise passenger vessels (`CPS_Poseidon` or `CPS_Triton`) where international safety regulations (IGF Code / SOLAS) strictly prohibit toxic cryogenic fuels in passenger spaces.
- **Root Cause**: Discrete fuel selection variable unconstrained across vessel classes.
- **Safeguard**: Hard-coded compatibility lookup table `COMPATIBILITY_MATRIX[vessel][fuel]`. Incompatible combinations return immediate rejection ($P \ge 50,000$) without invoking physics or surrogate models.

### FM-04: Hydrodynamic Domain Extrapolation
- **Hazard**: Optimizer requests speeds below maneuvering speed ($V < 8\text{ kn}$) or above physical maximum ($V > 24\text{ kn}$), causing ML residual models to output nonsensical fuel predictions or negative consumption.
- **Root Cause**: Unconstrained optimizer exploration vectors during initial population phases.
- **Safeguard**: Dual barrier:
  1. Mathematical clipping and bounded box projection.
  2. Multi-dimensional convex hull domain checker (`DomainChecker.is_in_domain()`). If out-of-domain, physical surrogate evaluation is blocked and a penalty is returned.

### FM-05: Involuntary Speed Loss Under Adverse Weather
- **Hazard**: Under severe sea states (SCEN-W4: $H_s = 3.5\text{ m}$), added resistance decreases achievable speed through the water for a given engine MCR, causing severe schedule delays. If ignored, the optimizer plans unrealistic calm-water speeds.
- **Root Cause**: Assuming calm-water speed equals effective speed over ground in heavy seas.
- **Safeguard**: Explicit Kwon (2008) added wave resistance and involuntary speed loss modeling:
  $$V_{\text{actual}} = V_{\text{ordered}} - \Delta V_{\text{weather}}(H_s, \theta_{\text{wave}}, C_B, \nabla)$$
  Arrival time is calculated strictly using $V_{\text{actual}}$, propagating delays directly into schedule demurrage penalties.

### FM-06: Floating-Point Noise Treated as Statistical Superiority
- **Hazard**: In near-saturated landscapes, two optimizers produce objective values differing by $10^{-8}$ (pure floating-point rounding). Reporting Wilcoxon signed-rank tests on these differences manufactures false statistical significance ($p < 0.05$).
- **Root Cause**: Standard statistical libraries (e.g. `scipy.stats.wilcoxon`) executing rank-sum calculations on numerical jitter when true differences are zero.
- **Safeguard**: Absolute engineering threshold $\epsilon = 10^{-5}$ USD. If $|J_A - J_B| \le \epsilon$, the pair is classified as a strict tie. If all pairs are ties ($n_{\text{nonzero}} = 0$), Wilcoxon is reported as `NOT_APPLICABLE_ALL_TIES` with $p = 1.0$ and stat = NaN.

### FM-07: Penalty Dominance in High-Dimensional Benchmarks
- **Hazard**: In high dimensions ($D \ge 300$, 50–100 vessels), random initialization places all particles in infeasible regions. Optimizers appear to make rapid progress, but are merely minimizing arbitrary penalty functions rather than physical fuel consumption.
- **Root Cause**: Conflating penalized objective $J_{\text{penalized}}$ with physical objective $J_{\text{phys}}$.
- **Safeguard**: Mandatory decomposed objective reporting. Every run exports separate columns for `physical_fitness`, `penalty_value`, and `is_feasible`. Benchmarks are audited to ensure feasibility is achieved before concluding convergence.

### FM-08: Risk Tail Truncation in CVaR Calculation
- **Hazard**: Conditional Value at Risk (CVaR) calculated on too few scenario samples or with improper quantile thresholds leads to unstable gradient estimates or negative risk contributions.
- **Root Cause**: Under-sampling weather uncertainty space.
- **Safeguard**: Distributionally robust CVaR over calibrated discrete weather distribution ($\alpha = 0.80$):
  $$\text{CVaR}_\alpha(J) = \text{VaR}_\alpha(J) + \frac{1}{1 - \alpha} \sum_{s: J_s > \text{VaR}_\alpha} p_s (J_s - \text{VaR}_\alpha)$$
  Strict non-negativity enforced.

---

## 3. Adversarial Test Suite Verification

The adversarial robustness of the Phase 4 engine is verified against 15 deliberate attack vectors in `tests/test_phase4_fleet_optimization.py`:

| Test ID | Adversarial Attack Vector | Injected Value | Expected Engine Behavior | Test Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADV-01** | Negative Speed | $V = -5.0\text{ kn}$ | Rejection / Bound Clip | **PASS** |
| **ADV-02** | Hyper-speed | $V = 55.0\text{ kn}$ | Hard Domain Penalty | **PASS** |
| **ADV-03** | Extreme Draft | $T = 25.0\text{ m}$ | Out-of-Domain Barrier | **PASS** |
| **ADV-04** | Negative Draft | $T = -2.0\text{ m}$ | Hard Domain Barrier | **PASS** |
| **ADV-05** | Extreme Displacement | $\nabla = 250,000\text{ t}$ | Hydrodynamic Rejection | **PASS** |
| **ADV-06** | Severe Sea State | $H_s = 12.0\text{ m}$ | Environmental Out-of-Domain | **PASS** |
| **ADV-07** | Extreme Gale Wind | $V_{\text{wind}} = 45.0\text{ m/s}$ | Domain Checker Rejection | **PASS** |
| **ADV-08** | Incompatible Fuel (Ammonia) | Ammonia on `CPS_Poseidon` | Fuel Compatibility Penalty | **PASS** |
| **ADV-09** | Unknown Fuel Identifier | Fuel Index = 99 | Discrete Boundary Error Catch | **PASS** |
| **ADV-10** | Cargo > Vessel DWT | $25,000\text{ t}$ on 8,500 DWT | Deadweight Penalty | **PASS** |
| **ADV-11** | Negative Cargo Demand | $m_{\text{cargo}} = -500\text{ t}$ | Physical Non-negativity Catch | **PASS** |
| **ADV-12** | Demand Collision | Vessel 1 & 2 $\to$ Demand A | Combinatorial Hard Penalty | **PASS** |
| **ADV-13** | NaN Injected in Vector | Vector with `np.nan` | Sanity Check Rejection | **PASS** |
| **ADV-14** | Inf Injected in Vector | Vector with `np.inf` | Sanity Check Rejection | **PASS** |
| **ADV-15** | Zero Speed with Cargo | $V = 0.0, m > 0$ | Immobile Transport Violation | **PASS** |

All 15 adversarial tests execute without software crashes, surrogate NaN propagation, or unhandled exceptions, confirming that the Phase 4 optimization engine is safe against adversarial exploitation.
