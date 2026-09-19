# SIH26138 Egreen Quanta — Phase 6 Architecture Decision
## Quantum-Inspired Fuel Prediction Engine: Two-Tier Architectural Decision & Protocol Freeze

---

### Executive Summary

| Parameter | Decision / Finding |
|---|---|
| **Phase 6 Decision Gate** | **GATE B (QI matches classical prediction with measurable search diversity & feature stability advantage)** |
| **Operational Fuel Predictor** | `y_hat_CLASSICAL = Physics(x) + Residual_ML(x)` (Frozen `MODEL-REAL-04`) |
| **Research / Exploration Predictor** | `y_hat_QI = Physics(x) + Residual_QI(x)` (QI-C1 QIEA-FS / QI-C2 QPSO-HPO) |
| **Direct QI MPS Residual (QI-C3)** | Preserved as theoretical research control; rejected for operational use (inferior capacity to GBDT) |
| **Downstream Fleet Integration** | Validated: Propagates through `CommonFleetEvaluator` into DE optimizer with 0 constraint violations |
| **Quantum Advantage Claim** | **EXPLICITLY REJECTED**: Zero physical quantum hardware, zero quantum speedup claimed |

---

### 1. The Core Scientific Question & Decision Gate

The central mandate of Phase 6 was to answer:
> *"Can a genuinely quantum-inspired mechanism improve maritime fuel/energy prediction relative to a strong physics-plus-classical-ML baseline under identical data, validation, computational-budget, and statistical conditions?"*

Following controlled 30-seed benchmarking on 173,986 real telemetry records across three vessels (*CPS Poseidon*, *CPS Triton*, *OSS Ceto*):
- **Hypothesis H1 (QI Superiority in Raw Accuracy):** **FALSIFIED.** QIEA-FS and QPSO-HPO improve MAE by $-0.15$ to $-1.06$ kg/h over the baseline MAE of $246.97$ kg/h. This difference is statistically insignificant ($p > 0.05$ under Holm-corrected Wilcoxon signed-rank testing) and practically indistinguishable from telemetry sensor noise ($\pm 25$ kg/h).
- **Hypothesis H2 (QI Competitive with Secondary Advantage):** **CONFIRMED.** QIEA-FS maintains comparable predictive accuracy ($R^2 = 0.9501$, $\text{MAPE} = 14.63\%$) while exhibiting significantly superior feature-selection stability across random seeds (mean pairwise Jaccard index $0.78$ vs $0.62$ for Classical GA) and persistent quantum population entropy preventing premature collapse.
- **Hypothesis H3 (QI Inferior in Direct Neural/Tensor Formulation):** **CONFIRMED FOR QI-C3.** The direct Matrix Product State (MPS) tensor-network predictor achieved $\text{MAE} = 392.4$ kg/h, underperforming LightGBM due to the expressivity limits of low-rank tensor decompositions on tabular hydrodynamic telemetry.

**Formal Decision Gate Selected:**
```
===========================================================================
DECISION GATE B:
QI matches classical prediction accuracy but provides measurable secondary
advantages in feature selection stability and search diversity.
Retain Classical Physics + ML as the PRIMARY OPERATIONAL PREDICTOR.
Retain Quantum-Inspired QIEA/QPSO as the RESEARCH & FEATURE SELECTION ENGINE.
===========================================================================
```

---

### 2. Two-Tier Prediction Architecture

To protect commercial reliability while fully addressing SIH26138 requirements, Egreen Quanta implements a strict two-tier architecture:

```
                            RAW TELEMETRY
                                  │
                                  ▼
                        Data Cleaning & Sorting
                                  │
                                  ▼
                         Domain Sanity Filter
                                  │
                                  ▼
                      Physics Engine (Holtrop-Mennen)
                                  │
                                  ▼
                         f_phys(x) Prediction
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
       [OPERATIONAL BRANCH]                [RESEARCH BRANCH]
     MODEL-REAL-04 (LightGBM)            QI-C1 / QI-C2 (QIEA/QPSO)
                 │                                 │
                 ▼                                 ▼
       r_ML(x) Residual                  r_QI(x) Residual
                 │                                 │
                 ▼                                 ▼
      y_hat = f_phys + r_ML             y_hat_QI = f_phys + r_QI
                 │                                 │
                 └────────────────┬────────────────┘
                                  │
                                  ▼
                       Quantile Uncertainty Band
                       (10% - 90% Prediction Interval)
                                  │
                                  ▼
                         CommonFleetEvaluator
                                  │
                                  ▼
                    Downstream Fleet Optimization
                    (MODE / DE + Deb's Feasibility)
```

#### Tier 1: Operational Baseline (`MODEL-REAL-04`)
- **Mathematical Form:**
  $$\hat{y}_{\text{operational}}(x) = f_{\text{phys}}(x) + 1.0 \cdot g_{\text{LGBM}}(x; \mathcal{F}_{\text{full}})$$
- **Feature Set:** Full 14-feature `CONFIG_REAL_A` hydrodynamic/metocean space.
- **Role:** Production fleet routing, regulatory compliance reporting (CII, EU ETS, FuelEU), voyage fuel estimation.
- **Justification:** Highest historical stability ($R^2 = 0.9501$, $\text{MAE} = 246.97$ kg/h), sub-millisecond inference latency ($0.02$ ms/call), 0 physical bound violations.

#### Tier 2: Research & Feature Exploration Engine (`QI-C1 / QI-C2`)
- **Mathematical Form:**
  $$\hat{y}_{\text{QI}}(x) = f_{\text{phys}}(x) + \alpha_{\text{QPSO}} \cdot g_{\text{LGBM}}(x; \mathcal{F}_{\text{QIEA}})$$
- **Feature Set:** Sparse 8-feature core selected via QIEA Q-bit amplitude measurement:
  $$\mathcal{F}_{\text{QIEA}} = \{\text{stw\_kn}, \text{sog\_kn}, \text{draft\_m}, \text{displacement\_t}, \text{wind\_speed\_ms}, \text{wave\_height\_m}, \text{current\_speed\_ms}, \text{water\_depth\_m}\}$$
- **Role:** Automated sensor failure robustness, edge-device sparse telemetry inference, hyperparameter sensitivity exploration.
- **Justification:** Eliminates noisy metocean angle features, reduces input dimensionality by 43% with zero loss in predictive fidelity ($\Delta \text{MAE} = -0.15$ kg/h).

---

### 3. Mathematical Formulation of Quantum-Inspired Components

#### 3.1 QIEA Q-bit Representation and Rotation Gate
Each feature candidate $i \in \{1, \dots, d\}$ is represented by a Q-bit probability amplitude vector:
$$q_i = \begin{bmatrix} \alpha_i \\ \beta_i \end{bmatrix}, \quad |\alpha_i|^2 + |\beta_i|^2 = 1$$
Measurement collapses the Q-bit into a binary feature mask:
$$x_i = \begin{cases} 1 & \text{if } u < |\beta_i|^2, \quad u \sim \mathcal{U}(0, 1) \\ 0 & \text{otherwise} \end{cases}$$
State updates are executed via quantum rotation gates $U(\Delta \theta_i)$:
$$\begin{bmatrix} \alpha_i' \\ \beta_i' \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_i) & -\sin(\Delta \theta_i) \\ \sin(\Delta \theta_i) & \cos(\Delta \theta_i) \end{bmatrix} \begin{bmatrix} \alpha_i \\ \beta_i \end{bmatrix}$$
where $\Delta \theta_i = \text{sign}(\alpha_i \beta_i) \cdot \theta_0$ is looked up from the canonical Han & Kim (2002) state-lookup table comparing candidate fitness against the generation elite.

#### 3.2 Delta-Potential Well QPSO
In contrast to classical PSO requiring velocity vectors and inertia weights, QPSO models particles bound in a quantum delta-potential well.
The mean best position of the swarm is:
$$mbest(t) = \frac{1}{M} \sum_{i=1}^M p_i(t)$$
The local quantum attractor is:
$$p_{ij}(t) = \phi_j(t) \cdot p_{ij}(t) + (1 - \phi_j(t)) \cdot g_j(t), \quad \phi_j(t) \sim \mathcal{U}(0, 1)$$
The position update follows a wave function collapse yielding a double-exponential jump:
$$x_{ij}(t+1) = p_{ij}(t) \pm \alpha \cdot |mbest_j(t) - x_{ij}(t)| \cdot \ln(1 / u_{ij}), \quad u_{ij} \sim \mathcal{U}(0, 1)$$
where $\alpha = \alpha_0 - \frac{t}{T_{\max}} (\alpha_0 - \alpha_1)$ is the linearly contracting quantum creativity parameter.

---

### 4. Promotion Criteria: When Can QI Replace the Operational Baseline?

QI cannot replace the operational baseline on philosophical or marketing grounds. It must satisfy all five **Gate A Promotion Criteria**:
1. **Statistical Superiority:** Paired Wilcoxon signed-rank test $p < 0.01$ with Holm-Bonferroni correction across $\ge 30$ matched seeds.
2. **Practical Significance:** Effect size $> 5.0\%$ MAE reduction ($> 12.3$ kg/h improvement) relative to baseline.
3. **Temporal Invariance:** Superiority must hold across all 3 rolling-origin forward temporal splits without degradation.
4. **Cross-Vessel Generalization:** Outperforms baseline on leave-one-vessel-out evaluation for *all* three vessels.
5. **Physical Robustness:** Zero negative fuel predictions and monotonic response to speed increases.

Until all five criteria are simultaneously satisfied, the **Classical Physics + ML Residual** predictor remains the sole operational engine.

---

### 5. Architectural Approvals & Sign-off

- **ML Research Lead:** Approved (Hypotheses experimentally verified; zero data leakage).
- **Quantum Systems Auditor:** Approved (Legitimate QIEA/QPSO formulations; no quantum advantage hype).
- **Maritime Operations Engineer:** Approved (Holtrop-Mennen physics model strictly preserved).
- **Fleet Optimizer Lead:** Approved (Downstream integration validated with identical 2,500 budget).
