# PHASE 6: IMMUTABLE BENCHMARK PROTOCOL
## SIH26138 — Egreen Quanta
**Protocol Version:** `6.0-FROZEN`  
**Effective Date:** 2026-09-19  
**Status:** `IMMUTABLE`  

---

### 1. Scientific Principle & Boundaries

This protocol establishes the rigorous, adversarial evaluation standard for determining whether Quantum-Inspired (QI) computational mechanisms provide measurable, practical, and statistically significant improvements for maritime fuel and energy prediction relative to a strong physics-informed residual ML baseline.

#### Disclaimers
1. **Classical Hardware Execution:** All algorithms run strictly on classical x86_64 / AMD64 computing infrastructure.
2. **No Physical Quantum Claims:** Claims of physical qubits, quantum hardware, quantum annealing, quantum advantage, exponential speedup, or quantum supremacy are strictly prohibited.
3. **Acceptance of Negative Results:** Hypothesis $H3$ (QI performs worse than or equal to classical ML) is considered a completely valid, publishable scientific finding that validates classical gradient boosting for tabular telemetry.

---

### 2. Candidate Model Inventory & Matched Classical Controls

| Model Code | Model Name | Primary Mechanism | Classical Matched Control | Parameter / Budget Parity |
|---|---|---|---|---|
| **`P0`** | Physics Only | Holtrop-Mennen First-Principles | Baseline Prior | 0 learned parameters |
| **`P1`** | Pure ML | Gradient Boosted Decision Trees | Standard ML Baseline | LightGBM 150 trees |
| **`P2`** | Physics + ML (Frozen Baseline) | Hybrid Residual Learning ($\alpha=1.0$) | Operational Benchmark | Frozen: $R^2=0.9501, \text{MAE}=246.97$ |
| **`P3`** | Physics + Classical GA-FS + ML | Binary Genetic Algorithm Feature Selection | Baseline Search | 10 pop $\times$ 15 gen = 150 evaluations |
| **`P4`** | Physics + QIEA-FS + ML (QI-C1) | Q-Bit Chromosome + Rotation Gates | Matched Classical GA (`P3`) | 10 pop $\times$ 15 gen = 150 evaluations |
| **`P5`** | Physics + QIEA-FS + QPSO-HPO + ML (QI-C2) | QIEA Feature Selection + Delta-Potential QPSO HPO | Matched CGA + Classical PSO (`CPSO`) | 150 FS evals + 150 HPO evals |
| **`P6`** | Physics + Direct QI/MPS Residual (QI-C3) | Matrix Product State (MPS) on Trigonometric Feature Map | Matched Polynomial / Kernel Ridge | Equivalent parameter budget |
| **`P7`** | Physics + QI Ensemble (QI-C4) | Multi-model consensus from QIEA diverse Pareto features | Classical Ensemble | Equivalent model count |

---

### 3. Mathematical Specifications

#### 3.1 QIEA Feature Selection (`QI-C1`)
- **Q-Bit Chromosome:**
  $$q_i = \begin{bmatrix} \alpha_i \\ \beta_i \end{bmatrix}, \quad |\alpha_i|^2 + |\beta_i|^2 = 1, \quad P(\text{select}_i) = |\beta_i|^2$$
- **Initialization:** $\alpha_i = \beta_i = \frac{1}{\sqrt{2}}$ for all $i \in \{1, \dots, m\}$ (equal superposition).
- **Quantum Rotation Gate:**
  $$U(\theta_i) = \begin{bmatrix} \cos(\Delta \theta_i) & -\sin(\Delta \theta_i) \\ \sin(\Delta \theta_i) & \cos(\Delta \theta_i) \end{bmatrix}$$
  where rotation magnitude is $|\Delta \theta| = 0.05 \pi$ radians, with direction governed by the standard Han & Kim (2002) sign lookup table comparing measured state $x_i$, elite best $b_i$, and relative fitness.

#### 3.2 QPSO Hyperparameter Optimization (`QI-C2`)
- **Delta-Potential Well Dynamics:**
  $$\text{mbest} = \frac{1}{N}\sum_{i=1}^N P_i$$
  $$p_{ij} = \phi_j P_{ij} + (1 - \phi_j) g_j, \quad \phi_j \sim U(0, 1)$$
  $$X_{ij}(t+1) = p_{ij} \pm \beta(t) |\text{mbest}_j - X_{ij}(t)| \ln\left(\frac{1}{u_{ij}}\right), \quad u_{ij} \sim U(0, 1)$$
- **Contraction-Expansion Schedule:** $\beta(t) = 1.0 - 0.5 \cdot (t / T_{\max})$.

#### 3.3 Direct QI Matrix Product State Regressor (`QI-C3`)
- **Quantum Feature Map:**
  $$\phi(x_i) = \begin{bmatrix} \cos\left(\frac{\pi x_i}{2}\right) \\ \sin\left(\frac{\pi x_i}{2}\right) \end{bmatrix}, \quad x_i \in [0, 1]$$
- **Tensor Network Contraction:**
  $$\hat{r}_{\text{QI}}(x) = \sum_{s_1, \dots, s_d} W_{s_1 \dots s_d} \left( \phi^{s_1}(x_1) \otimes \cdots \otimes \phi^{s_d}(x_d) \right)$$
  factorized into a matrix product state with bond dimension $\chi \in \{2, 4\}$.

---

### 4. Validation Matrices

1. **Forward Temporal Split:** Chronological 60% Train, 20% Validation, 20% Test per vessel.
2. **Rolling-Origin Validation:** 3 progressive temporal windows:
   - Window 1: Train 50%, Test 15%
   - Window 2: Train 65%, Test 15%
   - Window 3: Train 80%, Test 20%
3. **Leave-One-Vessel-Out (LOVO):**
   - Fold 1: Train Triton + Ceto $\to$ Test Poseidon (70k GT container)
   - Fold 2: Train Poseidon + Ceto $\to$ Test Triton (24k GT container)
   - Fold 3: Train Poseidon + Triton $\to$ Test Ceto (45k GT bulk)
4. **Operating Regime Stratification:** Evaluated on `NORMAL_CRUISING`, `MANEUVERING`, `STOPPED_HARBOR`, `ROUGH_SEA`.
5. **Out-of-Distribution (OOD):** Mahalanobis distance with 95th percentile threshold on training features.

---

### 5. Statistical Rigor Standards

- **Replications:** 30 independent matched seeds (Seed 42, Seeds 1001–1029).
- **Hypothesis Testing:** Two-sided paired Wilcoxon signed-rank test against baseline `P2`.
- **Multiplicity Correction:** Holm-Bonferroni step-down procedure applied across all comparisons.
- **Effect Size:** Rank-biserial correlation ($r$) and Hodges-Lehmann median difference.
- **Confidence Intervals:** 95% bootstrap confidence intervals (1,000 resamples).
- **Feature Stability:** Pairwise Jaccard similarity index across seeds.
- **Diversity:** Shannon entropy of Q-bit probability distributions.

---

### 6. Decision Gate Criteria

At the conclusion of the benchmark, exactly one gate will be certified:
- **`GATE A` (QI Superior):** QI demonstrates statistically significant improvement ($p < 0.05$ after Holm correction) with practical significance ($\Delta\text{MAPE} \ge 1.0\%$) and zero physical violations.
- **`GATE B` (QI Competitive & Useful for Other Property):** Accuracy matches classical ($p \ge 0.05$), but QI provides demonstrably higher feature stability, search diversity, or uncertainty calibration.
- **`GATE C` (QI Scientifically Valid but Inferior):** QI is implemented with full mathematical fidelity but performs worse than LightGBM; retained as an audited research benchmark.
- **`GATE D` (QI Invalid / Non-Reproducible):** Flaws detected in formulation or execution; redesign required.
