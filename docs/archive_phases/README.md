# Archive of Developmental Phases, Audits & Historical Artifacts

This directory contains the complete chronological developmental history, forensic data audits, mathematical models, and exploratory research ledgers for **EGREEN QUANTA (SIH26138)**.

All files here are **fully retained under version control** to ensure seamless continuation of ongoing research, engineering traceability, and auditability. The active production codebase, serving predictors, optimization engines, bridge HMI, and verified test suites are consolidated in the top-level repository modules (`physics/`, `prediction/`, `optimization/`, `src/`, `api/`, `web/`, and `tests/`).

---

## Catalog Index by Phase

### 1. Phase 1 & Forensic Data Audits (`docs/archive_phases/phase1_and_data_audits/`)
Forensic ingestion, provenance validation, schema mapping, and data quality reports for the DTU FuelCast commercial sensor dataset (173,986 records across 3 physical hulls):
- `01_REAL_DATA_RAW_AUDIT.md` & `REAL_DATA_RAW_AUDIT.csv`: Raw sensor ingestion reconciliation and row count verification.
- `02_REAL_TARGET_PROVENANCE.md`: Mass flow vs. volumetric flow sensor provenance.
- `03_REAL_STW_AUDIT.md` & `REAL_STW_AUDIT.csv`: Speed-Through-Water sensor audit, Doppler log reconciliation, and current correction.
- `04_CANONICAL_SCHEMA_MAPPING_REAL.csv` & `CANONICAL_SCHEMA_MAPPING.csv`: Schema harmonization between FuelCast, VISIR, and physical models.
- `05_REAL_DATA_QUALITY_REPORT.md`: Missingness, physical clipping, stuck-sensor, and outlier analysis.
- `06_REAL_OPERATING_REGIMES.csv`: Clustering and identification of operating regimes (berth, maneuvering, transit, storm).
- `07_REAL_SPLIT_MANIFEST.json`: Strict forward temporal splitting protocol preventing future lookahead leakage.
- `08_REAL_MODEL_RESULTS.csv` to `15_REAL_STATISTICAL_COMPARISON.csv`: Real telemetry ablation benchmarks, physics residual decomposition, and uncertainty calibrations.
- `16_PHASE2_3_SCIENTIFIC_GATE_REPORT.md` & `17_PHASE2_3_CLAIM_LEDGER.yaml`: Milestone gate sign-offs and claim status tracking.
- `DATASET_CONFLICT_RESOLUTION.md`, `DATASET_DOWNLOAD_MANIFEST.md`, `DATASET_LICENSE_AUDIT.md`, `DATASET_TARGET_PROVENANCE.md`: Licensing and dataset provenance.
- `PHASE1_COMPLETION_REPORT.md`: Comprehensive Phase 1 retrospective.
- `REAL_DATASET_FORENSIC_VERIFICATION.md`, `REAL_DATA_VALIDATION_PLAN.md`, `REAL_DATA_VALIDATION_RECOMMENDATION.md`, `VERIFIED_DATASET_MATRIX.csv`: Validation protocols.

### 2. Phase 2: Hybrid Prediction & Hardening (`docs/archive_phases/phase2_prediction/`)
Hydrodynamic physics baseline integration (Holtrop-Mennen resistance) with residual LightGBM predictors and inductive conformal prediction:
- `PHASE2_COMPLETION_REPORT.md`: Retrospective on feature selection, residual learning, and model architecture.
- `PHASE2_2_OPTIMIZATION_READINESS_REPORT.md`: Mathematical handoff between surrogate model serving and multi-objective optimizers.

### 3. Phase 3: Single-Vessel Quantum-Inspired Optimization (`docs/archive_phases/phase3_optimization/`)
Formulation, ablation, and benchmarking of Quantum-Inspired Evolutionary Algorithms (QIEA) and Quantum-Behaved Particle Swarm Optimization (QPSO) on single voyages:
- `PHASE3_ARCHITECTURE.md`, `PHASE3_MATHEMATICAL_MODEL.md`, `PHASE3_OPTIMIZATION_SPECIFICATION.md`: Problem formulation and penalty formulations.
- `PHASE3_ASSUMPTIONS.md`, `PHASE3_FAILURE_MODES.md`, `PHASE3_REGULATORY_MODEL.md`: CII, EEXI, and fuel sulfur boundary constraints.
- `PHASE3_BENCHMARK_PROTOCOL.md`, `PHASE3_SCIENTIFIC_GATE_REPORT.md`, `PHASE3_PRE_IMPLEMENTATION_AUDIT.md`: Validation against classical GA, PSO, and DE baselines.
- `PHASE3_2_1_STATISTICAL_INTEGRITY_REPORT.md` & `PHASE3_2_1_CLAIM_LEDGER.yaml`: 30-seed matched random trials and Wilcoxon statistical parity tests.
- `phase3_1_*` audit files: Detailed audits covering budget, fairness, feasibility cliffs, gold pilots, penalty dominance, and solution diversity.

### 4. Phase 4: Heterogeneous Fleet Optimization (`docs/archive_phases/phase4_fleet/`)
Fleet-wide multi-vessel routing, cargo allocation, draft constraints, berth queuing, and alternative green fuel trade-offs:
- `PHASE4_ARCHITECTURE.md`, `PHASE4_MATHEMATICAL_MODEL.md`, `PHASE4_SCENARIO_SPECIFICATION.md`: Mixed-integer formulation and demand satisfaction.
- `PHASE4_FINAL_REPORT.md`, `PHASE4_SIH_STORY.md`: Fleet benchmark narrative and trade-off analysis across 31 non-dominated Pareto solutions.
- `PHASE4_UNCERTAINTY_MODEL.md`, `PHASE4_REGULATORY_MODEL.md`: CVaR weather risk integration and IMO MEPC lifecycle carbon accounting.
- `PHASE4_1_FAILURE_AUDIT.md` & `PHASE4_1_CLAIM_LEDGER.yaml`: Edge case analysis and constraint stress audits.
- `PHASE5_STATUS.md`: Phase 5 staging and release readiness tracking.

### 5. UI & Production Audits (`docs/archive_phases/ui_audits/`)
Operator HMI design evolution, accessibility reviews, and production readiness checks:
- `UI_AUDIT_BEFORE.md`: Baseline review of legacy operational interfaces.
- `UI_PRODUCTION_AUDIT.md`: Zero mock data verification, responsive layout audit, and typed API contract traceability.

### 6. Historical Scratch Scripts (`docs/archive_phases/scripts/`)
Auxiliary test scripts and exploratory notebooks from earlier developmental iterations:
- `test_a0_regression.py`: Diagnostic check for early A0 QPSO edge cases.
- `check_cats.py` & `probe_all.py`: Dataset column and categorical integrity verification scripts.

---

## Note for Continued Development
To continue research or extend any component:
- Model architectures are defined in `prediction/` and `src/models/`.
- Optimizers are located in `optimization/` and `src/algorithms/`.
- API endpoints and schemas are defined in `api/` and `schemas/`.
- Frontend Next.js HMI is located in `web/`.
- All tests are maintained in `tests/` (`python -m pytest tests/`).
