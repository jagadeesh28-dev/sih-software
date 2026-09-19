# Scientific Methodology & Algorithmic Formulation
**System**: Egreen Quanta  
**Classification**: Hybrid Physics + Quantum-Inspired Machine Learning & Fleet Optimization  
**Audit Date**: September 2026  

---

## 1. Hybrid Hydrodynamic Residual Modeling
Pure empirical machine learning models often predict non-physical artifacts (e.g., negative fuel consumption at high speed) when extrapolated. Pure physics models, conversely, suffer from systematic inaccuracies due to unmodeled hull roughness and complex sea-state interactions.

Egreen Quanta resolves this through **Hybrid Physics-Guided Residual Learning**:
$$y(\mathbf{x}) = f_{\text{phys}}(\mathbf{x}) + r(\mathbf{x})$$
where:
1. $f_{\text{phys}}(\mathbf{x})$ is a deterministic first-principles hydrodynamic model based on Holtrop-Mennen resistance estimation, ITTC-1978 friction lines, and Isherwood wind resistance.
2. $r(\mathbf{x})$ is a non-linear residual correction learned by machine learning models trained specifically to predict the hydrodynamic deficit:
   $$r_i = y_{\text{actual},i} - f_{\text{phys}}(\mathbf{x}_i)$$

---

## 2. Quantum-Inspired Evolutionary Algorithm (QIEA) Feature Selection
To select the optimal subset of operational and environmental features, QIEA encodes feature inclusion probabilities as quantum-inspired bit registers (qubits):
$$q_j = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \quad |\alpha_j|^2 + |\beta_j|^2 = 1$$
where $|\beta_j|^2$ represents the probability that feature $j$ is included in the predictive model.

### Qubit Update Gate
Qubits are updated towards the best-performing individual $\mathbf{b}^*$ using a quantum rotation gate:
$$\begin{bmatrix} \alpha_j(t+1) \\ \beta_j(t+1) \end{bmatrix} = \begin{bmatrix} \cos(\Delta\theta_j) & -\sin(\Delta\theta_j) \\ \sin(\Delta\theta_j) & \cos(\Delta\theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j(t) \\ \beta_j(t) \end{bmatrix}$$
The rotation angle $\Delta\theta_j$ is dynamically scheduled according to the lookup table between current bit $x_j$, best bit $b_j^*$, and objective fitness.

### Verified Result
On the FuelCast fleet, QIEA converged to a compact **6-feature subset**:
$$\mathbf{x}_{\text{QI}} = \{\text{stw\_kn}, \text{sog\_kn}, \text{draft\_m}, \text{wave\_height\_m}, \text{water\_depth\_m}, \text{fuel\_type}\}$$
eliminating 8 redundant sensor channels while preserving predictive accuracy ($\text{MAE} = 237.96\text{ kg/h}$ vs $248.12\text{ kg/h}$ baseline).

---

## 3. Quantum-Behaved Particle Swarm Optimization (QPSO)
In classical PSO, particles follow deterministic Newtonian trajectories and are susceptible to premature stagnation in local minima. QPSO models particles as quantum entities trapped in an attractive delta-potential well centered at the local attractor $\mathbf{p}_i$:
$$p_{i,d} = \phi \cdot p_{\text{best},i,d} + (1 - \phi) \cdot g_{\text{best},d}, \quad \phi \sim \mathcal{U}(0, 1)$$

The particle position update is derived from the Schrödinger wave-function solution:
$$x_{i,d}(t+1) = p_{i,d} \pm \beta \cdot |C_d - x_{i,d}(t)| \cdot \ln(1/u), \quad u \sim \mathcal{U}(0, 1)$$
where $C_d = \frac{1}{N}\sum_{i=1}^N p_{\text{best},i,d}$ is the mean best position across the swarm, and $\beta$ is the contraction-expansion coefficient controlling quantum exploration.

---

## 4. Benchmark Against Classical Controls
To avoid unfounded quantum superiority claims, all quantum-inspired techniques were rigorously benchmarked against matched classical controls across 30 independent seeds:
- **QIEA vs. Classical GA**:
  - QIEA 30-seed MAE: $237.96 \pm 5.46\text{ kg/h}$
  - Classical GA 30-seed MAE: $237.24 \pm 4.89\text{ kg/h}$
  - Statistical significance: $p = 0.684$ (Wilcoxon signed-rank test).
  - Verdict: **Statistically competitive; no quantum advantage demonstrated on predictive accuracy.**
- **Population Diversity Advantage**:
  - QIEA maintains $+44.7\%$ higher bit-entropy ($H = 0.2814$ vs $0.1945$) across iterations, indicating superior resistance to genetic drift.

---

## 5. Alternative Fuel Energy Equivalence
Green fuels (bio-methanol, green ammonia, liquid hydrogen) are evaluated on an **invariant shaft work** thermodynamic basis:
$$E_{\text{shaft}} = P_B \cdot t = \dot{m}_{f,\text{ref}} \cdot \text{LHV}_{\text{ref}} \cdot \eta_{\text{ref}}$$
The equivalent fuel mass flow rate $\dot{m}_{f,\text{alt}}$ is given by:
$$\dot{m}_{f,\text{alt}} = \frac{E_{\text{shaft}}}{\text{LHV}_{\text{alt}} \cdot \eta_{\text{alt}}}$$

### Lifecycle Emissions Accounting
Lifecycle emissions are partitioned into:
1. **Well-to-Tank (WtT)**: Upstream fuel production, synthesis, and bunkering logistics.
2. **Tank-to-Wake (TtW)**: Direct combustion emissions on board the vessel.
3. **Well-to-Wake (WtW)**: Complete lifecycle carbon footprint:
   $$\text{GHG}_{\text{WtW}} = \dot{m}_f \cdot (\text{EF}_{\text{WtT}} + \text{EF}_{\text{TtW}})$$
