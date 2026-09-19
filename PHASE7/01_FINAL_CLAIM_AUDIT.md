# PHASE 7 — STEP 1: FORENSIC CLAIM RECONCILIATION & AUDIT
## SIH26138 — Egreen Quanta
### Complete Claim-to-Artifact Traceability Ledger for the SIH 2026 Evaluation Jury

**Date:** September 19, 2026  
**Auditor:** Hostile SIH Jury Reviewer, Reproducibility Auditor, Technical Architect  
**Policy:** Every numerical value and technical claim presented in the demo, report, or pitch must be backed by a concrete file artifact.  

---

## 1. Master Claim Traceability Matrix

| Index | Technical / Scientific Claim | Empirical Evidence & Mathematical Value | Underlying Artifact Source | Fully Reproducible? | Allowed Precise Scientific Wording |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **C01** | **Raw Dataset Scale** | 173,986 total records downloaded from DTU FuelCast across 3 physical hulls. | `01_REAL_DATA_RAW_AUDIT.md`, `PHASE7/results/data_count_reconciliation.csv` | **YES** | *"173,986 raw high-frequency sensor records from 3 commercial vessels."* |
| **C02** | **Validated Telemetry Sample** | 173,974 clean operational observations after dropping 12 null padding tail rows. | `data/processed/real/fuelcast/*.parquet`, `PHASE6/01_BASELINE_REPRODUCTION.md` | **YES** | *"173,974 validated active telemetry observations across 604 vessel-days."* |
| **C03** | **Classical Baseline $R^2$** | $R^2 = 0.9501$ on out-of-sample forward-temporal test split (34,796 records). | `08_REAL_MODEL_RESULTS.csv`, `PHASE6/results/baseline_reproduction.csv` | **YES** | *"Baseline physics + ML residual achieves R² = 0.9501 on out-of-sample test telemetry."* |
| **C04** | **Classical Baseline MAE** | $\text{MAE} = 246.97\text{ kg/h}$ (Seed 42); $248.12 \pm 0.81\text{ kg/h}$ across 30 seeds. | `PHASE6/results/baseline_reproduction.csv`, `PHASE6/results/baseline_results.csv` | **YES** | *"Frozen baseline achieves test MAE of 246.97 kg/h (248.12 kg/h 30-seed mean)."* |
| **C05** | **Classical Baseline MAPE** | $\text{MAPE} = 14.63\%$ on test split using direct Coriolis flow ground truth. | `08_REAL_MODEL_RESULTS.csv`, `PHASE6/results/baseline_reproduction.csv` | **YES** | *"Baseline MAPE is 14.63% relative to direct Coriolis mass-flow measurements."* |
| **C06** | **Candidate QI-C1 Test MAE** | $\text{MAE} = 237.96 \pm 5.46\text{ kg/h}$ across 30 matched random seeds. | `PHASE6/results/qi_c1_results.csv`, `PHASE6/results/statistical_comparison.csv` | **YES** | *"QI-C1 feature selection achieves test MAE of 237.96 kg/h across 30 matched seeds."* |
| **C07** | **Candidate QI-C1 Test $R^2$** | $R^2 = 0.9530 \pm 0.0012$ across 30 matched seeds. | `PHASE6/results/qi_c1_results.csv` | **YES** | *"QI-C1 delivers test R² = 0.9530 across 30 matched seeds."* |
| **C08** | **QI-C1 vs Classical GA Parity**| Difference vs Classical GA (237.24 kg/h) is $+0.72\text{ kg/h}$ ($p = 0.684$, Hodges-Lehmann $+0.65\text{ kg/h}$). | `PHASE6/results/ablation_results.csv`, `PHASE6/09_STATISTICAL_PROTOCOL.md` | **YES** | *"QI-C1 is statistically comparable to budget-matched Classical GA (p = 0.684)."* |
| **C09** | **Population Search Diversity** | QIEA preserves population Hamming diversity of $0.2814$ vs $0.1945$ for Classical GA ($+44.7\%$). | `PHASE6/results/feature_stability.csv`, `PHASE6/results/figures/fig10_qi_population_entropy.png` | **YES** | *"Q-bit probability amplitudes maintain +44.7% higher exploratory search diversity."* |
| **C10** | **Conformal Interval Coverage** | Empirical coverage probability (PICP) = $91.10\%$ for nominal $90.0\%$ confidence interval. | `PHASE6/results/uncertainty_results.csv`, `PHASE6/11_UNCERTAINTY_ANALYSIS.md` | **YES** | *"Conformal predictive intervals achieve 91.10% empirical coverage for nominal 90% bounds."* |
| **C11** | **Conformal Interval Sharpness** | 90% interval width is $598.40\text{ kg/h}$ for QI-C1 vs $618.50\text{ kg/h}$ for baseline ($-3.25\%$). | `PHASE6/results/uncertainty_results.csv` | **YES** | *"QI-C1 produces 3.25% narrower (sharper) uncertainty bounds while preserving nominal coverage."* |
| **C12** | **Out-of-Distribution Degradation** | Mahalanobis $>95$th percentile states exhibit $+101.0\%$ error increase ($458.12\text{ kg/h}$). | `PHASE6/results/ood_results.csv`, `PHASE6/12_OOD_ANALYSIS.md` | **YES** | *"Severe OOD conditions increase error by 101%; detected and guarded via Mahalanobis filter."* |
| **C13** | **Cross-Vessel Generalization** | LOVO testing shows $3.4\times\text{--}5.2\times$ error increase across unseen vessel hulls. | `PHASE6/results/lovo_results.csv`, `PHASE6/08_VALIDATION_PROTOCOL.md` | **YES** | *"Zero-shot cross-vessel generalization fails; vessel-specific calibration is mandatory."* |
| **C14** | **MPS Tensor Network Result** | Unconstrained SGD tensor train diverged on continuous tabular telemetry across 20/30 seeds. | `PHASE6/results/qi_c2_results.csv`, `PHASE6/10_FAILURE_ANALYSIS.md` | **YES** | *"The tested MPS formulation was not viable for continuous tabular telemetry (negative result)."* |
| **C15** | **Phase 5 Fleet Feasibility** | Hybrid framework cures continuous QPSO penalty-inversion failure (100% vs 80% feasibility). | `PHASE5_STATUS.md`, `PHASE5/PHASE5_FINAL_REPORT.md` | **YES** | *"Deb's feasibility-first constraint handling restored fleet feasibility from 80% to 100%."* |
| **C16** | **Phase 5 Pareto Hypervolume** | Complete hybrid A5 achieves $+64.0\%$ higher Hypervolume over standard NSGA-III ($247.11\text{M}$ vs $150.67\text{M}$). | `PHASE5_STATUS.md`, `results/pareto/` | **YES** | *"A5 achieves +64.0% higher Pareto hypervolume than standard NSGA-III on fleet trade-offs."* |
| **C17** | **High-Dimensional Fleet Scaling**| At $D=600$ (100 vessels), A5 scales sub-quadratically and runs $2.67\times$ faster than DE ($1.69\text{ s}$ vs $4.49\text{ s}$). | `PHASE5_STATUS.md`, `results/scalability/` | **YES** | *"A5 scales sub-quadratically at D=600, executing 2.67x faster than Differential Evolution."* |
| **C18** | **Alternative Fuel Energy Basis** | Alternative fuels modeled via invariant mechanical shaft energy: $E_{shaft} = \int P_B dt$. | `PHASE6/13_ALTERNATIVE_FUEL_SCENARIOS.md`, `configs/fuels.yaml` | **YES** | *"Green fuels evaluated as physics-based thermodynamic scenarios via invariant shaft energy."* |
| **C19** | **Regulatory Emissions Accounting** | Independent calculation of FuelEU WtW intensity, EU ETS operational costs, and IMO CII ratings. | `PHASE6/13_ALTERNATIVE_FUEL_SCENARIOS.md`, `optimization/regulatory.py` | **YES** | *"Regulatory accounting strictly isolates TtW, WtT, and WtW without double counting."* |
| **C20** | **Novelty and Algorithmic Scope** | Algorithmic novelty strictly disclaimed; novelty limited to platform architecture and multi-vessel telemetry audit. | `PHASE6/15_NOVELTY_AUDIT.md`, `PHASE6/reports/PHASE6_CLAIM_LEDGER.yaml` | **YES** | *"Novelty is strictly scoped to system integration, naval architecture residual coupling, and open benchmarking."* |

---

## 2. Forensic Reconciliation Verdict

1. **Zero Unbacked Claims:** Every performance figure ($R^2$, MAE, MAPE, Hypervolume, Feasibility, Runtime, Diversity) maps directly to a generated CSV table and validation report.
2. **Strict Nomenclature Compliance:** No forbidden terms (*"quantum supremacy"*, *"quantum speedup"*, *"quantum hardware"*, *"quantum advantage"*) appear in any approved claim.
3. **Negative Results Preserved:** The failure of MPS tensor networks (C14) and the failure of zero-shot cross-vessel generalization (C13) are prominently documented as core scientific findings.
