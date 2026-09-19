# PHASE 7 — STEP 0: REPOSITORY FREEZE & PRODUCTION RELEASE BASELINE
## SIH26138 — Egreen Quanta
### Complete System Inventory, Cryptographic Manifest, and Production Architecture Specification

**Date:** September 19, 2026  
**Auditor:** Principal ML Engineer, Safety-Critical Systems Lead, Reproducibility Auditor  
**Phase Status:** PHASE 7.0 REPOSITORY BASELINE LOCKED  

---

## 1. System Environment & Execution Provenance

| Environment Parameter | Value / Cryptographic Specification |
| :--- | :--- |
| **Project Identifier** | **SIH26138 — Egreen Quanta** |
| **Release Version** | **v1.0.0-rc1** |
| **Git Commit SHA** | `20309b214b9540a7363b7365e442a222cd9c49a1` |
| **Active Git Branch** | `master` |
| **Operating System** | `Windows-11-10.0.26200-SP0 (AMD64)` |
| **Processor (CPU)** | Intel64 Family 6 Model 183 Stepping 1, GenuineIntel (16 Cores) |
| **System Memory (RAM)**| 15.63 GB |
| **Python Environment** | CPython 3.14.0 (tags/v3.14.0:ebf955d, Oct 7 2025) |
| **NumPy Version** | 2.2.6 |
| **SciPy Version** | 1.17.0 |
| **Pandas Version** | 2.3.3 |
| **PyArrow Version** | 23.0.0 |
| **Scikit-Learn Version**| 1.8.0 |
| **LightGBM Version** | 4.7.0 |
| **Matplotlib Version** | 3.10.8 |

---

## 2. Cryptographic Dataset & Configuration Ledger

All files required by the production runtime are tracked by SHA256 checksums to guarantee zero silent modification:

### 2.1 Telemetry Datasets (`data/processed/real/fuelcast/`)
- `CPS_Poseidon.parquet`: `da85f2e21b6e8724c8350f9aadbda4e457593d77412b8cefaa077da9e1e260c2` (105,422 rows, 25,733,215 bytes)
- `CPS_Triton.parquet`: `fa8cc7f9f6a92d330088e41e3f275b8d8428d3604cfb35dfa46eaa753d545f89` (25,347 rows, 7,476,397 bytes)
- `OSS_Ceto.parquet`: `ac3f8d5e865f11cd40f147d6153de9915b543f675684719245a2d5d6d8e752cd` (43,205 rows, 10,283,734 bytes)
- **Total Validated Experimental Records:** **173,974 rows** (Raw Total: 173,986 rows; 12 trailing padding rows dropped in Phase 2.3).

### 2.2 Model & Configuration Specifications
- `PHASE6/config/baseline.yaml`: `ec977675c77614b61839ab8cac7fd9bdb29cb655948618100f3c4e8302f83553`
- `PHASE6/config/qi_c1.yaml`: `4c82f5c746ed209dffb5a00870b9ac8641839496a6e6388eca918521683559ba`
- `PHASE6/config/normalization.json`: `909d65f3d59caaf6c913db507b810d254579c9b0c90461443cb7663862b651e3`
- `configs/physics.yaml`: `0400423141c0308bdb9e43039ae1024e9ecafabeec1e9053c7171b71d17340ef`
- `configs/fuels.yaml`: `329f7d95d018b22ab5c17a37bf442a708f24c29613dd47874816c8e6b9a9bb2b`
- `configs/regulations.yaml`: `c654594db056b2224051b1b493c50ebb2ab3f67acb7eb37867b17292d10aad4f`

---

## 3. Production vs. Research Component Boundary

To prevent dead code or failed research experiments from leaking into the demo or production pipeline:

### 3.1 Production-Path Components (Active & Supported)
1. **Hydrodynamic Physics Pipeline (`physics/`):** First-principles Holtrop-Mennen calm water resistance, IMO STAwave-2 wave added resistance, and Blendermann wind drag, strictly locked to Speed Through Water (STW).
2. **Primary Prediction Engine (`QI-C1`):** Quantum-Inspired Evolutionary Feature Selection (`src/qi_prediction/qiea.py`) selecting 8 optimal hydrodynamic features, combined with LightGBM residual learning.
3. **Reference & Fallback Engine (`MODEL-REAL-04`):** Frozen physics + ML residual predictor with zero metaheuristic stochasticity.
4. **Domain Guardian (`prediction/safe_objective.py`, `prediction/domain_checker.py`):** Mahalanobis distance OOD detector and conformal quantile uncertainty calculator.
5. **Thermodynamic Scenario Layer (`optimization/cost_model.py`, `configs/fuels.yaml`):** Shaft mechanical energy conservation ($E_{shaft} = \int P_B dt$) calculating fuel mass flow for LNG, methanol, ammonia, and hydrogen.
6. **Regulatory Layer (`optimization/regulatory.py`, `configs/regulations.yaml`):** FuelEU Maritime WtW intensity, EU ETS operational carbon pricing, and IMO CII rating engine.
7. **Fleet Optimization Engine (`optimization/fleet_evaluator_phase4.py`, `src/algorithms/de.py`):** Multi-objective Differential Evolution and A5 QI-HFO with Deb's feasibility-first constraint handling and Hungarian route repair.

### 3.2 Research-Only Components (Excluded from Production Path)
1. **Candidate QI-C2 (MPS Tensor Network, `src/qi_prediction/mps_predictor.py`):** Proved to suffer unconstrained gradient divergence on tabular telemetry. Retained strictly in `research/` as an audited negative finding.
2. **Online QPSO Tuning (`src/qi_prediction/qpso.py`):** Evaluated experimentally in Phase 6; offline-tuned hyperparameters are frozen into `production.yaml` to prevent runtime stochastic latency during real-time dispatch.

---

## 4. Unresolved Discrepancies & Resolutions

| Item | Previously Reported State | Reconciled Verified State | Root Cause & Resolution |
| :--- | :--- | :--- | :--- |
| **Telemetry Record Count** | Inconsistent references to `173,986` and `173,974` | **173,986 Raw Records; 173,974 Active Experimental Records** | Exactly 12 trailing padding rows with null timestamps (4 on Triton, 8 on Ceto) were dropped in Phase 2.3 data quality cleaning. Fully reconciled in Phase 7.2. |
| **Baseline MAE** | Reported as 246.97 kg/h in single test run, 248.12 kg/h in 30-seed mean | **Both are exact and verified** | 246.97 kg/h is Seed 42 exact test score; 248.12 kg/h is the 30-seed matched mean across seeds 1001–1029. Both documented transparently. |
| **Alternative Fuel Claims** | Ambiguity between "predicted" vs "simulated" green fuels | **Formally Classified: PHYSICS-BASED THERMODYNAMIC SCENARIOS** | Explicitly documented that real telemetry is conventional fuel. Alternative fuel calculations are energy-equivalent thermodynamic conversions. |

---

## 5. Exact Files Requiring Modification vs. Untouchable Files

### 5.1 Exact Files Requiring Hardening / Production Creation
- `PHASE7/config/feature_contract.yaml`: Immutable schema, unit, and range contract.
- `PHASE7/config/production.yaml`: Centralized production parameters.
- `src/qi_prediction/serving.py`: Clean production inference API (`predict_fuel`, `predict_fuel_with_uncertainty`).
- `scripts/reproduce_release.py`: Single-command jury verification runner.
- All Phase 7 audit markdown reports, CSV datasets, and the `RELEASE/` distribution directory.

### 5.2 Exact Files That Must Remain Untouched (Strict Freeze)
- `optimization/fleet_evaluator_phase4.py` (Phase 5 Evaluator — FROZEN)
- `src/evaluator/common_evaluator.py` (Phase 5 Evaluator Interface — FROZEN)
- `src/algorithms/de.py` (Phase 5 Optimizer — FROZEN)
- `physics/resistance_model.py` (Physics Pipeline — FROZEN)
- `data/processed/real/fuelcast/*.parquet` (Telemetry — FROZEN)
- `PHASE6/` (All Phase 6 audit files — FROZEN)

---

## 6. Proposed Release Test Matrix (Phase 7 Gates)

The release verification will execute a 36-step protocol structured across six formal gates:
1. **Scientific Integrity Gate:** 100% verification of baseline reproduction, QIEA parity, and statistical transparency.
2. **Software Quality Gate:** 100% unit, integration, and regression test passage; elimination of hardcoded local paths.
3. **Safety-Critical Gate:** 1,000 automated stress tests; rejection of malformed/OOD inputs; safe model fallback.
4. **Reproducibility Gate:** Single-command clean execution via `python scripts/reproduce_release.py`.
5. **Downstream Integration Gate:** End-to-end trace from raw telemetry to Pareto fleet dispatch solutions.
6. **Presentation & Hostile Jury Gate:** Zero forbidden claims; 100% claim-to-artifact traceability.
