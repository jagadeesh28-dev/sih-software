# PHASE 6: SCIENTIFIC REPRODUCIBILITY MANIFEST
## SIH26138 — Egreen Quanta
**Audit Date:** 2026-09-19  
**Protocol Version:** `6.0-FROZEN`  
**Status:** `VERIFIED & REPRODUCIBLE`  

---

### 1. Hardware and System Architecture

All experiments in Phase 6 were executed strictly on classical computing hardware without any specialized quantum coprocessors, QPUs, or quantum simulators:

| Parameter | Host Specification |
|---|---|
| **Operating System** | Microsoft Windows 11 Home (Build 26100 / AMD64) |
| **Processor (CPU)** | Intel Core Ultra / AMD Ryzen x86_64 Architecture |
| **Physical Memory (RAM)** | 16.0 GB DDR5 |
| **Quantum Hardware Used** | **NONE** (Strictly Classical Hardware Execution) |
| **Quantum Simulators Used** | **NONE** (All mathematical algorithms are closed-form classical vector/matrix equations) |

---

### 2. Software Runtime Environment

| Package | Version | Primary Role in Phase 6 |
|---|---|---|
| **Python** | `3.14.0` | Core interpreter |
| **NumPy** | `2.2.6` | Vectorized numerical linear algebra and Q-bit amplitudes |
| **SciPy** | `1.17.0` | Wilcoxon signed-rank, Hodges-Lehmann, and Mahalanobis statistics |
| **Pandas** | `2.3.0` | High-throughput parquet telemetry ingestion and temporal slicing |
| **LightGBM** | `4.7.0` | Gradient boosted tree residual regressor |
| **Scikit-Learn** | `1.8.0` | Polynomial feature transforms, MinMax scalers, Ridge regression |
| **Matplotlib** | `3.10.8` | High-resolution publication diagnostic figure generation (Agg backend) |
| **PyYAML** | `6.0.2` | Machine-readable benchmark configuration loading |
| **PyTest** | `9.1.1` | Automated unit and regression test suite |

---

### 3. Data Provenance and Partitioning Integrity

- **Primary Repository:** FuelCast Real Maritime Telemetry.
- **Vessels Evaluated:**
  1. `CPS_Poseidon`: 105,422 rows (Container Feeder, 24,000 t displacement)
  2. `CPS_Triton`: 25,347 rows (Container Feeder, 24,000 t displacement)
  3. `OSS_Ceto`: 43,205 rows (Bulk Handymax, 45,000 t displacement)
- **Total Records:** 173,974 records.
- **Partitioning Method:** Chronological Forward Temporal (60% Train, 20% Validation, 20% Test per vessel, combined into fleet sets).
- **Zero-Leakage Assurance:**
  - Zero row shuffling.
  - Zero future data in training partitions.
  - Scalers and encoders fit strictly on `TRAIN`.
  - Target `fuel_mass_flow_kg_h` excluded from input features.

---

### 4. Random Seed Protocol

All stochastic algorithms (QIEA, Classical GA, QPSO, Classical PSO, Random Search, and LightGBM) were executed across **30 matched random seeds**:
```python
MATCHED_SEEDS = [
    42, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
    1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019,
    1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029
]
```
Seed pairing ensures that statistical tests (paired Wilcoxon signed-rank test and Hodges-Lehmann median difference) compare candidate models and classical controls under identical pseudo-random initialization trajectories.

---

### 5. Execution Commands to Reproduce

```powershell
# 1. Verify frozen baseline reproduction (reproduces R2=0.9501, MAE=246.97)
python scripts/phase6_baseline_reproduce.py

# 2. Run automated unit test suite (19 tests)
python -m pytest tests/test_qiea.py tests/test_qpso.py tests/test_mps_predictor.py tests/test_no_leakage.py tests/test_physics_constraints.py tests/test_reproducibility.py -v

# 3. Execute master 30-seed benchmark pipeline
python -u -c "from src.qi_prediction.benchmark import run_master_benchmark; run_master_benchmark(seed_limit=30)"

# 4. Execute downstream fleet optimizer integration test
python experiments/run_phase6_downstream_integration.py
```
