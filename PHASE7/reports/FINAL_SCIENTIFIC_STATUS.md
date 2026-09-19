# PHASE 7: FINAL SCIENTIFIC STATUS REPORT
## SIH26138 — Egreen Quanta
### Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization

**Release Tag:** `v1.0.0`  
**Date:** September 19, 2026  
**Auditor:** Principal ML Engineer, Maritime Optimization Lead, Scientific Validation Lead  
**Scientific Status:** **FROZEN & FULLY VALIDATED**

---

## 1. Architectural Overview & Scientific Hierarchy

Egreen Quanta resolves the dual challenges of accurate maritime vessel fuel prediction and green fleet operational dispatch through a unified, physics-guided, quantum-inspired architecture:

```
                  [ REAL HIGH-FREQUENCY SENSOR TELEMETRY ]
                           (173,974 Active Records)
                                      │
                                      ▼
                      [ DOMAIN GUARDIAN & OOD CHECKER ]
                                      │
                                      ▼
                      [ NAVAL ARCHITECTURE RESISTANCE ]
                      (Holtrop-Mennen + STAwave-2 + Wind)
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
                 ▼                                         ▼
         [ MODEL-REAL-04 ]                              [ QI-C1 ]
      Classical ML Residual                    QIEA Feature Selection (8 Feat)
      Reference / Fallback                     + LightGBM Residual (Primary)
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      ▼
                     [ CONFORMAL PREDICTIVE UNCERTAINTY ]
                                      │
                                      ▼
                    [ INVARIANT SHAFT MECHANICAL ENERGY ]
                                      │
                                      ▼
                  [ ALTERNATIVE FUEL THERMODYNAMIC SCENARIOS ]
                   (Bio-Methanol, Ammonia, Liquid Hydrogen)
                                      │
                                      ▼
                   [ REGULATORY LAYER (FuelEU / EU ETS / CII) ]
                                      │
                                      ▼
                  [ PHASE 5 MULTI-OBJECTIVE FLEET OPTIMIZER ]
                  (Hybrid A5: Deb Feasibility + Hungarian Repair)
                                      │
                                      ▼
                      [ HUMAN-IN-THE-LOOP FLEET DSS ]
```

---

## 2. Core Scientific Findings (Frozen & Verified)

### 2.1 Level 1 Fuel Prediction (QI-C1 vs. Baselines)
- **Baseline Physics (`P0`):** $R^2 = 0.5412$, $\text{MAE} = 812.4\text{ kg/h}$. Demonstrates that pure theoretical hydrodynamics alone cannot capture unmodeled operational hull fouling and engine degradation.
- **Baseline Hybrid (`MODEL-REAL-04`):** $R^2 = 0.9501$, $\text{MAE} = 246.97\text{ kg/h}$ (Seed 42; 30-seed mean: $248.12\text{ kg/h}$), $\text{MAPE} = 14.63\%$. Combines physics with LightGBM residual learning across all 14 features.
- **Candidate QI-C1 (QIEA-FS + LightGBM):** $R^2 = 0.9530 \pm 0.0012$, $\text{MAE} = 237.96 \pm 5.46\text{ kg/h}$. Selects an optimal 8-feature subset (`stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `wind_speed_ms`, `wave_height_m`, `current_speed_ms`, `water_depth_m`).
- **Matched Classical GA Control (`P3`):** $R^2 = 0.9532$, $\text{MAE} = 237.24 \pm 5.12\text{ kg/h}$.
- **Statistical Parity:** Wilcoxon signed-rank test yields $p = 0.684$ (Hodges-Lehmann difference $+0.65\text{ kg/h}$). **Conclusion:** QI-C1 is statistically indistinguishable in error from Classical GA.
- **Search Diversity Advantage:** Q-bit probability amplitudes maintain $+44.7\%$ higher population Shannon entropy ($0.2814$ vs $0.1945$) across identical budgets.

### 2.2 Level 2 MPS Tensor Network (Negative Result)
- Evaluated continuous Matrix Product State (MPS) tensor trains with bond dimensions $\chi \in [4, 32]$.
- Resulted in gradient divergence and numerical instability across 20/30 random seeds ($\text{MAE} > 10^{11}\text{ kg/h}$).
- **Scientific Conclusion:** Continuous tabular maritime telemetry lacks the 1D physical entanglement locality required for stable MPS representations. Formally retained as an audited negative finding.

### 2.3 Cross-Vessel Generalization (LOVO Boundary)
- Leave-One-Vessel-Out evaluation resulted in a $3.4\times\text{ to }5.2\times$ increase in test MAE on unseen hulls.
- **Scientific Conclusion:** Zero-shot cross-vessel generalization is invalid. Each vessel hull requires calibrated training telemetry.

### 2.4 Phase 5 Green Fleet Optimization
- Solves heterogeneous vessel routing, speed scheduling, bunker allocation, and shore power dispatch under weather uncertainty.
- Cures continuous QPSO penalty-inversion failure by enforcing **Deb's feasibility-first constraint handling** and **Hungarian algorithm route repair**, achieving **100% feasibility**.
- Complete hybrid algorithm A5 expands Pareto Hypervolume by $+64.0\%$ ($247.11\text{M}$ vs $150.67\text{M}$) over standard NSGA-III, executing $2.67\times$ faster at high dimensional scale ($D=600$).

---

## 3. Production Readiness Status

1. **Deterministic Reproducibility:** Single-command execution (`python reproduce_release.py`) reproduces all baseline metrics and passes all 9 verification gates in $<15\text{ seconds}$.
2. **Defensive Robustness:** 100% safe rejection of malformed, NaN, Inf, and impossible physical inputs across 1,000 automated stress tests.
3. **Traceability:** Every number displayed in the UI, report, or presentation traces directly to a frozen artifact in `PHASE6/results/` or `PHASE7/results/`.

**Scientific Readiness:** **APPROVED AND RELEASE-LOCKED.**
