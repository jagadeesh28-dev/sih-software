# Phase 5 Forensic Failure Analysis & Taxonomy
## SIH26138 — Egreen Quanta

---

## 1. The 10-Class Failure Taxonomy

Across all 330 optimization runs (11 algorithms $\times$ 30 seeds), every candidate and final solution was audited against the formal 10-class taxonomy:

| Taxonomy Class | Description & Failure Mode Criteria | Total Failures Observed Across Suite | Dominant Impacted Algorithms |
| :--- | :--- | :---: | :--- |
| **1. Assignment** | Duplicate demand assignment or unfulfilled mandatory demand | **40** | A0 (6), PSO (15), GA (8), NSGA3 (6), A3 (4), Random (1) |
| **2. Capacity** | Payload cargo exceeding vessel deadweight ($m_v > \text{DWT}_v$) | 0 | Protected by bounding & repair |
| **3. Fuel Compatibility** | Incompatible fuel burned (e.g. Ammonia on cruise ship) | 1 | GA (1) |
| **4. Schedule** | Severe involuntary speed loss causing arrival past deadline | 0 (as hard failure; soft penalty logged) | Present in early iterations |
| **5. Regulatory** | Non-compliance with IMO CII or FuelEU carbon intensity | 0 (penalties absorbed in OPEX) | Evaluated across all candidates |
| **6. Numerical** | Floating-point underflow, overflow, NaN, or Inf values | 0 | Zero numerical failures logged |
| **7. Stagnation** | Particle attractor radius shrinking below machine precision | 0 | Prevented by $\beta(t)$ schedule |
| **8. Decoder Failure** | Parser unable to unpack decision sub-vectors | 0 | Zero parsing errors |
| **9. Repair Failure** | Repair operator generating secondary invalid states | 0 | 100% valid repair executions |
| **10. Other** | Unclassified operational domain anomalies | 0 | None observed |

---

## 2. Forensic Analysis of the Four Phase 4 QPSO Failures

In Phase 4, Plain QPSO failed on four specific seeds: **1005, 1021, 1025, and 1029**. Our forensic evaluation traced the complete evaluation trajectory of each seed to uncover the exact physical and algorithmic mechanisms.

### 2.1 Seed 1021 Forensics
- **Final Decision State**: `CPS_Poseidon`: DEMAND-B, `CPS_Triton`: UNASSIGNED, `OSS_Ceto`: DEMAND-C.
- **Violation**: `Mandatory demand DEMAND-A is unfulfilled.`
- **Final Penalized Fitness**: $\$51,000.00$ (Physical: $\$1,000.00$, Penalty: $\$50,000.00$).
- **First Feasible Evaluation**: Occurred at evaluation **309** with fitness **$\$109,292.12$** (physical fuel: $148.2\text{t}$, but severe schedule delay under rough seas generated a $\$100,000+$ delay penalty).
- **The Penalty Inversion Trap**:
  Because $\$51,000.00 < \$109,292.12$, QPSO's scalar acceptance rule:
  $$\text{If } \text{fitness}(\mathbf{x}) < \text{fitness}(\mathbf{p}_{\text{best}}): \mathbf{p}_{\text{best}} \leftarrow \mathbf{x}$$
  chose the **infeasible candidate** over the feasible one!
- **Attractor Freezing**: $\mathbf{g}_{\text{best}}$ froze on the infeasible configuration at $\$51,000.00$. As the contraction coefficient $\beta(t)$ decayed toward 0.5, all 50 particles were pulled into the basin of the infeasible assignment, making escape mathematically impossible.

### 2.2 Seed 1025 Forensics
- **Final Decision State**: `CPS_Poseidon`: DEMAND-A, `CPS_Triton`: DEMAND-B, `OSS_Ceto`: UNASSIGNED.
- **Violation**: `Mandatory demand DEMAND-C is unfulfilled.`
- **Final Penalized Fitness**: $\$51,000.00$.
- **Best Feasible Evaluation**: Achieved at evaluation **1,929** with fitness **$\$56,681.84$**.
- **Trap Mechanism**: The feasible candidate was rejected because $\$51,000.00 < \$56,681.84$.

### 2.3 Seed 1029 Forensics
- **Final Decision State**: `CPS_Poseidon`: DEMAND-B, `CPS_Triton`: UNASSIGNED, `OSS_Ceto`: DEMAND-C.
- **Violation**: `Mandatory demand DEMAND-A is unfulfilled.`
- **Final Penalized Fitness**: $\$51,000.00$.
- **Best Feasible Evaluation**: Achieved at evaluation **2,499** with fitness **$\$118,335.27$**.
- **Trap Mechanism**: Again rejected in favor of the $\$51,000$ flat penalty attractor.

### 2.4 Seed 1005 Forensics
- In Phase 4 parallel execution, thread contention on global RNG state shifted initial sampling, trapping particle 12 in the unassigned demand attractor at evaluation 157.

---

## 3. How the Ablation Solutions Break the Trap

1. **A1 (Deb's Rule)**: Eliminates the trap by definition. Rule 1 dictates that any feasible solution ($v=0$) strictly defeats any infeasible solution ($v > 0$) regardless of objective magnitude. When evaluation 309 achieved feasible fitness $\$109,292.12$, Deb's rule forced $\mathbf{g}_{\text{best}}$ to accept it, permanently breaking the infeasible basin.
2. **A2 (Deterministic Repair)**: Eliminates the trap by preventing unassigned or duplicate demands from ever being evaluated. Repair maps the candidate to a feasible permutation before calling the evaluator.
3. **A5 (Full Hybrid QI)**: Combines conditional Q-bit demand observation (guaranteeing $\sum_v d_{v,k}=1$ probabilistically), repair projection, and Deb's selection, ensuring **0 failures across all 30 seeds**.
