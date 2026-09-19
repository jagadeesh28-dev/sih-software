# Phase 5 Mathematical Model: Multi-Objective Robust Fleet Optimization
## SIH26138 — Egreen Quanta

---

## 1. Formal Optimization Problem Statement

We formulate the green fleet deployment problem as a constrained, stochastic, mixed-integer multi-objective optimization problem over a fleet of $V$ heterogeneous vessels and $K$ operational cargo transport demands:

$$\min_{\mathbf{x} \in \mathcal{X}} \mathbf{F}(\mathbf{x}) = \begin{bmatrix} J_{\text{Fuel}}(\mathbf{x}) \\ J_{\text{OPEX}}(\mathbf{x}) \\ J_{\text{GHG}}(\mathbf{x}) \\ J_{\text{Delay}}(\mathbf{x}) \\ J_{\text{Risk}}(\mathbf{x}) \end{bmatrix}$$

subject to:
$$\begin{aligned}
g_j(\mathbf{x}) &\le 0, \quad j = 1, \dots, N_{\text{hard}} \quad &\text{(Hard Feasibility Constraints)} \\
h_l(\mathbf{x}) &\le 0, \quad l = 1, \dots, N_{\text{soft}} \quad &\text{(Operational / Regulatory Penalties)}
\end{aligned}$$

---

## 2. Decision Vector Parameterization

For each vessel $v \in \{1, \dots, V\}$, the local decision sub-vector is defined as:
$$\mathbf{x}_v = \big[ d_v, m_v, s_v, f_v, o_v, p_v \big]^T$$
where:
- $d_v \in \{0, 1, \dots, K\}$: Assigned cargo demand index (0 = Unassigned / Idle).
- $m_v \in [0, \text{DWT}_v]$: Payload cargo quantity (tonnes).
- $s_v \in [v_{\min, v}, v_{\max, v}]$: Commanded speed through water (knots).
- $f_v \in \{0, 1, \dots, F-1\}$: Fuel selection index (0: VLSFO, 1: LNG, 2: Bio-methanol, 3: Ammonia, 4: Hydrogen).
- $o_v \in \{0, 1, 2, 3\}$: Operating mode (0: Transit, 1: Maneuvering, 2: Dynamic Positioning, 3: Port).
- $p_v \in \{0, 1\}$: Cold ironing / Shore power activation status.

---

## 3. Physical Models and Environmental Dynamics

### 3.1 Involuntary Speed Loss (Voyage Kinematics)
Under environmental weather scenario $\omega = (H_s, T_p, V_w, \theta_w, V_c, \theta_c)$, the involuntary speed loss $\Delta v_{\text{loss}}$ is computed via naval hydrodynamic transfer functions:
$$s_{\text{actual}}(v, \omega) = \max\left(0.1, s_v - C_{\text{hull}}(v) \cdot H_s^2 - C_{\text{wind}}(v) \cdot V_w \cos(\theta_w)\right)$$
Voyage transit duration:
$$T_{\text{voyage}}(v, \omega) = \frac{D(d_v)}{s_{\text{actual}}(v, \omega)} + T_{\text{port}}$$

### 3.2 Fuel Mass Flow Rate (Telemetry-Calibrated Surrogates)
Fuel consumption rate $\dot{m}_f$ (kg/h) is evaluated using the vessel's calibrated `SafeFuelObjective` Gaussian Process / XGBoost surrogate:
$$\dot{m}_f(v, \omega) = f_{\text{surrogate}}^{(v)}\big(s_{\text{actual}}, m_v, H_s, T_p, V_w\big) \cdot \frac{\text{LHV}_{\text{base}}}{\text{LHV}(f_v)}$$
Total voyage fuel consumption:
$$M_{\text{fuel}}(v, \omega) = \dot{m}_f(v, \omega) \cdot T_{\text{voyage}}(v, \omega) \cdot 10^{-3} \quad (\text{tonnes})$$

---

## 4. Cost and Regulatory Formulations

### 4.1 Total OPEX Function
$$J_{\text{OPEX}}(v, \omega) = C_{\text{fuel}} + C_{\text{carbon}} + C_{\text{shore}} + C_{\text{delay}} + C_{\text{FuelEU}}$$
where:
- Fuel Cost: $C_{\text{fuel}} = M_{\text{fuel}}(v, \omega) \cdot P_{\text{fuel}}(f_v)$
- Carbon Cost: $C_{\text{carbon}} = M_{\text{fuel}} \cdot \text{CF}(f_v) \cdot P_{\text{carbon}}$ (EU ETS allowance: $\$90/\text{tCO}_2$)
- Shore Power Cost: $C_{\text{shore}} = P_{\text{hotel}}(v) \cdot T_{\text{port}} \cdot P_{\text{elec}}$ if $p_v = 1$
- Schedule Delay Cost: $C_{\text{delay}} = \max(0, T_{\text{voyage}} - T_{\text{deadline}}(d_v)) \cdot \$500/\text{h}$
- FuelEU Compliance Penalty:
  $$\text{Penalty}_{\text{FuelEU}} = \max\left(0, \frac{\text{GHG}_{\text{actual}} - \text{GHG}_{\text{target}}}{\text{GHG}_{\text{target}}}\right) \cdot \$2,400/\text{tVLSFO}_{\text{eq}}$$

### 4.2 Well-to-Wake (WtW) Emissions
$$J_{\text{GHG}}(\mathbf{x}, \omega) = \sum_{v=1}^V M_{\text{fuel}}(v, \omega) \cdot \left(\text{EF}_{\text{TtW}}(f_v) + \text{EF}_{\text{WtT}}(f_v)\right)$$

---

## 5. Weather Uncertainty and CVaR Risk Metric

Given weather scenarios $\Omega = \{\omega_1, \dots, \omega_S\}$ with discrete probabilities $p_s \ge 0$, $\sum_s p_s = 1$:
1. **Expected Loss**:
   $$\mathbb{E}_\omega[J(\mathbf{x})] = \sum_{s=1}^S p_s \cdot J(\mathbf{x}, \omega_s)$$
2. **Value at Risk ($\text{VaR}_\alpha$)**:
   $$\text{VaR}_\alpha(\mathbf{x}) = \min \{ \gamma \in \mathbb{R} : \sum_{s: J(\mathbf{x}, \omega_s) \le \gamma} p_s \ge \alpha \}$$
3. **Conditional Value at Risk ($\text{CVaR}_\alpha$)** at risk level $\alpha = 0.80$:
   $$\text{CVaR}_\alpha(\mathbf{x}) = \frac{1}{1 - \alpha} \sum_{s: J(\mathbf{x}, \omega_s) \ge \text{VaR}_\alpha} p_s \cdot J(\mathbf{x}, \omega_s)$$
4. **Distributionally-Robust Operational Objective**:
   $$J_{\text{robust}}(\mathbf{x}) = \mathbb{E}_\omega[J(\mathbf{x})] + \lambda \cdot \max\big(0, \text{CVaR}_{0.80}(\mathbf{x}) - \mathbb{E}_\omega[J(\mathbf{x})]\big)$$
   with risk aversion parameter $\lambda = 0.50$.

---

## 6. Constraint Taxonomy

### 6.1 Hard Constraints ($g_j(\mathbf{x}) \le 0$)
1. **Exactly-Once Mandatory Demand Fulfillment**:
   $$\sum_{v=1}^V \mathbb{I}(d_v = k) = 1, \quad \forall k \in \{1, \dots, K\}$$
2. **Vessel Deadweight Capacity**:
   $$m_v \le \text{DWT}_v, \quad \forall v \in \{1, \dots, V\}$$
3. **Vessel-Demand Family Compatibility**:
   $$\text{ClassFamily}(v) = \text{RequiredFamily}(d_v), \quad \forall v \text{ with } d_v \ne 0$$
4. **Engine-Fuel Technical Compatibility**:
   $$f_v \in \text{CompatibleFuels}(v), \quad \forall v \in \{1, \dots, V\}$$
5. **Safe Speed Envelopes**:
   $$v_{\min, v} \le s_v \le v_{\max, v}, \quad \forall v \in \{1, \dots, V\}$$

### 6.2 Soft Constraints / Objectives ($h_l(\mathbf{x})$)
1. **Voyage Deadline Breaches**: Penalized at $\$500/\text{hour}$ of delay.
2. **IMO Carbon Intensity Indicator (CII)**: Vessel must not drop below rating 'C'. Ratings 'D' and 'E' incur corrective action costs.
3. **FuelEU Maritime Compliance Deficit**: Incurs regulatory carbon surcharges.
