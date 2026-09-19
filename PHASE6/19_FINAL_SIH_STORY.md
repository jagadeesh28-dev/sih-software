# PHASE 6 — STEP 19: FINAL SIH 2026 TECHNICAL STORY
## SIH26138 — Egreen Quanta
### Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization

**Presented by:** Egreen Quanta Research & Engineering Team  
**Problem Statement:** SIH26138 — Green Fleet Decarbonization and Voyage Optimization  
**Core Posture:** Rigorous Scientific Honesty, Empirical Grounding, Zero Quantum Hype  

---

## 1. The Real Maritime Decarbonization Crisis
Commercial shipping accounts for nearly $3\%$ of global greenhouse gas emissions and is facing unprecedented regulatory stringency under the **EU Emissions Trading System (EU ETS)** and **FuelEU Maritime Regulation (EU 2023/1805)**. Shipowners face millions of dollars in non-compliance penalties unless fleet fuel consumption and greenhouse gas intensity are curtailed. 
However, ship dispatch decisions are frequently made using static charter table assumptions that ignore dynamic hydrodynamics, weather drift, and real-time engine degradation.

---

## 2. Real Multi-Vessel Sensor Telemetry
Unlike academic projects relying on synthetic toy curves, Egreen Quanta is validated on **173,974 real-world operational records** from the DTU FuelCast research dataset across three commercial vessels (*CPS_Poseidon*, *CPS_Triton*, and *OSS_Ceto*) over 366 days.
- Ground truth is logged directly from **high-frequency Coriolis mass-flow meters** ($kg/h$).
- Speeds are measured using dual Doppler acoustic logs for **Speed Through Water (STW)** and differential GPS for **Speed Over Ground (SOG)**.
- Telemetry is integrated with ECMWF and Copernicus ocean metocean hindcasts.

---

## 3. Naval Architecture Physics Foundation
Pure black-box machine learning models fail on ships because they can predict non-physical phenomena (e.g., negative fuel consumption or decreasing resistance at 25 knots). 
Egreen Quanta anchors all prediction to a **first-principles naval architecture backbone**:
- Calm-water resistance ($R_{calm}$) via the **Holtrop-Mennen (1982/1984)** equations.
- Wave-added resistance ($R_{wave}$) via **IMO STAwave-2 / Kwon** semi-empirical dynamics.
- Wind aerodynamic drag ($R_{wind}$) via **Blendermann** relative vector models.
- Mechanical power chain: $P_E \to P_D \to P_B \to \dot{m}_{fuel}$.
- Driven strictly by **Speed Through Water (STW)**; silent substitution of GPS SOG is strictly prohibited.

---

## 4. The Frozen Classical Baseline (`MODEL-REAL-04`)
Because pure theoretical physics cannot foresee vessel biofouling, propeller surface roughness, and auxiliary hotel loads, it displays a structural under-prediction bias ($-1,883\text{ kg/h}$). 
To solve this, Egreen Quanta pioneered a **Hybrid Residual Architecture**:
$$\hat{F}(x) = \max(0, F_{physics}(x) + 1.0 \times \hat{r}_{ML}(x))$$
where a LightGBM regressor learns the residual delta $r = y - F_{physics}$ strictly on hydrodynamic and weather features (`CONFIG_REAL_A`). 
This baseline was independently reproduced and frozen at:
- **$R^2 = 0.9501$**
- **$\text{MAE} = 246.97\text{ kg/h}$**
- **$\text{MAPE} = 14.63\%$**
- **Inference Latency: $0.02\text{ ms}$**

---

## 5. The Quantum-Inspired Prediction Mechanisms
We investigated two distinct levels of quantum-inspired algorithms:
1. **Level 1 (Optimization Mechanism):** Quantum-Inspired Evolutionary Algorithm (**QIEA**) using Q-bit probability amplitudes $[\alpha_i, \beta_i]^T$ and rotation gates for feature subset selection, combined with Quantum-Behaved Particle Swarm Optimization (**QPSO**) using Schrödinger delta-potential well bound states for hyperparameter tuning.
2. **Level 2 (Model Representation):** Direct Matrix Product State (**MPS**) tensor-network regression contracting 3-way core tensors across a bounded trigonometric feature map $\phi(x) = [\cos(\pi x/2), \sin(\pi x/2)]^T$.

---

## 6. The Fair 30-Seed Matched Benchmark
To ensure scientific integrity:
- Every model was tested across the **exact same 30 random seeds** (42, 1001–1029).
- Evaluated on identical forward-chronological test splits (34,796 records).
- Given identical computational evaluation budgets (150 fitness evaluations for QIEA vs Classical GA; 150 evaluations for QPSO vs Classical PSO).
- Analyzed via two-sided paired Wilcoxon signed-rank tests with Holm-Bonferroni corrections.

---

## 7. The Scientific Findings: What the Data Proved
- **Level 1 (QIEA/QPSO) is COMPETITIVE (Case B):** QIEA-FS achieved $\text{MAE} = 237.96\text{ kg/h}$ ($R^2 = 0.9530$), outperforming the baseline by $-10.28\text{ kg/h}$ ($p < 10^{-4}$). When tested against budget-matched Classical GA ($237.24\text{ kg/h}$), it was statistically comparable ($p = 0.684$).
- **Crucial Secondary Advantage:** Q-bit probability amplitudes maintained **$+44.7\%$ higher population diversity** ($H(Q) = 0.2814$ vs $0.1945$), preventing premature convergence.
- **Level 2 (MPS Tensor Network) FAILS (Case D):** Unconstrained SGD tensor train contraction diverged across 20 of 30 seeds ($\text{MAE} > 10^{11}\text{ kg/h}$), conclusively proving that naive MPS is unsuited for tabular telemetry.
- **Scientific Honesty:** We present this negative result openly to the jury.

---

## 8. Uncertainty Quantification & Domain Safety
- **Conformal Prediction Intervals:** Calibrated strictly on validation data, yielding an empirical $91.10\%$ coverage for nominal $90\%$ intervals. QIEA produced **$3.25\%$ sharper intervals** ($598.40\text{ kg/h}$ vs $618.50\text{ kg/h}$).
- **Mahalanobis Domain Guardian:** Inputs deviating beyond the 95th percentile training envelope trigger an out-of-domain flag, widening uncertainty intervals by $2.5\times$ to prevent silent extrapolation.

---

## 9. Alternative-Fuel Thermodynamic Scenario Layer
Real telemetry is conventional fuel. To model the green transition safely, the platform applies **invariant shaft energy conservation**:
$$E_{shaft} = \int P_B(t) \, dt \implies \dot{m}_f = \frac{P_B}{\text{LHV}_f \times \eta_f(L)}$$
Evaluating LNG, green methanol, green ammonia, and liquid hydrogen strictly as **physics-based scenarios** using IMO Fourth GHG Study parameters.

---

## 10. Downstream Phase 5 Fleet Optimization Integration
The resulting predictor directly feeds the frozen Phase 5 fleet optimizer (`CommonFleetEvaluator` + DE/A5):
- Evaluates routes across multi-scenario weather (Calm, Moderate, Storm).
- Guarantees **100% feasibility** via Deb's feasibility-first constraint handling.
- Downstream integration testing confirmed that substituting the classical baseline with the QI predictor maintained 100% feasibility, complete Pareto frontier stability, and sub-2-second execution.

---

## 11. Regulatory Compliance Accounting
An independent accounting layer evaluates:
- **FuelEU Maritime:** Penalties calculated from lifecycle Well-to-Wake (WtW) greenhouse gas intensity ($g\text{CO}_2e/\text{MJ}$).
- **EU ETS Maritime:** Compliance allowances priced at $\$90/\text{tCO}_2$ applied to operational Tank-to-Wake (TtW) emissions.
- **IMO CII Ratings:** Dynamic Carbon Intensity Indicator scoring from Band A to Band E.

---

## 12. Human-in-the-Loop Decision Support
The final platform does not make autonomous unreviewable dispatch decisions. It exposes an interactive operational dashboard providing:
- Side-by-side Pareto trade-offs (OPEX vs Fuel vs Delay vs Emissions).
- Visual conformal uncertainty envelopes with OOD risk alerts.
- Bunkering switch recommendations based on port fuel availability.

---

## 13. Limitations & Disclaimers
- **Zero-Shot Cross-Vessel Generalization Fails:** LOVO testing revealed that models cannot be transferred between different vessel classes without fine-tuning ($3.4\times\text{--}5.2\times$ error increase).
- **Not Quantum Computing:** Runs entirely on classical hardware; zero quantum hardware speedup is claimed.
- **Alternative Fuels are Scenarios:** Not experimentally validated by flow meters.

---

## 14. Evidence-Backed Novelty
Egreen Quanta is the **first unified maritime platform** that:
1. Combines QIEA quantum-inspired diversity preservation with naval architecture hybrid residuals.
2. Undergoes an exhaustive 30-seed adversarial audit on real multi-vessel telemetry.
3. Transparently demonstrates both where quantum-inspired optimization succeeds (diversity retention) and where direct quantum representations fail (MPS divergence).
4. Delivers an industrial-grade, 100% constraint-safe fleet optimization stack.
