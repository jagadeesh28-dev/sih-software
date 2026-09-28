# 16 — Phase 2.3 Real Maritime Telemetry Validation & Scientific Gate Report
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Phase:** 2.3 Real Maritime Data Validation & Model Transfer  
**Gate Status:** **`CONDITIONAL PASS FOR PHASE 3` (Strict In-Domain Restrictions)**  
**Audit Date:** 2026-09-12  
**Lead Scientific ML Engineer & Maritime-Domain Validation Researcher**  

---

## Executive Scientific Verdict

Phase 2.3 subjected the SIH26138 fuel consumption prediction architecture to rigorous **scientific falsification** using **173,974 clean operational telemetry records** from the primary industrial **FuelCast** dataset (`krohnedigital/FuelCast`). Telemetry covers three physical commercial ships: `CPS_Poseidon` (~70,000 GT cruise ship, 1 full year), `CPS_Triton` (~11,000 GT small cruise ship, ~3 months), and `OSS_Ceto` (~24,000 GT offshore supply vessel, ~5 months).

The scientific evaluation establishes:
1. **Target Provenance is Verified Ground Truth (PASS)**: Fuel flow is directly measured by dual industrial KROHNE OPTIMASS Coriolis mass-flow meters ($\Delta \dot{m} = \dot{m}_{\text{inlet}} - \dot{m}_{\text{outlet}}$) registering inertial mass flow in $\text{kg/s}$. Zero circularity; zero reconstruction from shaft power.
2. **Hydrodynamic Operational Generalization Survives (PASS)**: Under `CONFIG-REAL-A` (pure hydrodynamic and metocean inputs without shaft power, torque, or RPM), LightGBM achieves **$\text{MAE} = 263.91\text{ kg/h}$ ($15.69\%$ MAPE) and $R^2 = 0.9400$** across the commercial fleet test partition.
3. **Hybrid Modeling Yields Optimal Performance (PASS)**: The Physics + ML Residual architecture (`MODEL-REAL-04`, $\alpha = 1.0$) achieves the fleet's best overall accuracy: **$\text{MAE} = 246.97\text{ kg/h}$ ($14.63\%$ MAPE) and $R^2 = 0.9501$**, statistically outperforming pure ML-A ($p = 7.45 \times 10^{-18}$, Wilcoxon signed-rank test).
4. **Frozen Synthetic-to-Real Transfer Collapses (FAIL — Falsification Confirmed)**: Direct transfer of the Phase 2 synthetic-trained baseline without retraining yields **$\text{MAE} = 2,028.51\text{ kg/h}$ and $R^2 = -0.9447$**. The synthetic assumptions fail due to severe scale divergence ($< 700\text{ kg/h}$ vs $> 8,600\text{ kg/h}$) and unmodeled hotel electrical loads.
5. **Cross-Class Leave-Vessel-Out Generalization Collapses (FAIL — Domain Divergence)**: Leave-Vessel-Out across disparate vessel classes (large cruise vs small cruise vs offshore DP vessel) collapses ($R^2 < 0$ on all 3 folds).
6. **Quantile Uncertainty Under-Covers on Real Noise (FAIL — Miscalibrated)**: Nominal 90% prediction intervals achieve empirical **$\text{PICP} = 78.51\%$** (Wilson 95% CI: $[78.08\%, 78.94\%]$). Conformal calibration is mandatory for Phase 3.
7. **SafeFuelObjective Prevents Adversarial Optimization Exploits (PASS)**: In 7 of 8 deliberate adversarial exploit scenarios (negative power, ungrounded high speed at zero power, impossible draft, hurricane seas), `SafeFuelObjective` triggered a $100,000\text{ kg/h}$ penalty barrier, repelling optimizer drift.

**FINAL GATE DETERMINATION:** **`CONDITIONAL PASS`**  
Phase 3 optimization is permitted **strictly under in-domain operational constraints** on profiled vessel classes utilizing `SafeFuelObjective`. Zero-shot cross-class fleet optimization and claims of "universal generalization" remain strictly forbidden.

---

## 1. Unified Real-Data Prediction Leaderboard

Evaluated strictly on the held-out 20% chronological test partitions ($n_{\text{test}} = 34,796$ records):

| Model ID | Architecture | Feature Configuration | MAE ($\text{kg/h}$) | RMSE ($\text{kg/h}$) | MAPE ($\%$) | $R^2$ | Median AE ($\text{kg/h}$) | Bias ($\text{kg/h}$) | PICP 90% | MPIW ($\text{kg/h}$) | Runtime (s) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **MODEL-REAL-04** | **Hybrid Residual ($\alpha=1.0$)** | **Physics + ML-A (No Power)** | **246.97** | **443.21** | **14.63%** | **0.9501** | **129.31** | -141.82 | N/A | N/A | 10.87 |
| **MODEL-REAL-02** | Pure ML (LightGBM) | CONFIG-REAL-A (Hydro Only) | 263.91 | 486.05 | 15.69% | 0.9400 | 138.08 | -146.19 | 0.7851 | 1490.71 | 0.63 |
| **MODEL-REAL-03** | Pure ML (LightGBM) | CONFIG-REAL-B (Machinery-Aware) | 352.72 | 983.46 | 13.93% | 0.7543 | 90.49 | -301.95 | 0.7851 | 1490.71 | 0.60 |
| **MODEL-REAL-01** | Holtrop-Mennen | First-Principles Naval Arch | 1885.45 | 2468.05 | 72.56% | -0.5471 | 1228.38 | -1883.19 | N/A | N/A | 1.61 |
| **MODEL-REAL-05** | Frozen Synthetic ML | Transferred (Zero Retraining) | 2028.51 | 2767.01 | 71.00% | -0.9447 | 1208.21 | -2027.19 | N/A | N/A | 0.18 |

### Per-Vessel Breakdown Under CONFIG-REAL-A:
- **`CPS_Poseidon`** (70,000 GT Cruise): Mean Fuel = $2,815.4\text{ kg/h}$ $\to$ **MAE = 331.26 kg/h ($10.68\%$ MAPE), $R^2 = 0.8939$**
- **`CPS_Triton`** (11,000 GT Cruise): Mean Fuel = $635.1\text{ kg/h}$ $\to$ **MAE = 74.40 kg/h ($23.57\%$ MAPE), $R^2 = 0.7782$**
- **`OSS_Ceto`** (24,000 GT OSV): Mean Fuel = $675.6\text{ kg/h}$ $\to$ **MAE = 210.77 kg/h ($23.29\%$ MAPE), $R^2 = 0.3540$**

---

## 2. Answers to the 10 Scientific Falsification Questions

### Q1: Does the synthetic model transfer to real maritime data?
**VERDICT: `FAIL` (SYNTHETIC-TO-REAL TRANSFER FAILURE)**  
- **Empirical Evidence**: The frozen Phase 2 synthetic model evaluated on FuelCast test data achieved $R^2 = -0.9447$, $\text{MAE} = 2,028.51\text{ kg/h}$, and a systematic negative bias of $-2,027.19\text{ kg/h}$.
- **Root Cause**: The synthetic benchmark was generated for a single feeder container vessel operating between 0 and 700 kg/h. Real cruise passenger vessels burn up to 8,610 kg/h with 1,000–2,000 kg/h consumed by hotel loads alone. The synthetic model severely underpredicts and cannot generalize zero-shot.

### Q2: Does physics improve prediction on real data?
**VERDICT: `PASS` (HYBRID RESIDUAL SUPERIORITY)**  
- **Empirical Evidence**: Pure uncalibrated naval architecture physics (`MODEL-REAL-01`) fails alone ($R^2 = -0.5471$, $\text{MAE} = 1,885.45\text{ kg/h}$) because Holtrop-Mennen omits hotel electrical loads and azipod thruster appendages. However, the Hybrid Residual model (`MODEL-REAL-04`) combining first-principles resistance with ML residual learning achieves the **lowest MAE ($246.97\text{ kg/h}$) and highest $R^2$ ($0.9501$)**, outperforming pure ML-A ($263.91\text{ kg/h}$) with high statistical significance ($p = 7.45 \times 10^{-18}$).

### Q3: Does environmental information materially improve prediction?
**VERDICT: `PASS` (STATISTICALLY VALIDATED CONTRIBUTION)**  
- **Empirical Evidence**: Ablating wave parameters ($H_s, T_p, \theta_{\text{wave}}$) increased test RMSE by $+29.57\text{ kg/h}$ and degraded $R^2$ by $0.0150$. Ablating wind channels increased RMSE by $+11.65\text{ kg/h}$. Metocean features provide essential resistance signals.

### Q4: Does shaft power dominate the prediction?
**VERDICT: `CONDITIONAL` (LEGITIMATE MACHINERY INFORMATION, NOT LEAKAGE)**  
- **Empirical Evidence**: In `CONFIG-REAL-A`, fuel flow is accurately predicted ($R^2 = 0.9400$) **without shaft power**. In `CONFIG-REAL-B`, adding shaft power improves dynamic positioning predictions on `OSS_Ceto` (MAE drops from $210.77$ to $73.66\text{ kg/h}$). Shaft power is physically upstream via engine BSFC, making it an operationally legitimate machinery feature for instantaneous estimation, though unnecessary for pure hydrodynamic routing.

### Q5: Does vessel identity create memorization?
**VERDICT: `PASS` (RESISTANT TO MEMORIZATION)**  
- **Empirical Evidence**: Adding `vessel_id` to CONFIG-REAL-B produced no meaningful improvement ($\Delta\text{MAE} = +1.28\text{ kg/h}$, $\Delta R^2 = -0.0021$) and failed to prevent collapse during Leave-Vessel-Out testing ($R^2 < 0$).

### Q6: Does LVO performance collapse?
**VERDICT: `FAIL` (CROSS-CLASS DOMAIN COLLAPSE)**  
- **Empirical Evidence**: 3-fold Leave-Vessel-Out testing yielded:
  - Fold 1 (`CPS_Poseidon` test): $R^2 = -1.1102$, $\text{MAE} = 1,914.60\text{ kg/h}$
  - Fold 2 (`CPS_Triton` test): $R^2 = -59.6368$, $\text{MAE} = 1,731.72\text{ kg/h}$
  - Fold 3 (`OSS_Ceto` test): $R^2 = -10.1978$, $\text{MAE} = 1,210.55\text{ kg/h}$
- **Root Cause**: The fleet represents fundamentally distinct vessel typologies (70k GT cruise vs 11k GT small cruise vs offshore supply). Generalization across disparate ship categories without vessel-specific hydrostatic calibration is scientifically impossible.

### Q7: Does uncertainty remain calibrated?
**VERDICT: `FAIL` (MISCALIBRATED / UNDER-COVERING)**  
- **Empirical Evidence**: Nominal 90% prediction intervals $[q_{05}, q_{95}]$ achieved empirical **$\text{PICP} = 78.51\%$** on real fleet test telemetry (Wilson 95% CI: $[78.08\%, 78.94\%]$) with $\text{MPIW} = 1,490.71\text{ kg/h}$. Real-world sensor noise causes the quantile model to under-cover by $11.49\%$. Conformal calibration is required.

### Q8: Does SafeFuelObjective reject legitimate real states?
**VERDICT: `CONDITIONAL` (OPERATIONAL ENVELOPE GAP IDENTIFIED)**  
- **Empirical Evidence**: Synthetic heuristic rule ($STW < 2.0\text{ kn}$ and $P > 5,000\text{ kW}$) rejected $93.85\%$ of legitimate operational test states on `OSS_Ceto`.
- **Root Cause**: Offshore supply vessels routinely engage in Dynamic Positioning (DP) station-keeping where speed is near zero while thrusters deliver megawatt power against wind and waves. Domain envelopes must be parameterized per vessel class.

### Q9: Can the surrogate still be adversarially exploited?
**VERDICT: `PASS` (DEFENSIVE INTERFACE MITIGATES UNGROUNDED TROUGHS)**  
- **Empirical Evidence**: Out of 8 adversarial stress tests, `SafeFuelObjective` successfully repelled optimizer exploitation in all cases: 7 resulted in hard rejection ($100,000\text{ kg/h}$ penalty) and 1 was penalized with `CAUTION`. Raw ML would have accepted negative power and zero-power cruise states.

### Q10: Is the current model sufficiently trustworthy for optimization?
**VERDICT: `CONDITIONAL PASS` (STRICT IN-DOMAIN FLEET RESTRICTIONS)**  
- **Empirical Evidence**: The model is trustworthy for speed and trim optimization within the empirical operating domain of evaluated vessels using `SafeFuelObjective`. It is NOT trustworthy for unmonitored vessels, cross-class fleet optimization, or uncalibrated zero-shot transfer.

---

## 3. Statistical Validation Matrix (Stage 18)

Paired sample tests across identical test observations ($n = 2,000$, Wilcoxon signed-rank test):

| Comparison | Mean $\Delta$ Error ($\text{kg/h}$) | Median $\Delta$ Error ($\text{kg/h}$) | 95% Confidence Interval | Wilcoxon $W$ | $p$-value | Effect Size $r$ | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hybrid vs. ML Config-A** | **-16.94** | **-9.65** | **[-275.13, 155.47]** | **778,167.0** | **$7.45 \times 10^{-18}$** | **0.1925** | **Significant ($p < 0.001$)** |
| **ML Config-A vs. Physics** | **-1621.54** | **-1082.90** | **[-3931.72, 46.02]** | **22,905.0** | **$0.0000$** | **0.2236** | **Significant ($p < 0.001$)** |
| **ML Config-B vs. ML Config-A** | +88.81 | -32.15 | [-555.77, 2707.76] | 718,958.0 | $1.15 \times 10^{-27}$ | 0.2437 | Significant ($p < 0.001$) |

### 10-Seed Stochastic Benchmark:
- **CONFIG-REAL-A**: Mean MAE = $263.11\text{ kg/h}$ (std = $2.79\text{ kg/h}$, $95\%$ CI: $[258.78, 267.10]\text{ kg/h}$)
- **CONFIG-REAL-B**: Mean MAE = $330.37\text{ kg/h}$ (std = $2.81\text{ kg/h}$, $95\%$ CI: $[326.07, 333.76]\text{ kg/h}$)

---

## 4. Operational Restrictions for Phase 3 Fleet Optimization

Phase 3 optimization is conditionally authorized under the following mandatory constraints:

1. **Mandatory Safe Objective Wrapper**: All candidate evaluations must pass through `SafeFuelObjective`. Raw ML surrogates are forbidden.
2. **Strict In-Domain Bounding**: Optimization search spaces must be bounded by the fitted `DomainChecker` empirical envelope (P01–P99) of the target vessel.
3. **Vessel-Class Specific Profiles**: Cruise ships and offshore DP vessels must use specialized domain checkers to accommodate hotel loads and DP station-keeping.
4. **Uncertainty Penalty Term**: Optimization must use the risk-adjusted objective:
   $$J(\lambda) = \hat{F}_{\text{median}} + \lambda \cdot (q_{95} - q_{05}), \quad \lambda \ge 0.5$$
5. **No Cross-Class Extrapolation**: Models must never optimize voyages for vessel classes outside the training set.
6. **Result Labeling**: All Phase 3 optimization outputs must carry the provenance label:
   `REAL_TELEMETRY_VALIDATED_IN_DOMAIN_OPTIMIZATION`.
