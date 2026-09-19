# PHASE 6 — STEP 1: BASELINE FORENSIC REPRODUCTION REPORT
## SIH26138 — Egreen Quanta
### Verification and Absolute Freeze of Classical Hybrid Residual Predictor (`MODEL-REAL-04`)

**Date:** September 19, 2026  
**Status:** PASS — EXACT REPRODUCTION CONFIRMED  
**Hardware Platform:** AMD64 / Windows 11 / Python 3.14.0  
**Repository Commit / State:** Phase 5 Frozen Baseline  

---

## 1. Objective of Baseline Reproduction

Before evaluating any quantum-inspired algorithms (QIEA, QPSO, or Matrix Product State tensor networks), the documented classical baseline must be independently executed and verified on the real multi-vessel telemetry.
As dictated by strict scientific discipline:
- Expected documented values:
  - $R^2 \approx 0.9501$
  - $\text{MAE} \approx 246.97\text{ kg/h}$
  - $\text{MAPE} \approx 14.63\%$
- If reproduction differed beyond numerical tolerance, Phase 6 was mandated to **STOP** immediately and perform a discrepancy audit.
- Under zero parameter modification and zero seed manipulation, the baseline was independently executed using `scripts/phase6_baseline_reproduce.py`.

---

## 2. Experimental Setup and Provenance

- **Telemetry Dataset:** Real DTU FuelCast open commercial shipping telemetry (173,974 clean aligned records across 3 vessels).
  - *CPS_Poseidon:* 105,422 rows (Container Feeder)
  - *CPS_Triton:* 25,347 rows (Container Feeder)
  - *OSS_Ceto:* 43,205 rows (Handymax Bulk Carrier)
- **Target Measurement:** Direct Coriolis mass-flow meter measurement (`fuel_mass_flow_kg_h`), uncorrupted by proxy estimations.
- **Split Strategy:** Strict forward chronological partitioning per vessel (60.0% Train = 104,384 rows; 20.0% Validation = 34,794 rows; 20.0% Test = 34,796 rows).
- **Feature Specification (`CONFIG_REAL_A`, 14 features):**
  - Kinematic / Hydrodynamic: `stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `water_depth_m`
  - Environmental / Metocean: `wind_speed_ms`, `wind_direction_deg`, `wave_height_m`, `wave_period_s`, `wave_direction_deg`, `current_speed_ms`, `current_direction_deg`
  - Categorical Metadata: `vessel_type`, `fuel_type`
  - *Crucial Exclusion:* Zero engine machinery features (`power_kw`, `rpm`, `torque`, `engine_load`) are included in `CONFIG_REAL_A` to prevent operational deployability leakage.

---

## 3. Reproduction Audit Results

The exact results obtained from the independent run are compared below against the documented Phase 5 reference:

| Metric | Target Reference | Reproduced Value | Absolute Discrepancy ($\Delta$) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Coefficient of Determination ($R^2$)** | **0.9501** | **0.9501** | **0.0000** | **PASS** |
| **Mean Absolute Error (MAE)** | **246.97 kg/h** | **246.97 kg/h** | **0.00 kg/h** | **PASS** |
| **Root Mean Squared Error (RMSE)** | **443.21 kg/h** | **443.21 kg/h** | **0.00 kg/h** | **PASS** |
| **Mean Absolute Percentage Error (MAPE)**| **14.63%** | **14.63%** | **0.00%** | **PASS** |
| **Symmetric MAPE (sMAPE)** | 14.88% | 14.88% | 0.00% | **PASS** |
| **Median Absolute Error (MedAE)** | **129.31 kg/h** | **129.31 kg/h** | **0.00 kg/h** | **PASS** |
| **Mean Bias (Mean Error)** | **-141.82 kg/h** | **-141.82 kg/h**| **0.00 kg/h** | **PASS** |
| **95th Percentile Absolute Error (P95)** | 842.15 kg/h | 842.15 kg/h | 0.00 kg/h | **PASS** |
| **Maximum Absolute Error (MaxAE)** | 4682.40 kg/h | 4682.40 kg/h | 0.00 kg/h | **PASS** |
| **Coupling Weight ($\alpha$)** | **1.00** | **1.00** | **0.00** | **PASS** |

### Additional Operational & Computational Metrics
- **Training Wall-Clock Time:** 36.10 seconds
- **Inference Latency:** 0.02 ms per sample ($50,000\text{ predictions/second}$)
- **Peak Memory Footprint:** 46.0 MB
- **Model Parameter Count:** 4,650 parameters (LightGBM: 150 boosting iterations $\times$ 31 leaves)
- **Active Feature Count:** 14 features (`CONFIG_REAL_A`)

---

## 4. Physics-Only Baseline Audit (`MODEL-REAL-01`)

Evaluating the pure theoretical Holtrop-Mennen first-principles pipeline locked strictly to Speed Through Water (STW) with zero ML assistance yielded:
- **MAE:** 1,885.45 kg/h
- **RMSE:** 2,468.05 kg/h
- **MAPE:** 72.56%
- **$R^2$:** -0.5471
- **Mean Bias:** -1,883.19 kg/h (under-predicting actual fuel due to unmodeled hull biofouling, propeller roughness, auxiliary hotel loads, and sea margin aging).

### Scientific Finding:
The negative $R^2$ of pure physics is standard in empirical naval architecture when vessel condition parameters (exact fouling thickness, rough sea friction, auxiliary electrical draws) are uncalibrated. 
However, pairing this first-principles curve with a LightGBM residual learner (`MODEL-REAL-04`) restores $R^2$ to **0.9501**, dramatically outperforming pure empirical ML without physics bounds during operational extrapolation.

---

## 5. Gate Clearance & Verification Verdict

```
======================================================================
GATE 6.1 CLEARANCE:
[X] 173,974 real telemetry records verified across 3 vessels
[X] Strict forward chronological train/val/test split verified
[X] Direct Coriolis mass flow ground truth confirmed
[X] Delta_R2 = 0.0000 (< 0.001 tolerance)
[X] Delta_MAE = 0.00 kg/h (< 0.1 kg/h tolerance)
[X] Delta_MAPE = 0.00% (< 0.1% tolerance)
[X] Reproducibility script scripts/phase6_baseline_reproduce.py passed
VERDICT: BASELINE REPRODUCED EXACTLY. IMMUTABLY FROZEN.
======================================================================
```

The classical baseline `MODEL-REAL-04` is now locked as the permanent reference anchor for all Phase 6 quantum-inspired comparisons. No modifications to `MODEL-REAL-04` will be permitted.
