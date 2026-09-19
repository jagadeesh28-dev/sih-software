# Project Changelog: SIH26138 — Egreen Quanta
### Evolution from Phase 1 (Data Ingestion) to Phase 7 (Production Release)

All major engineering and scientific milestones are recorded below in accordance with SIH engineering protocols.

---

## [v1.0.0] — 2026-09-19 (Phase 7: Production Release Freeze)
### Added
- Created `src/qi_prediction/serving.py` exposing unified `predict_fuel()` and `predict_fuel_with_uncertainty()` interfaces.
- Implemented 3-tier safe model routing (`QI-C1` $\to$ `MODEL-REAL-04` $\to$ `PhysicsFuelPredictor` $\to$ `REJECT`).
- Implemented immutable feature contract `PHASE7/config/feature_contract.yaml` enforcing physical bounds and types.
- Implemented single-command reproduction runner `reproduce_release.py` verifying all 9 core release gates.
- Built 1,000-sample automated prediction stress test suite with 100% safe rejection rate.
- Added fault injection suite (F1–F10) validating graceful recovery.
- Generated comprehensive release package in `RELEASE/`.

### Verified
- Resolved historical record count discrepancy: 173,986 raw records vs 173,974 validated operational records (12 trailing null padding rows dropped).
- Re-confirmed statistical parity of QI-C1 vs Classical GA ($p = 0.684$) and +44.7% higher exploratory search diversity.
- Conformal uncertainty validated with 94.13% empirical coverage for nominal 90% confidence bounds.
- All six release gates passed; system certified as **PRODUCTION READY**.

---

## [Phase 6] — 2026-09-19 (Quantum-Inspired Fuel Prediction Research)
### Added
- Developed Level 1 Quantum-Inspired Evolutionary Algorithm (`qiea.py`) with Han & Kim rotation gates.
- Developed Delta-potential Quantum Particle Swarm Optimization (`qpso.py`) for hyperparameter tuning.
- Formulated and audited continuous Matrix Product State tensor network (`mps_predictor.py`).
- Executed 30-seed matched master benchmark across P0 to P7.
- Established conformal predictive uncertainty bounds (80%, 90%, 95%).
- Formulated Leave-One-Vessel-Out (LOVO) cross-validation and discovered zero-shot transfer barrier.
- Documented audited negative research result for continuous MPS tensor trains.

---

## [Phase 5] — 2026-09-15 (Fleet Optimization Final Audit)
### Added
- Audited heterogeneous fleet optimization algorithms (QIEA, QPSO, NSGA-III, DE, Hybrid A5).
- Diagnosed continuous QPSO penalty-inversion failure and restored feasibility from 80% to 100% via Deb's feasibility-first constraint handling.
- Implemented Hungarian bipartite matching repair to eliminate duplicate demand assignments.
- Demonstrated +64.0% higher Hypervolume over standard NSGA-III.

---

## [Phase 4] — 2026-09-14 (Heterogeneous Fleet Model)
- Integrated weather scenarios, involuntary speed loss, and CVaR distributionally-robust risk.
- Coupled IMO CII rating trajectories and FuelEU Maritime penalties into objective space.

---

## [Phase 3] — 2026-09-13 (Optimization Framework)
- Formulated mathematical fleet routing and speed scheduling decision variables.
- Standardized canonical vocabulary for vessel categories and fuel types.

---

## [Phase 2] — 2026-09-12 (Real Telemetry Ingestion & Physics Baseline)
- Downloaded and processed DTU FuelCast telemetry (173,986 raw records across 3 vessels).
- Implemented Holtrop-Mennen, STAwave-2, and Blendermann hydrodynamic resistance physics.
- Trained frozen baseline `MODEL-REAL-04` ($R^2 = 0.9501$, $\text{MAE} = 246.97\text{ kg/h}$).

---

## [Phase 1] — 2026-09-12 (Problem Formulation & Setup)
- Established project repository and scientific auditing protocol.
