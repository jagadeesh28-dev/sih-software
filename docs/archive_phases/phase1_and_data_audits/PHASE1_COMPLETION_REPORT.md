# Phase 1 Completion Report — SIH26138: Egreen Quanta Platform
**Phase 1: Data Engine + Scientific Validation Gate**  
**Execution Timestamp:** 2026-09-12T12:44:00Z  
**Software Version:** 0.1.0 (Phase 1 Gate Passed)

---

## 1. Data Pipeline Status
The schema-first data pipeline is operational and validated against specified checks:
- **Canonical Schema**: Defined in `data/schemas/canonical_schema.yaml` covering 25 maritime observation channels with exact physical units, datatypes, descriptions, and physical allowable ranges.
- **Unit Normalization**: Handled deterministically in `data/normalization.py`. Conversions log full audit records (`original_value`, `original_unit`, `canonical_value`, `canonical_unit`, `conversion_rule`) with zero silent transformations. Ambiguous units are rejected.
- **Metocean Adapter**: `data/metocean_adapter.py` establishes an extensible interface for point-querying ocean and weather conditions, decoupling environmental grid metadata from ship telemetry.

---

## 2. Dataset Status
- **Synthetic Test Telemetry**: Generated via `data/synthetic_generator.py` and stored at `data/synthetic/synthetic_vessel_telemetry.csv` (1,203 rows, 3 vessels). Strictly tagged with `dataset_type = "SYNTHETIC_TEST_DATA"` and governed by `data/dataset_cards/synthetic_benchmark_dataset.yaml`.
- **Real-World / Zenodo Datasets**: Governed by `data/dataset_cards/zenodo_open_maritime_template.yaml`. Status marked strictly as `PENDING_VALIDATION` with `research_allowed: false` until on-disk files are verified. No unverified datasets were downloaded or fabricated.

---

## 3. Schema Status
- **Canonical Fields**: 25/25 fields active, including `sog_kn`, `stw_kn`, `shaft_power_kw`, `shaft_torque_nm`, `fuel_mass_flow_kg_h`, `wave_height_m`, `engine_load_pct`, etc.
- **Field Definitions**: Loaded through `data/schemas/__init__.py` with backwards-compatible aliases for Phase 0 components.

---

## 4. Quality Audit Results
Audited via `data/data_quality.py` across 16 dimensions without data destruction. Outputs saved to `results/data_quality/`:
- **Total Records Audited**: 1,203
- **Classification Breakdown**:
  - **VALID**: 1,178 (97.9%)
  - **SUSPICIOUS**: 1 (0.1%) (detected timestamp jump)
  - **INVALID**: 9 (0.7%) (controlled anomalies successfully captured: lat > 90, lon < -180, negative fuel flow, negative wave height, impossible speed-power combination, duplicate rows)
  - **MISSING**: 15 (1.2%) (controlled null values detected)
- **Reports Generated**: `dataset_summary.json`, `missingness.csv`, `duplicates.csv`, `range_violations.csv`, `timestamp_gaps.csv`, `quality_report.json`, `quality_report.md`.

---

## 5. Leakage Prevention Status
Implemented and verified in `data/splitting.py`:
- **Chronological Temporal Splitting**: Partitions sorted strictly by timestamp into Train (70%: 824 rows), Validation (15%: 177 rows), and Test (15%: 177 rows). Enforces $\max(t_{train}) \le \min(t_{val})$ and $\max(t_{val}) \le \min(t_{test})$ with zero shuffling.
- **Leave-Vessel-Out Splitting**: Isolates target holdout vessel (`VESSEL_HM_03`, 393 rows) from training set (`VESSEL_FE_01`, `VESSEL_FE_02`, 785 rows) with verified disjoint vessel IDs ($Train \cap Test = \emptyset$).
- **Sister-Vessel Group Isolation**: Maps sister feeder vessels to `CLASS_FEEDER_1000`, guaranteeing that sister vessels remain together in the training set and never leak into the test set.

---

## 6. Independent Physics Validation
Validated against analytical reference calculations in `scientific_validation/validation_gate.py`:
- **Power Calculation**: $P_E = R_T \times V$ and $P_B = P_E / (\eta_D \times \eta_S)$. Hand-calculation ($2,205.65\,\text{kW}$) matches module output with **0.0000% error**.
- **Fuel Rate**: Load-dependent parabolic SFC curve matches hand-calculation ($623.70\,\text{kg/h}$) with **0.0000% error**.
- **ITTC-1957 Friction Line**: $C_F = 0.075 / (\log_{10}(Re) - 2)^2$ verified analytically.
- **Physics Gate Status**: **PASS**.

---

## 7. LCA Validation & Fuel Registry Audit
Audited across all 5 fuel pathways in `configs/fuels.yaml` on a 1,000 kg basis, exported to `results/scientific_validation/lca_audit.csv`:
- **VLSFO**: LHV $40.2\,\text{MJ/kg}$, Total energy $40,200\,\text{MJ}$, WtT $0.54\,\text{tCO}_2\text{e}$, TtW $3.16\,\text{tCO}_2\text{e}$, WtW $3.71\,\text{tCO}_2\text{e}$ ($92.22\,\text{gCO}_2\text{e/MJ}$).
- **Fossil LNG**: LHV $48.0\,\text{MJ/kg}$, Total energy $48,000\,\text{MJ}$, WtT $0.89\,\text{tCO}_2\text{e}$, TtW $3.44\,\text{tCO}_2\text{e}$ (including $0.66\,\text{tCO}_2\text{e}$ from 2.2% methane slip with AR6 GWP=29.8), WtW $4.32\,\text{tCO}_2\text{e}$ ($90.08\,\text{gCO}_2\text{e/MJ}$).
- **Bio-Methanol**: LHV $19.9\,\text{MJ/kg}$, WtW $1.69\,\text{tCO}_2\text{e}$ ($84.78\,\text{gCO}_2\text{e/MJ}$).
- **Green Ammonia**: LHV $18.6\,\text{MJ/kg}$, WtW $0.29\,\text{tCO}_2\text{e}$ ($15.34\,\text{gCO}_2\text{e/MJ}$).
- **Liquid Hydrogen**: LHV $120.0\,\text{MJ/kg}$, WtW $1.44\,\text{tCO}_2\text{e}$ ($12.00\,\text{gCO}_2\text{e/MJ}$).
- **Dimensional Tracking**: $WtW = WtT + TtW$ verified within machine precision.

---

## 8. QPSO Mathematical Benchmark Results
Benchmarked on standard continuous test functions in `scientific_validation/qpso_benchmark.py`:
- **Sphere** ($d=5$): Initial $17.17 \to$ Best $0.0000$ (**100.0% reduction**).
- **Rastrigin** ($d=5$, highly multimodal): Initial $56.16 \to$ Best $2.7222$ (**95.2% reduction**).
- **Rosenbrock** ($d=5$, narrow parabolic valley): Initial $307.32 \to$ Best $1.3096$ (**99.6% reduction**).
- **Bounds & Determinism**: All particles remained strictly within box bounds; seeded runs are 100% deterministic.
- **QPSO Status**: **PASS**.

---

## 9. Automated Test Results
- **Pytest Suite**: 24/24 tests PASSED in 8.68s.
  - Phase 0 Infrastructure & Unit Tests: 14 PASSED.
  - Phase 1 Data Engine Tests: 6 PASSED (`tests/test_phase1_data.py`).
  - Phase 1 Scientific Validation Tests: 4 PASSED (`tests/test_scientific_validation.py`).
- **Smoke Test**: `python -m tests.smoke_test` PASSED with exit code 0.

---

## 10. Scientific Discrepancies Discovered
- **Smoke Test Target Reproduction Check**:
  - $R_{tot}$: Target $= 198,540.1\,\text{N}$, Recomputed $= 198,540.12\,\text{N}$ (rel diff: $0.0000\%$).
  - $P_B$: Target $= 2,189.5\,\text{kW}$, Recomputed $= 2,189.54\,\text{kW}$ (rel diff: $0.0019\%$).
  - Fuel rate: Target $= 619.3\,\text{kg/h}$, Recomputed $= 619.32\,\text{kg/h}$ (rel diff: $0.0036\%$).
  - VLSFO WtW: Target $= 3.71\,\text{tCO}_2\text{e}$, Recomputed $= 3.7073\,\text{tCO}_2\text{e}$ (rel diff: $0.0720\%$).
  - LNG WtW: Target $= 4.32\,\text{tCO}_2\text{e}$, Recomputed $= 4.3236\,\text{tCO}_2\text{e}$ (rel diff: $0.0840\%$).
  - **Assessment**: Discrepancies are purely display rounding artifacts from Phase 0 log prints (2 decimal places); underlying numerical equations are exact.

---

## 11. Corrections Made
1. **Categorical vs Numerical Schema Handling**: Fixed `data_quality.py` to differentiate between categorical lists (e.g. `vessel_type`) and numerical 2-tuples `[min, max]`.
2. **Timestamp Bounds Evaluation**: Handled temporal bounds in `data_quality.py` via ISO datetime comparisons rather than categorical set membership.
3. **Backwards Compatibility Aliases**: Exposed `REQUIRED_VESSEL_FIELDS` and `FIELD_UNITS` in `data/schemas/__init__.py` to maintain compatibility with Phase 0 modules.

---

## 12. Remaining Uncertainties
1. Real vessel operational data from external sources (e.g. Zenodo) remain unverified on disk; all current tests use controlled synthetic data marked `SYNTHETIC_TEST_DATA`.
2. Real-time metocean hindcast API integration (e.g. ECMWF CDS ERA5) will require external API keys if live querying is needed; platform currently utilizes calibrated benchmark regimes.

---

## 13. Evidence Ledger Changes
Updated `evidence/claims.yaml`:
- Added `CLM-009`: Synthetic data epistemic boundary (`FACT`).
- Added `CLM-010`: Data leakage prevention guarantees (`FACT`).
- Added `CLM-011`: QPSO performance on standard continuous benchmark functions (`MEASURED_RESULT`).
- Added `CLM-012`: Phase 0 reproduction and dimensional consistency status (`MEASURED_RESULT`).
- Added `CLM-013`: Zenodo dataset availability and validation status (`ASSUMPTION` / `PENDING_VALIDATION`).
- Added `CLM-014`: Life cycle GHG calculations species-level consistency (`MEASURED_RESULT`).

---

## 14. Exact Next Recommended Phase
**PHASE 2: HYDRODYNAMIC PHYSICS ENGINE**  
Implementation of high-fidelity Holtrop-Mennen resistance, full STAWAVE-2 spectral integration, wind drag, engine load diagrams, and speed-power baseline evaluation.
