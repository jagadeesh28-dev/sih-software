# Phase 3.1 — Penalty Dominance Forensic Report

## Executive Summary
Across all 150 benchmark runs (5 optimizers x 30 seeds), **100% of candidate solutions are PENALTY_DOMINATED**.

- **Mean Total Objective:** 115,003.2758
- **Total Penalty Value:** 115,000.0000
- **Penalty Fraction:** **99.99715%**
- **Physical Fraction:** **0.00285%**
- **Feasibility Rate:** **0.00%** (0 out of 150 runs feasible)

## Root-Cause Forensic Discovery
The dominance of penalties was caused by a categorical feature string mismatch between the fleet configuration and the domain checker training data:
- `DomainChecker` fitted on FuelCast telemetry with `vessel_type = 'passenger_cruise'`.
- `FleetEvaluationEngine._get_vessel_profile()` provided `class_family = 'cruise_passenger'`.
- Candidate evaluation in `safe_objective.py` submitted `'cruise_passenger'`, which `DomainChecker.evaluate_point()` rejected with:
  `Unknown category vessel_type='cruise_passenger' (valid: ['passenger_cruise'])`.
- This assigned `domain_status = 'OUT_OF_DOMAIN'` despite an envelope Euclidean distance of `0.00`.
- In `FleetConstraintManager`, an out-of-domain status incurred a hard penalty:
  `P_domain = 1e5 * (1.0 + envelope_distance) = 100,000.0`.
- Additionally, single-voyage passenger transit without cargo capacity defaulted IMO CII rating to `'E'`, incurring a soft penalty of `15,000.0`.
- Total Penalty = `100,000 + 15,000 = 115,000.0`.

## Tabular Summary by Optimizer

| Optimizer | Mean Penalty Fraction | Mean Physical Fraction | Penalty Dominated Pct | Feasibility Pct |
|:---|:---:|:---:|:---:|:---:|
| DE | 99.99715% | 0.00285% | 100.0% | 0.0% |
| QPSO | 99.99715% | 0.00285% | 100.0% | 0.0% |
| GA | 99.99715% | 0.00285% | 100.0% | 0.0% |
| PSO | 99.99715% | 0.00285% | 100.0% | 0.0% |
| Random_Search | 99.99715% | 0.00285% | 100.0% | 0.0% |

## Audit Conclusion
The benchmark did NOT measure maritime optimization performance (fuel, emissions, slow steaming).
Instead, all algorithms operated on an infeasible penalty plateau, differentiating only on floating-point noise of the physical objective component ($3.275826$ vs $3.275827$).
