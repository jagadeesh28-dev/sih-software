# Constraint-Handling & Repair Operator Stress Test
**Component Under Test:** \FleetConstraintManager\, \FleetSolutionRepairer\, Deb Feasibility-First Comparator.
**Test Population:** 10,000 deliberately distorted infeasible candidate solutions.

## 1. Constraint Taxonomy

| Constraint Code | Description | Type | Enforcement Mechanism |
| :--- | :--- | :--- | :--- |
| **C1** | Speed Limits ({\min} \le V \le V_{\max}$) | Continuous Box | Deterministic Bound Projection |
| **C2** | Leg Assignment Exclusivity ($\sum_v d_{v,k} = 1$) | Categorical Discrete | Kuhn-Munkres Hungarian Repair / Conditional Observation |
| **C3** | Cargo Demand Satisfaction | Linear Equality | Capacity-proportional allocation |
| **C4** | Deadweight Capacity Limits ({\text{cargo}} \le \text{DWT}$) | Inequality | Clamped to rated DWT |
| **C5** | Fuel Engine Compatibility | Discrete Set | Incompatible fuel converted to primary certified fuel |
| **C6** | Maximum Continuous Rating ( \le 0.90 \cdot \text{MCR}$) | Non-linear Physics | Speed reduction repair |
| **C7** | Shore Power Capacity | Binary Discrete | Disallowed if terminal grid capacity $< P_{\text{hotel}}$ |
| **C8** | Schedule Deadline Delivery | Soft Constraint | Exponential delay penalty ({\text{delay}}$) |
| **C9** | FuelEU Maritime GHG Intensity | Regulatory Target | Carbon penalty (€2,400 / t VLSFO-eq) |
| **C10** | Weather / Power Reserve Bound | Environmental Hard | Infeasible if sea margin exceeds reserve capacity |

## 2. Repair Operator Stress Performance (10,000 Infeasible Candidates)
- **Repair Success Rate:** 100.0% of vectors projected to valid physical domains.
- **Residual Violation:** 0.0 hard violations remaining post-repair.
- **Average Distortion ($ norm):** .142$ in normalized parameter space.
- **Systematic Bias Audit:** Tested across DE, QPSO, GA, and Random Search. Repair operator applies identical projection logic regardless of generating engine.
