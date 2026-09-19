# Slide 7: Fleet-Level Multi-Objective Optimization

## Fleet Scheduling Problem Formulation
- **Fleet Scope**: 3 Heterogeneous Commercial Vessels (*CPS_Poseidon*, *CPS_Triton*, *OSS_Ceto*) traversing multi-leg voyages under strict port arrival deadlines.
- **Decision Variables**: Speed per leg, arrival time windows, cargo distribution, and bunker selection.
- **Constraints**: Engine operating envelope, draft limits, and port contractual laytime windows.

---

## The Frozen Optimization Benchmark (825,000 Evaluations)

| Optimization Algorithm | Best Scalar Objective (Tonnes) | Feasibility Rate | Pareto Hypervolume | Spacing Metric | Diversity Entropy ($H$) |
|:-----------------------|:-------------------------------|:-----------------|:-------------------|:---------------|:------------------------|
| **Differential Evolution (DE)** | **$873.2265$** (Best Scalar) | **$100.0\%$** | $0.842 \pm 0.012$ | $0.038$ | $0.1982$ |
| **Classical GA** | $879.4510 \pm 4.22$ | $100.0\%$ | $0.835 \pm 0.015$ | $0.042$ | $0.2104$ |
| **Classical PSO** | $891.1204 \pm 8.45$ | $98.4\%$ | $0.812 \pm 0.021$ | $0.055$ | $0.1650$ |
| **QPSO** | $874.1520 \pm 3.10$ | **$100.0\%$** | **$0.865 \pm 0.010$** | **$0.029$** | **$0.2814$** |
| **Random Search** | $2,450.8000 \pm 142.0$ | $12.3\%$ | $0.210 \pm 0.050$ | $0.240$ | $0.3400$ |

---

## Critical Optimality Distinction: The Penalty Gap
> **Scientific Requirement**: "The penalized objective incorporates a large schedule-feasibility penalty; therefore its optimum must not be interpreted as the pure physical fuel minimum."

- **Penalized Objective Optimum**: $J^*_{\text{pen}} \approx \mathbf{873.2265\text{ tonnes}}$
  - **Actual Physical Fuel Consumed**: $\approx \mathbf{3.7861\text{ tonnes}}$
  - **Contractual Schedule Penalty**: $\approx \mathbf{869.4404\text{ tonnes fuel-equivalent}}$
- **Pure Physical Grid Minimum (Unconstrained / No Deadlines)**: $\approx \mathbf{3.2369\text{ tonnes}}$
- **Engineering Verdict**: Differential Evolution provides a strong scalar benchmark; QPSO yields superior Pareto coverage. The non-zero penalty gap is rigorously documented.
