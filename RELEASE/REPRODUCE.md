# Reproducibility Instructions
### SIH26138 — Egreen Quanta (v1.0.0)

This guide provides instructions for replicating all experimental benchmarks, regression tests, and verification gates.

---

## 1. Single-Command Minimum Verification

To verify that the complete platform is operational and passes all 9 release gates:
```bash
python reproduce_release.py
```
This script executes:
1. Telemetry integrity check and SHA-256 validation.
2. Booster model loading and health check.
3. Baseline `MODEL-REAL-04` accuracy verification.
4. Primary `QI-C1` accuracy verification.
5. Conformal predictive uncertainty coverage test ($94.1\% \ge 90\%$).
6. Domain guard and severe OOD rejection test.
7. Optimizer `SafeFuelObjective` constraint test.
8. End-to-end full scenario execution trace.
9. Claim ledger compliance audit.

---

## 2. Running the Complete Verification & Stress Suite

To run all 1,000 automated prediction stress tests, 40-trial runtime benchmarks, failure injections (F1–F10), and end-to-end tracing:
```bash
python scripts/validate_phase7_hardening.py
```
Outputs generated in `PHASE7/results/`:
- `ood_guard_validation.csv`
- `prediction_stress_tests.csv`
- `failure_injection.csv`
- `runtime_benchmark.csv`
- `regression_results.csv`
- `end_to_end_trace.json`

---

## 3. Running the Phase 5 Optimization Tests

To execute the complete suite of 14 multi-objective fleet optimization tests:
```bash
pytest tests/test_phase5_verification.py -v
```

---

## 4. Re-training Models from Scratch

To re-fit and export the booster models and calibration quantiles from the raw parquet telemetry:
```bash
python scripts/build_production_models.py
```
Takes ~15 seconds on a multi-core machine.
