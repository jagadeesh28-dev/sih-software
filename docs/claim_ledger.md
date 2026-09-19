# Egreen Quanta: Official Scientific Claim Ledger
**System Classification**: Controlled Maritime Decision-Support Prototype (SIH 2026)  
**Release Gate**: 1.0.0-verified | **Audit Date**: September 2026  

---

## 1. Governance & Protocol
Every claim made in the Egreen Quanta project documentation, technical presentations, demo interfaces, and research reports must be cataloged below with its traceable proof, experiment source, and verification status.

Allowed Statuses:
- **VERIFIED**: Proven by exact deterministic code reproduction on validated telemetry.
- **VERIFIED WITH QUALIFICATION**: Statistically supported under explicitly stated boundary conditions.
- **UNVERIFIED**: Insufficient empirical data or pending independent testing.
- **REJECTED**: Refuted by experimental evidence or prohibited by scientific integrity rules.

---

## 2. Comprehensive Claim Ledger

| ID | Claim Statement | Claimed Value | Source / Artifact | Dataset / Code Version | Status | Scientific Qualification & Audit Notes |
|:---|:----------------|:--------------|:------------------|:-----------------------|:-------|:---------------------------------------|
| **CLM-01** | Telemetry dataset record count | 173,974 validated records | `data/processed/real/fuelcast/*.parquet` | FuelCast v1.0 | **VERIFIED** | Reconciled from 173,986 raw records after removing 12 trailing logger-shutdown rows with null timestamps. |
| **CLM-02** | Three-vessel fleet distribution | Poseidon: 105,422; Triton: 25,347; Ceto: 43,205 | `results/audit/detailed_uncertainty_metrics.json` | Commit `20309b2` | **VERIFIED** | Exactly matches verified telemetry files across all three vessel classes. |
| **CLM-03** | Frozen baseline MODEL-REAL-04 performance | Seed 42 MAE: 246.91 kg/h; R²: 0.9503 (30-seed mean: 248.12 ± 0.81 kg/h) | `models/model_real_04_meta.json` | Seed 42, 60/20/20 forward temporal split | **VERIFIED** | 14-feature hybrid physics + LightGBM baseline model evaluated on 34,796 test records. |
| **CLM-04** | Reconciled QI-C1 performance | Seed 42 MAE: 244.86 kg/h; R²: 0.9500 (30-seed mean: 237.96 ± 5.46 kg/h) | `models/qi_c1_meta.json` | 6 QIEA features, LightGBM | **VERIFIED** | Seed 42 uses exact QIEA-selected subset (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `fuel_type`). |
| **CLM-05** | QI-C1 universally outperforms classical ML | QI superiority across all metrics | Phase 6 Benchmark / Phase 7 Audit | Master Benchmark | **REJECTED** | Statistical test (p=0.684) confirms parity with classical GA (MAE 237.24 kg/h). No universal superiority. |
| **CLM-06** | QI-C1 is statistically competitive with classical GA | Parity with GA (p=0.684); +44.7% diversity | `reports/final_validation_report.md` | 30 seeds matched | **VERIFIED WITH QUALIFICATION** | QIEA preserves significantly higher population entropy (H=0.2814 vs 0.1945) while achieving matched predictive accuracy. |
| **CLM-07** | Matrix Product States (MPS) viable predictor | MPS tensor network fuel model | `experiments/exp_phase6_mps_failure.py` | PyTorch Tensor Network | **REJECTED** | The tested MPS formulation failed under the evaluated training configuration. Preserved as negative result. |
| **CLM-08** | Quantum computing / quantum advantage | Quantum hardware execution | Codebase audit | Classical CPU/GPU | **REJECTED** | All algorithms are quantum-inspired heuristics running on classical computing hardware. Zero quantum hardware used. |
| **CLM-09** | Conformal uncertainty coverage | 90% nominal: QI-C1 = 93.56%, M04 = 95.05% | `results/audit/detailed_uncertainty_metrics.json` | 34,796 test records | **VERIFIED** | Both models safely exceed the 90.0% nominal coverage floor on forward temporal test data. |
| **CLM-10** | Conformal interval sharpness | QI-C1 MPIW: 1564.93 kg/h (31.17% sharper than M04: 2273.70 kg/h) | `models/conformal_quantiles.json` | Test split | **VERIFIED** | QI-C1 achieves 31.17% narrower prediction intervals while preserving >93.5% empirical test coverage. |
| **CLM-11** | Out-of-Distribution (OOD) specificity | In-domain false positive rate: 0.0% | `results/audit/detailed_ood_metrics.json` | 2,000 test samples | **VERIFIED** | 2,000 real in-domain test records evaluated with zero false alarms at primary threshold distance 1.50. |
| **CLM-12** | Out-of-Distribution severe detection recall | Severe OOD recall: 96.55% (1.50 threshold) / 100.0% (1.00 threshold) | `results/audit/detailed_ood_metrics.json` | 666 severe synthetic OOD samples | **VERIFIED WITH QUALIFICATION** | Severe storm and speed extrapolation detected reliably. Mild extrapolations receive conformal interval inflation. |
| **CLM-13** | Automated safety stress testing | 100.0% safe rejection on 1,000 invalid inputs | `results/audit/safety_test_matrix.json` | 1,000 stress cases + 16 edge cases | **VERIFIED** | All malformed, NaN, negative, and out-of-bounds inputs safely rejected or routed to fallback. |
| **CLM-14** | Autonomous vessel control | System directly commands ship autopilot/throttle | Architecture audit | All configs | **REJECTED** | System is exclusively a human-in-the-loop decision-support prototype. Autonomous control is explicitly forbidden. |
| **CLM-15** | Alternative fuel telemetry | Real sensor measurements for green fuels | Data audit | Telemetry files | **REJECTED** | Telemetry consists entirely of conventional marine diesel/fuel oil. Alternative fuels are thermodynamic scenario simulations. |
| **CLM-16** | Alternative fuel thermodynamic scenarios | Invariant shaft work: E = P_B * t, m_f = E / (LHV * eta) | `results/audit/demo_numbers.json` | Thermodynamic model | **VERIFIED** | Fuel mass flow and emissions calculated on identical shaft work basis across VLSFO, MGO, Methanol, Ammonia, and H2. |
| **CLM-17** | Global slow steaming savings | Ships save 24.8% fuel globally | Scenario test | 18 kn vs 15 kn cruise | **REJECTED AS GENERAL CLAIM** | Must be qualified: "24.8% simulated fuel reduction specifically for CPS_Poseidon from 18 to 15 knots under calm conditions." |
| **CLM-18** | Exact zero-gap physical fleet optimum | Pure physical grid minimum reached | `results/audit/phase5_optimizer_audit.json` | 825,000 evaluations | **REJECTED** | Penalized optimum J*_pen = 873.23 includes schedule penalty (869.44). Pure physical grid minimum is 3.24. Non-zero gap. |
| **CLM-19** | Classical DE optimization superiority | Differential Evolution strongest scalar baseline | Phase 5 Benchmark | 30 seeds, 5 algorithms | **VERIFIED** | Classical DE outperforms QPSO on scalar penalized fuel minimization; QPSO competitive on Pareto coverage. |
| **CLM-20** | Clean one-command reproduction | Deterministic end-to-end execution | `reproduce_release.py` | Pinned Python 3.14 environment | **VERIFIED** | Single command executes all 10 release gates in <5 seconds from clean checkout. |

---

## 3. Strict Negative Results Preservation
The following negative and null results are permanently frozen in the project record:
1. **MPS Tensor Networks**: Yielded uncompetitive validation loss and numerical instability under gradient optimization.
2. **Universal QIEA Superiority**: QIEA failed to outperform Classical GA on raw predictive accuracy ($p=0.684$).
3. **Pure Physical Fuel Predictor**: Achieved $\text{MAE} \approx 1885.45\text{ kg/h}$ and $R^2 \approx -0.547$, proving pure physics is insufficient without residual machine learning.
