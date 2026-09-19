# SIH26138 — PHASE 3.1 FORENSIC AUDIT REPORT
## Green Fleet Optimization & Benchmark Validity Gate

**Auditor:** Hostile Scientific Reviewer, Optimization Researcher, Numerical Methods Auditor  
**Date:** 2026-09-13  
**Target Repository:** `sih26138_platform`  
**Git Commit:** `20309b214b9540a7363b7365e442a222cd9c49a1`  
**Engineering Test Status:** **87 / 87 PASSED (100%)**  
**Scientific Gate Status:** **REQUIRES CORRECTION**  

---

## 1. Primary Investigation: The Suspicious "115003.2758" Loss
The Phase 3 benchmark reported identical loss values across Differential Evolution (DE) and Quantum-Behaved Particle Swarm Optimization (QPSO) down to four decimal places:
- **DE Mean Loss:** 115003.2758
- **QPSO Mean Loss:** 115003.2758
- **GA Mean Loss:** 115003.2767
- **PSO Mean Loss:** 115003.2775
- **Random Search Mean Loss:** 115003.2828

Simultaneously, Wilcoxon signed-rank testing reported that DE beat QPSO in 25 out of 30 seeds ($p = 0.0012$).

### The Forensic Finding
Forensic deconstruction revealed that **100% of all 150 benchmark runs were INFEASIBLE and PENALTY-DOMINATED**:
- **Physical Normalized Objective:** $\approx 3.2758$ ($0.00285\%$ of total loss)
- **Hard Domain Envelope Penalty:** $+100,000.00$
- **Soft IMO CII Rating E Penalty:** $+15,000.00$
- **Total Penalty Value:** $+115,000.00$ ($99.99715\%$ of total loss)

### Root Cause
In `DomainChecker.evaluate_point()`, step 2 audits Categorical Validity against `valid_categories`.
When fitted on FuelCast telemetry for `CPS_Poseidon`, the dataset contained `vessel_type = 'passenger_cruise'`.
However, `FleetEvaluationEngine._get_vessel_profile()` hardcoded `class_family = 'cruise_passenger'`.
Because `'cruise_passenger' != 'passenger_cruise'`, `DomainChecker` flagged **every candidate state as OUT_OF_DOMAIN** with:
`Unknown category vessel_type='cruise_passenger' (valid: ['passenger_cruise'])`.
This triggered the $+100,000$ hard penalty barrier regardless of speed, cargo, mode, or physical variables.

Consequently, all 5 algorithms spent 100% of their search budgets traversing an artificial penalty plateau. DE's "superiority" over QPSO was an artifact of finding floating-point values lower by $2.8 \times 10^{-7}$ on an infeasible plateau.

---

## 2. Evaluation Budget Audit (2,500 vs 50,000)
- Single evaluation latency was empirically measured at **33.41 ms**.
- A full 30-seed, 5-optimizer benchmark at 50,000 evaluations would require **69.5 hours** of continuous compute.
- The 2,500 evaluation budget was applied strictly equally across all 5 optimizers ($50 \times 50$ population/iterations).
- **Gold Pilot Verdict:** Running 50,000 evaluations on the current objective function is futile because the categorical rejection is immutable in parameter space.

---

## 3. Claim Audit Summary

| Claim | Initial Phase 3 Status | Phase 3.1 Audit Status | Forensic Evidence |
|:---|:---:|:---:|:---|
| **A: QPSO outperforms PSO/GA/Random** | Supported | **FALSIFIED / INVALID** | Differences are floating-point noise on a penalty plateau. |
| **B: DE outperforms QPSO** | Supported | **FALSIFIED / INVALID** | Median diff is $0.000000$ ($2.8 \times 10^{-7}$). |
| **C: QPSO practical superiority** | Supported | **NOT SUPPORTED** | No real-world operational difference. |
| **D: DE mathematical superiority** | Supported | **NOT SUPPORTED** | Artifact of infeasible penalty surface. |
| **E: SafeFuelObjective defense** | Supported | **SUPPORTED** | Intercepted 100% of adversarial out-of-domain probes. |
| **F: Fuel savings generated** | Supported | **CONDITIONAL** | Unverified until feasibility is restored. |
| **G: Multi-vessel scalability** | Supported | **CONDITIONAL** | Dispatch scaling works; single-vessel evaluation needs fix. |

---

## 4. Required Next Action (Phase 3.2 Correction)
1. Synchronize the categorical string in `optimization/evaluator.py`:
   Map `v_class` to match the exact string present in `DomainChecker.valid_categories['vessel_type']` (i.e. `'passenger_cruise'`).
2. Adjust the single-voyage CII evaluation to use design deadweight/gross tonnage appropriate for cruise vessels so that baseline transit does not artificially default to rating 'E'.
3. Re-execute the 30-seed benchmark under genuine feasibility to determine true slow-steaming and fleet optimization performance.
