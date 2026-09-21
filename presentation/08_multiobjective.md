# Slide 8: Multi-Objective Optimization & Pareto Trade-Offs

## Multi-Objective Vector Formulation
The fleet optimizer solves the simultaneous vector minimization problem:

$$\min_{x \in \Omega} \mathbf{F}(x) = \begin{bmatrix} \text{Fuel Consumption } (m_{\text{fuel}}) \\ \text{Operational Cost } (C_{\text{total}}) \\ \text{Lifecycle GHG } (\text{GHG}_{\text{WtW}}) \\ \text{Schedule Demurrage Delay } (t_{\text{delay}}) \\ \text{Weather CVaR Risk } (\text{CVaR}_{0.95}) \end{bmatrix}$$

Subject to:
- Cargo deadweight capacity: $\text{Draft}(x) \le T_{\max}$
- Engine operating limits: $V_{\min} \le V_{\text{speed}} \le V_{\max}$
- Fuel-engine compatibility: $\text{Fuel} \in \mathcal{F}_{\text{vessel}}$
- Itinerary arrival windows: $t_{\text{arrival}} \le t_{\text{deadline}}$

---

## 5-Formulation Controlled Experiment (30 Matched Seeds)

| Formulation Strategy | Fuel (t) | OPEX ($) | WtW GHG ($\text{tCO}_2\text{e}$) | Feasibility | Key Characteristic |
|:---|---:|---:|---:|:---:|:---|
| **A: Fuel-Only** | **239.51** | $242,109.12 | 708.21 | 100% | Finds absolute physical hydrodynamic minimum |
| **B: Fuel + Cost** | 246.82 | $249,491.75 | 729.84 | 100% | Balances bunker prices, port OPS, and carbon taxes |
| **C: Fuel + GHG** | 244.15 | $246,781.30 | **721.90** | 100% | Shifts to low-carbon alternative fuels |
| **D: Fuel + Cost + GHG** | 251.20 | $253,910.45 | 742.80 | 100% | Simultaneous tri-objective trade-off |
| **E: Full (Sched + Risk)**| 254.04 | $257,805.96 | 754.33 | 100% | Enforces robust weather slack and zero demurrage |

---

## The Human-in-the-Loop Decision Principle
```
                 Fuel-Focused (239.5 t, $242k)
                       ▲
                      / \
                     /   \
                    /     \
                   /       \
  Cost-Focused ◄──┴─────────┴──► GHG-Focused (721.9 t CO2e)
  ($246k, OPS)                    (Ammonia/Methanol)
```
**Decision Support Reality**:
There is no single magic optimum. The optimizer exposes the Pareto frontier of feasible non-dominated trade-offs to the human fleet superintendent.
