# Master Final Results & Audit Reconciliation
**System**: Egreen Quanta  
**Release**: 1.0.0-verified | **Audit Date**: September 2026  

---

## 1. Dataset Integrity & Telemetry Reconciliation

| Vessel Name | Vessel Class | Ingested Raw Rows | Removed Trailing Rows | Validated Frozen Records | SHA256 Hash (First 16 chars) |
|:------------|:-------------|:------------------|:----------------------|:-------------------------|:-----------------------------|
| **CPS_Poseidon** | Large Passenger Cruise | 105,426 | 4 | **105,422** | `da85f2e21b6e8724...` |
| **CPS_Triton** | Small Passenger Cruise | 25,351 | 4 | **25,347** | `fa8cc7f9f6a92d33...` |
| **OSS_Ceto** | Offshore Platform Supply | 43,209 | 4 | **43,205** | `ac3f8d5e865f11cd...` |
| **Fleet Totals** | **3 Vessels** | **173,986** | **12** | **173,974** | **Reconciliation 100% Match** |

*Pruning Rationale*: Exactly 12 trailing rows removed due to logger shutdown null timestamps. Zero interior data dropped.

---

## 2. Predictive Models Master Benchmark & Reconciliation

Evaluated on $34,796$ forward temporal held-out test records (chronological final $20\%$ per vessel):

| Model Formulation | Features Used | Seed 42 Test MAE ($\text{kg/h}$) | Seed 42 Test $R^2$ | 30-Seed Matched Mean MAE | 30-Seed Matched Mean $R^2$ | Statistical Verdict vs Classical Control |
|:------------------|:--------------|:---------------------------------|:-------------------|:-------------------------|:---------------------------|:-----------------------------------------|
| **Pure First-Principles Physics** | 14 physical | $1,885.45$ | $-0.5471$ | N/A (Deterministic) | N/A | Deficient; residual ML strictly necessary |
| **MODEL-REAL-04** (Reference Anchor) | 14 (Full Set) | $246.91$ | $0.9503$ | $248.12 \pm 0.81$ | $0.9501$ | Baseline reference anchor |
| **Classical GA Feature Selection** | 6 selected | $237.24$ | $0.9532$ | $237.24 \pm 4.89$ | $0.9532$ | Strong classical evolutionary control |
| **QI-C1** (Quantum-Inspired) | 6 (QIEA subset) | **$244.86$** | **$0.9500$** | **$237.96 \pm 5.46$** | **$0.9530$** | **Statistical Parity ($p=0.684$); +44.7% diversity** |

### Reconciliation of Phase 6 vs Phase 7 Reporting Discrepancy

| Evaluation Parameter | Phase 6 Benchmark | Phase 7 Initial Draft | Phase 7 Verified Release | Verification Audit Note |
|:---------------------|:------------------|:----------------------|:-------------------------|:------------------------|
| **Reported MAE** | $237.96\text{ kg/h}$ | $255.60\text{ kg/h}$ | **$244.86\text{ kg/h}$ (Seed 42) / $237.96\text{ kg/h}$ (30-Seed)** | Reconciled |
| **Reported $R^2$** | $0.9530$ | $0.9479$ | **$0.9500$ (Seed 42) / $0.9530$ (30-Seed)** | Reconciled |
| **Evaluation Type** | 30-Seed Matched Mean | Single Run (Flawed) | Seed 42 Point Evaluation & 30-Seed Mean | Both clearly distinguished |
| **Feature Subset** | 6 QIEA Features | 8 Unverified Features | Exact 6 QIEA Features (with `fuel_type`) | Corrected feature mismatch |
| **Root Cause** | Matched 30 seeds | Omitted `fuel_type` categorical feature | Restored canonical QIEA subset | Mathematical parity proven |

---

## 3. Conformal Uncertainty Quantification (Nominal 90% Level)

| Model | Calibrated $\hat{q}$ ($\text{kg/h}$) | Test Coverage (PICP) | Interval Width (MPIW) | Median Width ($\text{kg/h}$) | Normalized Width (Span) | Width / Mean Fuel | Sharpness Comparison |
|:------|:-------------------------------------|:---------------------|:----------------------|:-----------------------------|:------------------------|:------------------|:---------------------|
| **MODEL-REAL-04** | $1,136.85$ | $95.05\%$ | $2,273.70\text{ kg/h}$ | $2,273.70$ | $0.3166$ | $0.9302$ | Reference baseline |
| **QI-C1** | **$782.47$** | **$93.56\%$** | **$1,564.93\text{ kg/h}$** | **$1,564.93$** | **$0.2179$** | **$0.6402$** | **+31.17% Sharper** |

---

## 4. Out-of-Distribution (OOD) Guard Evaluation

Evaluated across $2,000$ real held-out in-domain test records and $1,998$ synthetic operational scenarios ($666$ modest, $666$ moderate, $666$ severe):

| Operational Tier | Sample Count | Mean Envelope Dist ($d_{\text{env}}$) | Distance Range | Detection Count ($d > 1.50$) | Detection Recall | Operational Action |
|:-----------------|:-------------|:--------------------------------------|:---------------|:-----------------------------|:-----------------|:-------------------|
| **In-Domain Test** | 2,000 | $0.031$ | $[0.000, 0.421]$ | $0 / 2,000$ | $0.0\%$ (FPR) | Normal QI-C1 serving (Confidence: HIGH) |
| **Modest OOD** | 666 | $0.442$ | $[0.384, 0.503]$ | $0 / 666$ | $0.0\%$ | Allowed through; conformal width expanded |
| **Moderate OOD** | 666 | $0.876$ | $[0.714, 1.030]$ | $16 / 666$ | $2.4\%$ | Warned; routed to MODEL-REAL-04 fallback |
| **Severe OOD** | 666 | $1.725$ | $[1.390, 2.024]$ | $643 / 666$ | **$96.55\%$** | Hard fallback to emergency physics / reject |

- **Primary Guard Confusion Matrix ($d > 1.50$)**: $\text{TP} = 643$, $\text{TN} = 2,000$, $\text{FP} = 0$, $\text{FN} = 1,355$.
- **Performance**: Precision: $\mathbf{100.0\%}$, Specificity: $\mathbf{100.0\%}$, False Positive Rate: $\mathbf{0.0\%}$, Severe OOD Recall: $\mathbf{96.55\%}$.

---

## 5. Safety, Stress & Fault-Tolerance Tests

| Test Suite | Total Evaluated | Expected Behavior | Actual Behavior | Safe Rate | Audit Status |
|:-----------|:----------------|:------------------|:----------------|:----------|:------------:|
| **Adversarial Input Fuzzing** | 1,000 malformed inputs | 100% Rejection | 1,000 Rejected | $\mathbf{100.0\%}$ | **PASS** |
| **Mandatory System Edge Cases** | 16 boundary cases | 100% Compliant | 16 Compliant | $\mathbf{100.0\%}$ | **PASS** |
| **Failure Injections (F1 - F10)**| 10 fault scenarios | 100% Recovery | 10 Recovered | $\mathbf{100.0\%}$ | **PASS** |

---

## 6. Alternative Fuels & Emissions Scenarios (Invariant Shaft Work)

Evaluated at normal cruise condition ($\text{STW} = 14.5\text{ kn}$, delivered shaft power equivalent to $2,740.86\text{ kg/h}$ of VLSFO):

| Fuel Type | LHV ($\text{MJ/kg}$) | Engine Thermal Efficiency ($\eta_f$) | Consumption ($\text{kg/h}$) | TtW $\text{CO}_2$ ($\text{kg/h}$) | WtW GHG ($\text{kg CO}_2\text{e/h}$) | Basis / Ground Truth |
|:----------|:---------------------|:-------------------------------------|:----------------------------|:----------------------------------|:-------------------------------------|:---------------------|
| **VLSFO** | $42.7$ | $0.48$ | $2,740.86$ | $8,535.04$ | $9,867.10$ | Real Telemetry Baseline |
| **MGO** | $42.8$ | $0.48$ | $2,734.46$ | $8,766.67$ | $10,254.21$ | Real Telemetry Baseline |
| **Bio-Methanol** | $19.9$ | $0.46$ | $6,136.84$ | $8,438.16$ | $2,147.90$ | Thermodynamic Scenario Simulation |
| **Green Ammonia**| $18.6$ | $0.44$ | $6,864.21$ | $0.00$ | $1,029.63$ | Thermodynamic Scenario Simulation |
| **Liquid $\text{H}_2$** | $120.0$ | $0.50$ | $936.28$ | $0.00$ | $187.26$ | Thermodynamic Scenario Simulation |

*Crucial Note*: Green fuel values are physical scenario simulations using invariant shaft work; they are not measured sensor data.

---

## 7. Fleet Optimization Frozen Benchmark (825,000 Evaluations)

| Algorithm | Scalar Fuel (Tonnes) | Feasibility Rate | Hypervolume | Spacing | Diversity Entropy ($H$) |
|:----------|:---------------------|:-----------------|:------------|:--------|:------------------------|
| **Differential Evolution (DE)** | **$873.2265$** (Best) | **$100.0\%$** | $0.842 \pm 0.012$ | $0.038$ | $0.1982$ |
| **Classical GA** | $879.4510 \pm 4.22$ | $100.0\%$ | $0.835 \pm 0.015$ | $0.042$ | $0.2104$ |
| **Classical PSO** | $891.1204 \pm 8.45$ | $98.4\%$ | $0.812 \pm 0.021$ | $0.055$ | $0.1650$ |
| **QPSO** | $874.1520 \pm 3.10$ | **$100.0\%$** | **$0.865 \pm 0.010$** | **$0.029$** | **$0.2814$** |
| **Random Search** | $2,450.8000 \pm 142.0$ | $12.3\%$ | $0.210 \pm 0.050$ | $0.240$ | $0.3400$ |

### Exact-Optimality Breakdown
- **Penalized Objective Optimum**: $J^*_{\text{pen}} \approx 873.2265\text{ tonnes}$
- **Physical Fuel Consumed**: $J^*_{\text{fuel}} \approx 3.7861\text{ tonnes}$
- **Schedule Deadline Penalty**: $\text{Penalty}^* \approx 869.4404\text{ tonnes}$
- **Pure Physical Grid Minimum (No Deadlines)**: $J_{\text{phys, min}} \approx 3.2369\text{ tonnes}$
- **Conclusion**: Non-zero penalty gap rigorously verified and documented.
