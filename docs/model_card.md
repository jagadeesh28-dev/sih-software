# Model Card: Egreen Quanta Predictive Architecture
**Models Evaluated**: `QI-C1` (Quantum-Inspired Feature-Selected Residual Model) & `MODEL-REAL-04` (Classical Hybrid Baseline)  
**Release Gate**: 1.0.0-verified | **Audit Date**: September 2026  

---

## 1. Model Details

### Primary Evaluated Models

#### 1. QI-C1 (Candidate Prediction Path)
- **Architecture**: Quantum-Inspired Evolutionary Algorithm (QIEA) Feature Selection + Quantum-Behaved Particle Swarm Optimization (QPSO) Hyperparameter Search + LightGBM Gradient Boosted Decision Trees on Physics Residuals.
- **Formulation**: Residual learning atop first-principles hydrodynamic resistance:
  $$\hat{y}_{\text{total}} = f_{\text{phys}}(\mathbf{x}) + \hat{r}_{\text{QI-C1}}(\mathbf{x}_{\text{sub}})$$
- **Selected Features (Seed 42)**: 6 features (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `fuel_type`).
- **Target Variable**: Fuel mass flow rate ($\text{kg/h}$).

#### 2. MODEL-REAL-04 (Reference Anchor / High-Reliability Fallback)
- **Architecture**: Classical Hybrid Holtrop-Mennen Resistance Estimator + Full 14-Feature LightGBM Residual Booster.
- **Role**: Stable reference anchor, cross-check baseline, and high-uncertainty fallback.
- **Selected Features**: All 14 features of `CONFIG_REAL_A`.

---

## 2. Quantitative Performance & Metric Reconciliation

### Forward Temporal Evaluation (34,796 Held-Out Records)

| Model Architecture | Seed 42 MAE ($\text{kg/h}$) | Seed 42 $R^2$ | 30-Seed Matched MAE ($\text{kg/h}$) | 30-Seed Matched $R^2$ | Feature Count | 90% Conformal MPIW ($\text{kg/h}$) | 90% Empirical Coverage |
|:-------------------|:----------------------------|:--------------|:------------------------------------|:----------------------|:--------------|:-----------------------------------|:-----------------------|
| **Pure Physics Baseline** | 1,885.45 | -0.5471 | N/A (Deterministic) | N/A | 14 | N/A | N/A |
| **MODEL-REAL-04** (Reference) | 246.91 | 0.9503 | 248.12 ± 0.81 | 0.9501 | 14 | 2,273.70 | 95.05% |
| **Classical GA Control** | 237.24 | 0.9532 | 237.24 ± 4.89 | 0.9532 | 6 | 1,598.20 | 93.40% |
| **QI-C1** (Candidate) | **244.86** | **0.9500** | **237.96 ± 5.46** | **0.9530** | **6** | **1,564.93** | **93.56%** |

### Reconciliation of Phase 6 vs Phase 7 Metrics
- **Phase 6 Report**: $\text{MAE} = 237.96\text{ kg/h}$, $R^2 = 0.9530$ represents the **30-seed matched mean** across stochastic search seeds `[42, 1001, ..., 1029]`.
- **Seed 42 Exact Run**: $\text{MAE} = 244.86\text{ kg/h}$, $R^2 = 0.9500$ is the deterministic point-evaluation for Seed 42 using the QIEA-selected 6-feature subset.
- **Phase 7 Discrepancy Resolved**: The earlier Phase 7 reporting of $\text{MAE} = 255.60\text{ kg/h}$ was traced to an unverified 8-feature subset in `build_production_models.py` that inadvertently omitted the categorical `fuel_type` feature. When restored to the verified 6 QIEA features, Seed 42 achieves $\text{MAE} = 244.86\text{ kg/h}$.

---

## 3. Statistical Interpretation & Honest Scientific Claims
1. **Statistical Parity, Not Superiority**: A Wilcoxon signed-rank test between QI-C1 (30 seeds) and Classical GA (30 seeds) yields $p = 0.684$. QI-C1 is **statistically competitive** with the classical control; claims of "quantum superiority" are empirically **REJECTED**.
2. **Diversity Advantage**: QIEA maintains $+44.7\%$ higher population bit-entropy ($H = 0.2814$ vs $0.1945$) throughout optimization, demonstrating superior exploration without premature stagnation.
3. **Sharpness Benefit**: Under inductive conformal prediction, QI-C1 yields a **$31.17\%$ narrower interval** ($1,564.93\text{ kg/h}$ vs $2,273.70\text{ kg/h}$) while maintaining $93.56\%$ empirical test coverage (well above the $90.0\%$ nominal floor).

---

## 4. Operational Model Routing Policy
In production serving, QI-C1 is **NOT** forced unconditionally. A multi-tier safety router governs execution:

```
                  OPERATIONAL INPUT
                          │
                          ▼
                Input Validation Gate
             (Schema & Physical Contracts)
                          │
                          ▼
                 Domain Envelope Guard
             (Mahalanobis / Envelope Dist)
              /                         \
       In-Domain (dist ≤ 1.5)      Severe OOD (dist > 1.5)
             │                                  │
             ▼                                  ▼
      Dual-Model Evaluation             Emergency Physics /
   (QI-C1 + MODEL-REAL-04 Cross-Check)    Hard Rejection
             │
             ▼
   Uncertainty / Disparity Gate
             │
   ┌─────────┴─────────┐
   ▼                   ▼
Disparity ≤ 500 kg/h  Disparity > 500 kg/h OR Near-Boundary
   │                   │
   ▼                   ▼
Serve QI-C1         Fallback to MODEL-REAL-04
(Confidence: HIGH)  (Confidence: MEDIUM)
```

---

## 5. Explicit Known Limitations
- **Fleet Scope**: Validated exclusively on 3 vessels (Poseidon, Triton, Ceto). Untested on bulk carriers, container ultra-large vessels, or inland barges.
- **Alternative Fuel Simulations**: All green-fuel figures (bio-methanol, green ammonia, liquid hydrogen) are physics-based scenario estimates based on invariant shaft work ($E = P_B \cdot t$). They are **NOT** validated against physical green-fuel telemetry.
- **MPS Formulation**: Matrix Product States (MPS) tensor network regression failed to converge under gradient training and is preserved as a negative result.
- **No Closed-Loop Autonomy**: The system is an advisory decision-support prototype. It is **NOT certified for autonomous vessel navigation or direct engine actuator control**.
