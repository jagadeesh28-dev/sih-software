# Discrete & Mixed-Variable d-QPSO Benchmark
**Algorithm:** Discrete Quantum-Behaved Particle Swarm Optimization (d-QPSO)
**Mechanism:** Probability transition matrices and angle-based categorical projection.

## 1. Performance Results (Seeds 1001–1030)

| Algorithm | Feasibility Rate | Mean Penalized Objective | Physical Objective | Runtime (s) |
| :--- | :--- | :--- | :--- | :--- |
| **A3 (Discrete QPSO)** | 86.67% | ,802.94$ | .27$ | 3.255s |
| **d-QPSO (Mixed-Variable)** | 90.00% | ,120.40$ | .40$ | 3.820s |
| **A1 (QPSO + Deb)** | **100.0%** | **,003.35$** | **.35$** | **2.319s** |

## 2. Key Takeaways
- While d-QPSO outperforms naive continuous rounding (86.7% vs 90.0%), it remains susceptible to categorical deadlock on assignment constraints without explicit repair or Deb feasibility-first selection.
- d-QPSO alone does not achieve 100% feasibility.
