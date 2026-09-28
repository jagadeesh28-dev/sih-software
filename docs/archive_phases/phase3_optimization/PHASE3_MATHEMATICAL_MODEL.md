# PHASE 3 MATHEMATICAL MODEL
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Mathematical Formulations & Optimization Theory  
**Date:** 2026-09-12  
**Status:** MATHEMATICAL SPECIFICATION LOCKED  

---

## 1. General Optimization Problem Formulation

The green maritime fleet dispatch problem is formulated as a non-linear, non-convex, mixed-variable constrained multi-objective optimization problem:

$$\begin{aligned}
\min_{\mathbf{x} \in \mathcal{X}} \quad & \mathbf{F}(\mathbf{x}) = \left[ f_1(\mathbf{x}), f_2(\mathbf{x}), f_3(\mathbf{x}), f_4(\mathbf{x}), f_5(\mathbf{x}) \right]^T \\
\text{subject to} \quad & g_i(\mathbf{x}) \le 0, \quad i = 1, \dots, m \\
& h_j(\mathbf{x}) = 0, \quad j = 1, \dots, p \\
& \mathbf{x}_L \le \mathbf{x} \le \mathbf{x}_U
\end{aligned}$$

where:
- $\mathbf{x} \in \mathcal{X} \subset \mathbb{R}^{n_{\text{cont}}} \times \mathbb{Z}^{n_{\text{disc}}}$ is the hybrid continuous-discrete decision vector.
- $\mathbf{F}(\mathbf{x}): \mathcal{X} \to \mathbb{R}^5$ is the objective vector mapping operating decisions to fuel, cost, emissions, delay, and uncertainty risk.
- $g_i(\mathbf{x})$ are inequality constraints (domain envelope, capacity, speed limits, engine power, deadlines).
- $h_j(\mathbf{x})$ are equality constraints (engine-fuel compatibility, binary dispatch logic).

---

## 2. Objective Function Formulations

### 2.1 Fuel Consumption Objective ($f_1(\mathbf{x})$)
For a voyage divided into $L$ legs with distance $D_l$ ($\text{nm}$), operational speed $V_l$ ($\text{kn}$), and operational mode $\text{Mode}_l$:

$$f_1(\mathbf{x}) = \frac{1}{1000} \sum_{l=1}^L \dot{m}_{f, l}(\mathbf{x}) \cdot T_l(\mathbf{x}) \quad \left[\text{metric tonnes fuel}\right]$$

where $\dot{m}_{f, l}(\mathbf{x})$ ($\text{kg/h}$) is evaluated by the surrogate model:
$$\dot{m}_{f, l}(\mathbf{x}) = \text{SafeFuelObjective}\left(V_{l, \text{actual}}, T_{\text{draft}}, \Delta, H_{s, l}, T_{p, l}, V_{\text{wind}, l}, \text{vessel\_id}\right)$$

### 2.2 Operational Cost Objective ($f_2(\mathbf{x})$)
$$f_2(\mathbf{x}) = C_{\text{fuel}}(\mathbf{x}) + C_{\text{carbon}}(\mathbf{x}) + C_{\text{shore}}(\mathbf{x}) + C_{\text{schedule}}(\mathbf{x}) + C_{\text{penalty}}(\mathbf{x}) \quad \left[\text{USD}\right]$$

Expanded terms:
- **Fuel Cost**:
  $$C_{\text{fuel}}(\mathbf{x}) = \sum_{l=1}^L \left( \frac{\dot{m}_{f, l} \cdot T_l}{1000} \right) \cdot P_{\text{fuel}}(F_{\text{type}})$$
- **Carbon Tax Cost (EU ETS / IMO Levy)**:
  $$C_{\text{carbon}}(\mathbf{x}) = \text{Scope}_{\text{ETS}} \cdot \text{GHG}_{\text{TtW}}(\mathbf{x}) \cdot P_{\text{carbon}}$$
- **Shore Power Cost**:
  $$C_{\text{shore}}(\mathbf{x}) = \mathbb{I}_{S_{\text{shore}}=1} \cdot \left( P_{\text{hotel}} \cdot T_{\text{port}} \cdot \text{Tariff}_{\text{kWh}} + \text{Fee}_{\text{connect}} \right)$$
- **Schedule Demurrage Cost**:
  $$C_{\text{schedule}}(\mathbf{x}) = c_{\text{demurrage}} \cdot \max\left(0, T_{\text{voyage}}(\mathbf{x}) - T_{\text{deadline}}\right)$$

### 2.3 Well-to-Wake Lifecycle GHG Emissions ($f_3(\mathbf{x})$)
$$\begin{aligned}
f_3(\mathbf{x}) &= \text{GHG}_{\text{WtT}}(\mathbf{x}) + \text{GHG}_{\text{TtW}}(\mathbf{x}) + \text{GHG}_{\text{slip}}(\mathbf{x}) \quad \left[\text{tonnes CO}_2\text{e}\right] \\
&= \sum_{l=1}^L \left[ \frac{m_{f, l} \cdot \text{LHV} \cdot e_{\text{WtT}}}{10^6} + \frac{m_{f, l} \cdot C_{f, \text{CO}_2}}{1000} + \frac{m_{f, l} \cdot e_{\text{N}_2\text{O}} \cdot \text{GWP}_{\text{N}_2\text{O}}}{10^6} + \frac{m_{f, l} \cdot \sigma_{\text{slip}} \cdot \text{GWP}_{\text{CH}_4}}{1000} \right]
\end{aligned}$$

### 2.4 Schedule Delay Objective ($f_4(\mathbf{x})$)
$$f_4(\mathbf{x}) = \max\left(0, T_{\text{voyage}}(\mathbf{x}) - T_{\text{deadline}}\right) + \kappa_{\text{early}} \max\left(0, T_{\text{earliest}} - T_{\text{voyage}}(\mathbf{x})\right) \quad \left[\text{hours}\right]$$

### 2.5 Epistemic & Aleatoric Uncertainty Risk ($f_5(\mathbf{x})$)
$$f_5(\mathbf{x}) = \frac{1}{1000} \sum_{l=1}^L \left[ q_{95, l}(\mathbf{x}) - q_{05, l}(\mathbf{x}) \right] \cdot T_l(\mathbf{x}) \quad \left[\text{tonnes dispersion}\right]$$

---

## 3. Hydrodynamics & Involuntary Speed Loss

In heavy seas, commanded speed $V_{\text{command}}$ cannot be sustained due to added resistance. Actual speed through water $V_{\text{actual}}$ is calculated using the Kwon empirical resistance formulation:

$$\frac{\Delta V}{V_{\text{command}}} = \frac{\alpha_{\text{form}} \cdot H_s + \beta_{\text{form}} \cdot V_{\text{wind}}}{100} \cdot f(\theta_{\text{rel}})$$

where:
$$f(\theta_{\text{rel}}) = \begin{cases} 
1.00 & \text{for head seas } (0^\circ \le |\theta_{\text{rel}}| \le 30^\circ) \\
0.75 & \text{for bow quartering seas } (30^\circ < |\theta_{\text{rel}}| \le 60^\circ) \\
0.50 & \text{for beam seas } (60^\circ < |\theta_{\text{rel}}| \le 120^\circ) \\
0.25 & \text{for following seas } (120^\circ < |\theta_{\text{rel}}| \le 180^\circ)
\end{cases}$$

Effective transit time:
$$T_l = \frac{D_l}{\max\left(V_{\min}, V_{\text{command}} - \Delta V\right)}$$

---

## 4. Scalarization Methods

### 4.1 Normalized Weighted-Sum Scalarization
$$J_{\text{scalar}}(\mathbf{x}) = \sum_{k=1}^5 w_k \left( \frac{f_k(\mathbf{x}) - f_k^{\min}}{f_k^{\max} - f_k^{\min}} \right) + P_{\text{penalty}}(\mathbf{x})$$

where $w_k \ge 0$, $\sum w_k = 1$, and $P_{\text{penalty}}$ is the constraint penalty.

### 4.2 Augmented Chebyshev Scalarization
$$J_{\text{cheby}}(\mathbf{x}) = \max_{k \in \{1,\dots,5\}} \left\{ w_k \left( \frac{f_k(\mathbf{x}) - z_k^*}{f_k^{\max} - f_k^{\min}} \right) \right\} + \rho \sum_{k=1}^5 w_k \left( \frac{f_k(\mathbf{x}) - z_k^*}{f_k^{\max} - f_k^{\min}} \right)$$

where $z_k^* = \min_{\mathbf{x}} f_k(\mathbf{x})$ is the ideal objective point and $\rho = 10^{-4}$ is the augmentation factor.

### 4.3 Risk-Adjusted Robust Objective Formulation
$$J_{\text{robust}}(\lambda) = q_{50} + \lambda \cdot (q_{95} - q_{05}), \quad \lambda \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$$

---

## 5. Quantum-Behaved Particle Swarm Optimization (QPSO) Theory

### 5.1 Physical & Mathematical Principles
In canonical PSO, particles possess a velocity vector that determines their trajectory through classical phase space. In **QPSO (Sun, Feng, & Xu, 2004)**, particles move in quantum space where their state is governed by a wave function $\psi(\mathbf{x}, t)$ in a delta-potential well centered at a local attractor $\mathbf{p}$.

The probability density of a particle appearing at position $\mathbf{x}$ follows the exponential decay:
$$|\psi(\mathbf{x})|^2 = \frac{1}{L} \exp\left( -\frac{2 |\mathbf{x} - \mathbf{p}|}{L} \right)$$
where $L$ is the characteristic width of the potential well.

Employing the Monte Carlo inverse transform method on $u \sim \mathcal{U}(0, 1)$:
$$x_d = p_d \pm \frac{L}{2} \ln\left( \frac{1}{u} \right)$$

### 5.2 QPSO Algorithmic Equations
For swarm size $M$, dimension $D$, iteration $t \in \{1, \dots, t_{\max}\}$:

1. **Local Stochastic Attractor**:
   $$p_{i,d}(t) = \phi_d(t) \cdot \text{pbest}_{i,d}(t) + (1 - \phi_d(t)) \cdot \text{gbest}_d(t), \quad \phi_d \sim \mathcal{U}(0, 1)$$

2. **Mean Best Position (Center of Gravity)**:
   $$mbest_d(t) = \frac{1}{M} \sum_{i=1}^M \text{pbest}_{i,d}(t)$$

3. **Characteristic Well Length**:
   $$L_{i,d}(t) = 2 \beta(t) \cdot |mbest_d(t) - x_{i,d}(t)|$$

4. **Quantum Position Update**:
   $$x_{i,d}(t+1) = p_{i,d}(t) \pm \beta(t) \cdot |mbest_d(t) - x_{i,d}(t)| \cdot \ln\left( \frac{1}{u} \right), \quad u \sim \mathcal{U}(0, 1)$$
   The sign $\pm$ is selected with probability $0.5$.

5. **Contraction-Expansion Schedule**:
   $$\beta(t) = \beta_{\text{start}} - (\beta_{\text{start}} - \beta_{\text{end}}) \cdot \left( \frac{t}{t_{\max}} \right)$$
   Typically: $\beta_{\text{start}} = 1.0$, $\beta_{\text{end}} = 0.5$.

---

## 6. Classical Benchmark Optimizers

### 6.1 Canonical Particle Swarm Optimization (PSO)
Velocity and position equations:
$$v_{i,d}(t+1) = w \cdot v_{i,d}(t) + c_1 r_1 \left(\text{pbest}_{i,d}(t) - x_{i,d}(t)\right) + c_2 r_2 \left(\text{gbest}_d(t) - x_{i,d}(t)\right)$$
$$x_{i,d}(t+1) = x_{i,d}(t) + v_{i,d}(t+1)$$
Parameters: $w = 0.7298$, $c_1 = 1.49618$, $c_2 = 1.49618$ (Clerc's constriction coefficient).

### 6.2 Genetic Algorithm (GA)
- **Simulated Binary Crossover (SBX)**:
  $$\beta_q = \begin{cases}
  (2u)^{\frac{1}{\eta_c + 1}} & \text{if } u \le 0.5 \\
  \left(\frac{1}{2(1-u)}\right)^{\frac{1}{\eta_c + 1}} & \text{otherwise}
  \end{cases}$$
  $$c_1 = 0.5 \left[ (1 + \beta_q) p_1 + (1 - \beta_q) p_2 \right], \quad c_2 = 0.5 \left[ (1 - \beta_q) p_1 + (1 + \beta_q) p_2 \right]$$
  with distribution index $\eta_c = 15$.
- **Polynomial Mutation**:
  $$\delta_q = \begin{cases}
  (2r)^{\frac{1}{\eta_m + 1}} - 1 & \text{if } r \le 0.5 \\
  1 - [2(1-r)]^{\frac{1}{\eta_m + 1}} & \text{otherwise}
  \end{cases}$$
  with distribution index $\eta_m = 20$.

### 6.3 Differential Evolution (DE/rand/1/bin)
- **Donor Vector Generation**:
  $$\mathbf{v}_i(t+1) = \mathbf{x}_{r_1}(t) + F \cdot \left(\mathbf{x}_{r_2}(t) - \mathbf{x}_{r_3}(t)\right), \quad r_1 \ne r_2 \ne r_3 \ne i$$
- **Binomial Crossover**:
  $$u_{i,d}(t+1) = \begin{cases}
  v_{i,d}(t+1) & \text{if } \text{rand}_d(0,1) \le CR \text{ or } d = d_{\text{rand}} \\
  x_{i,d}(t) & \text{otherwise}
  \end{cases}$$
  Parameters: $F = 0.8$, $CR = 0.9$.

---

## 7. Multi-Objective Performance Metrics

For evaluating Pareto front approximation $\mathcal{P}$ against reference front $\mathcal{P}^*$:

1. **Hypervolume ($HV$)**:
   $$HV(\mathcal{P}, \mathbf{r}) = \Lambda\left( \bigcup_{\mathbf{y} \in \mathcal{P}} [\mathbf{y}, \mathbf{r}] \right)$$
   where $\mathbf{r}$ is the nadir reference point and $\Lambda$ denotes Lebesgue measure.

2. **Generational Distance ($GD$)**:
   $$GD(\mathcal{P}, \mathcal{P}^*) = \frac{\sqrt{\sum_{\mathbf{y} \in \mathcal{P}} \min_{\mathbf{y}^* \in \mathcal{P}^*} \|\mathbf{y} - \mathbf{y}^*\|^2}}{|\mathcal{P}|}$$

3. **Inverted Generational Distance ($IGD$)**:
   $$IGD(\mathcal{P}^*, \mathcal{P}) = \frac{\sum_{\mathbf{y}^* \in \mathcal{P}^*} \min_{\mathbf{y} \in \mathcal{P}} \|\mathbf{y}^* - \mathbf{y}\|}{|\mathcal{P}^*|}$$

4. **Spacing Metric ($S$)**:
   $$S(\mathcal{P}) = \sqrt{\frac{1}{|\mathcal{P}| - 1} \sum_{i=1}^{|\mathcal{P}|} (d_i - \bar{d})^2}, \quad d_i = \min_{j \ne i} \|\mathbf{y}_i - \mathbf{y}_j\|_1$$
