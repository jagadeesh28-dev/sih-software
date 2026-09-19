# Phase 3.1 — Penalty Cliff Forensic Analysis

## 1. Mathematical Structure of the Penalty Cliff
The Phase 3 Fleet Optimization objective is formulated as:

$$J_{\text{total}}(x) = \sum_{k=1}^5 w_k \frac{f_k(x)}{s_k} + P_{\text{domain}}(x) + P_{\text{CII}}(x) + P_{\text{FuelEU}}(x)$$

Where:
- $w = [0.30, 0.30, 0.25, 0.10, 0.05]$
- $s = [50.0\text{ t}, 50,000\text{ USD}, 150.0\text{ t}, 10.0\text{ h}, 15.0\text{ t}]$
- $P_{\text{domain}} = 100,000 \times (1.0 + d_{\text{envelope}})$ if `status != VALID`
- $P_{\text{CII}} = 15,000$ if CII rating is 'E'
- $P_{\text{FuelEU}} = 2,500$ if non-compliant with FuelEU intensity targets.

## 2. Quantitative Dimensions of the Cliff

| State Description | Physical Normalized Score | Domain Penalty | CII Penalty | FuelEU Penalty | Total Objective |
|:---|:---:|:---:|:---:|:---:|:---:|
| Hypothetical Feasible State | ~3.06 | 0.0 | 0.0 | 0.0 | **~3.06** |
| Single-Voyage Cruise (CII E) | ~3.06 | 0.0 | 15,000.0 | 0.0 | **~15,003.06** |
| Actual Benchmark (Bio-Methanol) | **3.2758** | **100,000.0** | **15,000.0** | **0.0** | **115,003.28** |
| Actual Benchmark (VLSFO) | **1.8397** | **100,000.0** | **15,000.0** | **2,500.0** | **117,501.84** |

## 3. Impact on Optimization Dynamics
1. **Search Space Polarization:** Because VLSFO incurs $+2,500$ FuelEU penalty, all optimizers immediately fled VLSFO and adopted `bio_methanol`.
2. **Artificial Plateau:** For `bio_methanol`, every single state incurs $+115,000.00$.
3. **Loss of Gradient:** The physical objective accounts for only $0.0028\%$ of the total value.
4. **Floating-Point Differentiation:** Competitor comparisons (e.g. QPSO vs DE) were determined entirely by minute floating point variations ($10^{-7}$) around speed $18.59$ knots on top of an infeasible $115,000$ penalty block.
