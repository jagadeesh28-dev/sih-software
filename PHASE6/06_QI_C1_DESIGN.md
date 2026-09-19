# PHASE 6 — STEP 6: CANDIDATE QI-C1 ARCHITECTURAL SPECIFICATION
## SIH26138 — Egreen Quanta
### Quantum-Inspired Evolutionary Feature Selection & Quantum-Behaved PSO Hyperparameter Tuning

**Candidate Designation:** QI-C1  
**Formal Scientific Nomenclature:** Quantum-Inspired Optimized Fuel Predictor  
**Compliance Level:** Level 1 (Moderate Compliance)  
**Terminology Constraint:** This architecture runs entirely on classical computing hardware. The predictor MUST NOT be described as a "quantum neural network" or "quantum processor".  

---

## 1. Architectural Overview

Candidate QI-C1 enhances the classical residual learner through a dual quantum-inspired evolutionary mechanism:
1. **Discrete Feature Selection (QIEA):** Uses a Q-bit probability amplitude population with quantum rotation gate updates to explore the combinatorial feature subset space.
2. **Continuous Hyperparameter Optimization (QPSO):** Uses a delta-potential well bound-state particle swarm to tune the regularization and tree structure of the residual regressor.
3. **Downstream Predictor:** A classical LightGBM residual learner trained on the selected feature subset using the optimized hyperparameters.

```
       [14 Candidate Telemetry Features]
                       │
                       ▼
       ┌───────────────────────────────┐
       │   QIEA Feature Selection      │
       │  (Q-Bit Amplitude Population) │
       │    - Superposition Init       │
       │    - Measurement Collapse     │
       │    - Han & Kim Rotation Gate  │
       └───────────────┬───────────────┘
                       │ (Optimal Feature Subset)
                       ▼
       ┌───────────────────────────────┐
       │    QPSO Hyperparameter Tuning │
       │  (Delta-Potential Well Swarm) │
       │    - Mean Best (mbest)        │
       │    - Local Attractor          │
       │    - Contraction-Expansion    │
       └───────────────┬───────────────┘
                       │ (Optimal Model Hyperparameters)
                       ▼
       ┌───────────────────────────────┐
       │   Classical Residual Learner  │
       │    (LightGBM on r = y - F_p)  │
       └───────────────┬───────────────┘
                       │
                       ▼
        y_hat = max(0, F_physics + alpha * r_hat)
```

---

## 2. Mathematical Formulation of QIEA Feature Selection

### 2.1 Q-Bit Chromosome Representation
A candidate feature subset is represented by a string of $m$ classical Q-bits:
$$q = \begin{bmatrix} \alpha_1 & \alpha_2 & \dots & \alpha_m \\ \beta_1 & \beta_2 & \dots & \beta_m \end{bmatrix}$$
where $|\alpha_i|^2 + |\beta_i|^2 = 1.0$. 
- $|\alpha_i|^2$ represents the probability that feature $i$ is **excluded** ($|0\rangle$).
- $|\beta_i|^2$ represents the probability that feature $i$ is **included** ($|1\rangle$).

### 2.2 Superposition Initialization
At $t = 0$, every Q-bit is initialized to equal probability amplitude:
$$\alpha_i = \beta_i = \frac{1}{\sqrt{2}} \implies |\beta_i|^2 = 0.5$$
This represents an unbiased superposition across all $2^m$ possible feature combinations.

### 2.3 Measurement Collapse
A classical binary decision vector $x \in \{0, 1\}^m$ is obtained by sampling independent random numbers $u_i \sim \mathcal{U}(0, 1)$:
$$x_i = \begin{cases} 1, & \text{if } u_i < |\beta_i|^2 \\ 0, & \text{otherwise} \end{cases}$$
Safety guard: If $\sum x_i = 0$, the feature with the highest $|\beta_i|^2$ is set to 1.

### 2.4 Quantum Rotation Gate Update
Amplitudes are updated via the rotation operator $U(\Delta \theta_i)$:
$$\begin{bmatrix} \alpha_i(t+1) \\ \beta_i(t+1) \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_i) & -\sin(\Delta \theta_i) \\ \sin(\Delta \theta_i) & \cos(\Delta \theta_i) \end{bmatrix} \begin{bmatrix} \alpha_i(t) \\ \beta_i(t) \end{bmatrix}$$
The rotation magnitude is fixed at $\theta_{step} = 0.05\pi\text{ rad}$. The direction sign $s(\alpha_i, \beta_i)$ is looked up in the canonical Han & Kim (2002) quadrant table based on the relative fitness of the current collapsed string vs. the population best.

### 2.5 Quantum Population Entropy
Search diversity is monitored across generations via Shannon quantum entropy:
$$H(Q) = -\frac{1}{m} \sum_{i=1}^m \left( |\alpha_i|^2 \log_2 |\alpha_i|^2 + |\beta_i|^2 \log_2 |\beta_i|^2 \right)$$
$H(Q) = 1.0$ indicates maximal exploratory superposition; $H(Q) \to 0.0$ indicates convergence to a deterministic feature subset.

---

## 3. Mathematical Formulation of QPSO Hyperparameter Optimization

### 3.1 Delta-Potential Well Bound States
Classical PSO suffers from velocity explosion and premature stagnation. QPSO models particles as quantum entities trapped in a delta-potential well centered at the local attractor $p_{ij}$.

### 3.2 Mean Best Position ($mbest$)
$$mbest_j(t) = \frac{1}{N} \sum_{i=1}^N P_{ij}(t)$$
where $P_{ij}$ is the personal historical best of particle $i$ in dimension $j$.

### 3.3 Local Attractor
$$p_{ij}(t) = \phi_j(t) P_{ij}(t) + (1 - \phi_j(t)) G_j(t), \quad \phi_j \sim \mathcal{U}(0, 1)$$
where $G_j(t)$ is the global swarm best.

### 3.4 Quantum Position Update
Solving the Schrödinger wave equation for a 1D delta-potential well yields the probability density $|\psi(x)|^2$, resulting in the stochastic position step:
$$X_{ij}(t+1) = p_{ij}(t) \pm \beta(t) \cdot |mbest_j(t) - X_{ij}(t)| \cdot \ln\left( \frac{1}{u_{ij}(t)} \right), \quad u_{ij} \sim \mathcal{U}(0, 1)$$

### 3.5 Contraction-Expansion Schedule
The parameter $\beta(t)$ governs exploration/exploitation:
$$\beta(t) = 1.0 - 0.5 \left( \frac{t}{T_{max}} \right)$$

---

## 4. Fair Computational Budget Ledger

To ensure absolute experimental fairness against classical counterparts:
- **Feature Selection:** QIEA budget = $10\text{ particles} \times 15\text{ generations} = 150\text{ evaluations}$.
  - Matched classical control: Classical Genetic Algorithm (CGA) with identical 150 evaluations.
- **Hyperparameter Optimization:** QPSO budget = $15\text{ particles} \times 10\text{ iterations} = 150\text{ evaluations}$.
  - Matched classical controls: Classical PSO (150 evals) and Uniform Random Search (150 evals).
- **Search Space:** 8 continuous/discrete hyperparameters identically bounded across all methods.
