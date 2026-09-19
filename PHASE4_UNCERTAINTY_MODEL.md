# PHASE 4 UNCERTAINTY & RISK MODEL SPECIFICATION
## Egreen Quanta / SIH26138: Heterogeneous Fleet, Uncertainty-Aware & Scientifically Defensible Optimization

**Provenance**: `REAL_TELEMETRY_CALIBRATED` / `SYNTHETIC_OPERATIONAL_SCENARIO`  
**Repository**: `sih26138_platform`  
**Date**: September 2026  

---

## 1. Environmental Uncertainty Architecture

Open-sea maritime transit is fundamentally stochastic due to dynamic metocean conditions. Traditional deterministic voyage planning assumes calm-water conditions ($H_s = 0, V_w = 0$), which severely underestimates fuel consumption, schedule delays, and greenhouse gas emissions.

Phase 4 introduces a **4-scenario environmental uncertainty model** where every candidate fleet strategy is evaluated across the complete joint distribution of wind, waves, and surface currents.

---

## 2. Weather Scenarios & Probability Distribution

The operational domain encompasses North Sea and Norwegian Coastal transit:

$$
\mathcal{S} = \{\text{SCEN-W1}, \text{SCEN-W2}, \text{SCEN-W3}, \text{SCEN-W4}\}
$$

| Scenario ID | Environmental Description | $H_s$ (m) | $T_p$ (s) | $V_w$ (m/s) | $\theta_w$ (deg) | $V_c$ (m/s) | $p_s$ | Epistemic Risk Domain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SCEN-W1`** | Calm Sea / Gentle Breeze | 1.0 | 5.5 | 4.0 | 45.0 | 0.2 | 0.35 | Core Valid Envelope |
| **`SCEN-W2`** | Moderate Sea / Fresh Breeze | 1.8 | 7.0 | 8.5 | 90.0 | 0.5 | 0.35 | Core Valid Envelope |
| **`SCEN-W3`** | Rough Sea / Strong Breeze | 2.6 | 8.2 | 12.0 | 180.0 | 0.7 | 0.20 | Near Domain Boundary |
| **`SCEN-W4`** | Severe Sea / Near Gale | 3.4 | 9.5 | 14.5 | 225.0 | 0.9 | 0.10 | Extreme Valid Boundary ($H_s \le 3.5\text{ m}$) |

### Scientific Domain Barrier:
The maximum significant wave height in `SCEN-W4` is $H_s = 3.4\text{ m}$. This explicitly honors the training boundary of the real-telemetry calibrated `DomainChecker` ($H_s \le 3.5\text{ m}$), preventing any synthetic extrapolation outside verified physical observations.

---

## 3. Involuntary Speed Loss Mechanics

Adverse weather impacts vessels via two coupled physical mechanisms:
1. **Direct Wind Resistance**: Aerodynamic drag on the vessel superstructure:
   $$R_{\text{wind}} = \frac{1}{2} \rho_{\text{air}} C_x(\theta_{\text{rel}}) A_{\text{trans}} V_{\text{rel}}^2$$
2. **Added Wave Resistance in Irregular Seas**: Second-order wave drift forces and ship motions:
   $$R_{\text{wave}} = 2 \rho_{\text{sea}} g \int_0^\infty S_{\zeta\zeta}(\omega) \left(\frac{R_{\text{aw}}(\omega)}{\zeta_a^2}\right) d\omega$$

The resulting actual speed $v_{\text{act}, i, s}$ decreases relative to the commanded speed $v_i$:

$$
v_{\text{act}, i, s} = v_i - \Delta v(v_i, H_{s, s}, V_{w, s})
$$

### Operational Consequences:
- **Duration Increase**: Transit time expands non-linearly: $T_{i, s} = \frac{D_k}{v_{\text{act}, i, s}}$.
- **Deadline Penalties**: If rough weather causes $T_{i, s} > T_{\text{deadline}}$, delay penalties accrue at \$1,500/hour.
- **Power Increase**: Maintaining higher speeds in rough seas increases shaft power exponentially ($P \propto v^3$), sharply inflating fuel consumption and WtW emissions.

---

## 4. Conditional Value at Risk (CVaR) Formulation

Rather than optimizing solely for expected performance ($E[L]$) or relying on symmetric variance penalties, Phase 4 utilizes **Conditional Value at Risk ($\text{CVaR}_\alpha$)** to govern asymmetric tail risk.

### Mathematical Derivation:
Let $L_s$ be the normalized composite loss in scenario $s$, and $p_s$ its probability.
Let the cumulative distribution function be:
$$F_L(l) = \sum_{s: L_s \le l} p_s$$

For risk confidence level $\alpha = 0.80$:
1. **Value at Risk ($\text{VaR}_{0.80}$)** is the 80th percentile threshold:
   $$\text{VaR}_{0.80} = \inf \{l \in \mathbb{R} : F_L(l) \ge 0.80\}$$
2. **Conditional Value at Risk ($\text{CVaR}_{0.80}$)** is the conditional expectation of loss exceeding $\text{VaR}_{0.80}$:
   $$\text{CVaR}_{0.80} = \frac{1}{1 - \alpha} \sum_{s: L_s \ge \text{VaR}_{0.80}} p_s L_s$$
3. **Tail Risk Dispersion Metric ($R_{0.80}$)** measures excess loss under adverse scenarios:
   $$R_{0.80} = \max\left(0, \text{CVaR}_{0.80} - E[L]\right)$$

### Robust Objective Function:
The risk-adjusted robust objective is:

$$
J_{\text{robust}}(\lambda) = E[L] + \lambda \cdot R_{0.80}
$$

The risk-aversion coefficient is evaluated across:
$$\lambda \in \{0.0, 0.25, 0.50, 1.00\}$$
- $\lambda = 0.0$: Risk-neutral (pure expected loss minimization).
- $\lambda = 0.50$: Balanced operational planning (baseline).
- $\lambda = 1.00$: Conservative weather-averse planning (prioritizing schedule and fuel predictability in severe seas).
