# PHASE 4 MATHEMATICAL MODEL SPECIFICATION
## Egreen Quanta / SIH26138: Heterogeneous Fleet, Uncertainty-Aware & Scientifically Defensible Optimization

**Provenance**: `REAL_TELEMETRY_CALIBRATED` / `SYNTHETIC_OPERATIONAL_SCENARIO` / `SYNTHETIC_SCALABILITY_BENCHMARK`  
**Repository**: `sih26138_platform`  
**Date**: September 2026  

---

## 1. Mathematical Formulation Overview

Phase 4 defines a **mixed-integer, non-linear, simulation-grounded, multi-objective, distributionally robust fleet dispatch problem**. The optimizer determines vessel assignment, cargo allocation, transit speed, fuel pathway selection, operating mode, and shore power connection under environmental uncertainty and regulatory constraints.

---

## 2. Decision Vector Definition

For a fleet of $N_v$ vessels, the global decision vector $X \in \mathbb{R}^{6 N_v}$ is composed of vessel sub-vectors:

$$
X = \begin{bmatrix} x_1 & x_2 & \dots & x_{N_v} \end{bmatrix}^T
$$

where each vessel decision $x_i$ is a 6-dimensional tuple:

$$
x_i = \begin{bmatrix} a_i & c_i & v_i & f_i & m_i & s_i \end{bmatrix}
$$

### Variable Definitions & Domains:
1. **$a_i \in \{0, 1, \dots, N_d\}$**: Operational cargo demand assignment index (0 = unassigned / idle).
2. **$c_i \in [0, DWT_i]$**: Allocated cargo payload in metric tonnes.
3. **$v_i \in [v_{\min, i}, v_{\max, i}]$**: Commanded speed through water in knots.
4. **$f_i \in \{0, 1, 2, 3, 4\}$**: Fuel pathway index (0: VLSFO, 1: Fossil LNG, 2: Bio-methanol, 3: Green Ammonia, 4: Liquid Hydrogen).
5. **$m_i \in \{0, 1, 2, 3\}$**: Operational machinery mode (0: Transit, 1: Maneuvering, 2: Dynamic Positioning, 3: Port Idle).
6. **$s_i \in \{0, 1\}$**: Shore power cold-ironing connection at destination port (0: Inactive, 1: Active).

For the 3-vessel real benchmark ($N_v = 3$), the decision space dimension is **$D = 18$**.

---

## 3. Environmental Scenarios & Involuntary Speed Loss Kinematics

Let $\mathcal{S} = \{s_1, s_2, \dots, s_S\}$ represent the discrete set of environmental weather scenarios with prior probabilities $p_s \ge 0$, $\sum_{s=1}^S p_s = 1$.

Each scenario $s$ is characterized by:

$$
\mathbf{w}_s = \begin{bmatrix} H_{s, s} & T_{p, s} & V_{w, s} & \theta_{w, s} & V_{c, s} & \theta_{c, s} & d_{w, s} \end{bmatrix}^T
$$

where $H_s$ is significant wave height (m), $T_p$ is wave period (s), $V_w$ is wind speed (m/s), $V_c$ is current speed (m/s), and $d_w$ is water depth (m).

### Involuntary Speed Loss Model:
Added resistance from wind and irregular waves diminishes the actual speed over ground:

$$
v_{\text{act}, i, s} = v_i - \Delta v_{\text{wind}}(v_i, V_{w, s}, \theta_{w, s}) - \Delta v_{\text{wave}}(v_i, H_{s, s}, T_{p, s})
$$

subject to the physical lower bound $v_{\text{act}, i, s} \ge 0.1\text{ kn}$.

### Leg Transit Duration & Schedule Delay:
For assigned demand $k = a_i$ with voyage distance $D_k$ (nautical miles) and deadline $T_{\text{deadline}, k}$ (hours):

$$
T_{i, s} = \frac{D_k}{v_{\text{act}, i, s}}
$$

$$
\Delta T_{i, s} = \max\left(0, T_{i, s} - T_{\text{deadline}, k}\right)
$$

---

## 4. Surrogate-Grounded Fuel & Emissions Consumption

Every feasible operating state is routed to the vessel-specific, real-telemetry-calibrated `SafeFuelObjective`:

$$
\dot{m}_{\text{vlsfo}, i, s} = \mathcal{M}_i\left(v_{\text{act}, i, s}, \text{draft}_i, \text{disp}_i, \mathbf{w}_s\right) \quad [\text{kg/h}]
$$

For cruise vessels, hotel electrical load $P_{\text{hotel}, i}$ establishes a physical baseline auxiliary fuel floor:

$$
\dot{m}_{\text{fuel}, i, s} = \max\left(\dot{m}_{\text{vlsfo}, i, s}, P_{\text{hotel}, i} \times SFOC_{\text{aux}}\right)
$$

### Alternative Fuel Energy Equivalence:
When operating on alternative fuel $f_i$, the physical fuel mass consumption scales by lower heating value (LHV):

$$
M_{f, i, s} = \frac{\dot{m}_{\text{fuel}, i, s} \times T_{i, s}}{1000.0} \times \left(\frac{LHV_{\text{vlsfo}}}{LHV(f_i)}\right) \quad [\text{metric tonnes}]
$$

### Lifecycle Well-to-Wake (WtW) Emissions:
Using certified WtW greenhouse gas emission factors $EF_{\text{WtW}}(f_i)$ in $\text{gCO}_2\text{e/g fuel}$:

$$
E_{\text{WtW}, i, s} = M_{f, i, s} \times EF_{\text{WtW}}(f_i) \quad [\text{tonnes }\text{CO}_2\text{e}]
$$

---

## 5. Economic Cost Function Decomposition

Voyage operational expenditure ($C_{\text{OPEX}, i, s}$) comprises:

$$
C_{\text{OPEX}, i, s} = C_{\text{fuel}} + C_{\text{carbon}} + C_{\text{shore}} + C_{\text{delay}} + C_{\text{FuelEU}}
$$

1. **Fuel Cost**: $C_{\text{fuel}} = M_{f, i, s} \times P_{\text{fuel}}(f_i)$
2. **Carbon Cost**: $C_{\text{carbon}} = E_{\text{TtW}, i, s} \times P_{\text{carbon}}$ (baseline \$90/t $\text{CO}_2$)
3. **Shore Power Cold-Ironing**: $C_{\text{shore}} = \mathbb{I}(s_i = 1) \times P_{\text{hotel}, i} \times t_{\text{port}} \times P_{\text{elec}}$
4. **Demurrage / Delay Penalty**: $C_{\text{delay}} = \Delta T_{i, s} \times \$1,500/\text{hour}$
5. **FuelEU Non-Compliance Penalty**: Assessed via regulatory compliance balance.

---

## 6. Multi-Scenario CVaR Distributionally Robust Objective

For scenario $s$, the fleet normalized objective vector $\mathbf{J}_s \in \mathbb{R}^4$ is:

$$
\mathbf{J}_s = \begin{bmatrix}
\frac{\sum_i M_{f, i, s}}{S_{\text{fuel}}} &
\frac{\sum_i C_{\text{OPEX}, i, s}}{S_{\text{cost}}} &
\frac{\sum_i E_{\text{WtW}, i, s}}{S_{\text{ghg}}} &
\frac{\max_i \Delta T_{i, s}}{S_{\text{delay}}}
\end{bmatrix}^T
$$

The scalar scenario loss $L_s$ is:

$$
L_s = \mathbf{w}^T \mathbf{J}_s, \quad \mathbf{w} = [0.30, 0.30, 0.25, 0.15]^T
$$

### Conditional Value at Risk (CVaR):
With probability weights $p_s$, the expected loss is $E[L] = \sum_s p_s L_s$.

For risk confidence level $\alpha = 0.80$, Value at Risk ($\text{VaR}_\alpha$) is:

$$
\text{VaR}_\alpha = \min \left\{ l \in \mathbb{R} : \sum_{s: L_s \le l} p_s \ge \alpha \right\}
$$

Conditional Value at Risk ($\text{CVaR}_\alpha$) measures the expected loss in the worst $(1 - \alpha)$ tail:

$$
\text{CVaR}_\alpha = \frac{\sum_{s: L_s \ge \text{VaR}_\alpha} p_s L_s}{\sum_{s: L_s \ge \text{VaR}_\alpha} p_s}
$$

The operational weather risk dispersion metric is:

$$
R_\alpha = \max\left(0, \text{CVaR}_\alpha - E[L]\right)
$$

### Robust Objective Formulation:

$$
J_{\text{robust}} = E[L] + \lambda \cdot R_\alpha, \quad \lambda \in \{0.0, 0.25, 0.50, 1.00\}
$$

---

## 7. Constraints & Defensive Barrier Penalties

The optimization is subject to:

1. **Demand Mutual Exclusivity**:
   $$\sum_{i=1}^{N_v} \mathbb{I}(a_i = k) = 1 \quad \forall k \in \{1, \dots, N_d\}$$
   *Violation Penalty: $P_{\text{dup}} = 100,000 \times (\text{count} - 1)$, $P_{\text{unmet}} = 50,000$.*

2. **Deadweight Cargo Capacity**:
   $$c_i \le DWT_i \quad \forall i$$
   *Violation Penalty: $P_{\text{dwt}} = 100,000 + 100 \times (c_i - DWT_i)$.*

3. **Vessel-Demand Family Compatibility**:
   $$\text{Class}(i) \in \text{AuthorizedClasses}(a_i)$$
   *Violation Penalty: $P_{\text{compat}} = 100,000$.*

4. **Vessel-Fuel Pathway Compatibility**:
   $$f_i \in \mathcal{F}_i^{\text{compat}}$$
   *Violation Penalty: $P_{\text{fuel}} = 100,000$.*

5. **Safe Operating Domain Boundary**:
   $$\mathbf{x}_{\text{state}, i, s} \in \mathcal{D}_{\text{empirical}}$$
   *Out-of-domain barrier penalty: $P_{\text{OOD}} = 50,000$.*

### Total Master Objective:

$$
J_{\text{total}} = J_{\text{robust}} + \sum P_{\text{hard}} + \sum P_{\text{soft}}
$$
