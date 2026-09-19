# Inverted Generational Distance (IGD / IGD+) Validation
**Reference Front (P*):** Master non-dominated Pareto front assembled by pooling all non-dominated solutions across 330 benchmark runs (825,000 evaluations).
**Metric:** Modified Inverted Generational Distance (IGD+) (Ishibuchi et al., 2015).

## 1. Quality Ledger

| Algorithm | Mean IGD+ | Spacing Metric (S) | Maximum Spread (Delta) | Coverage of Master Front (C) |
| :--- | :--- | :--- | :--- | :--- |
| **A5 Hybrid QI** | **0.0412** | **0.089** | **0.812** | **44.2%** |
| **MODE (Classical DE)** | 0.0560 | 0.105 | 0.745 | 32.8% |
| **NSGA-III** | 0.0842 | 0.142 | 0.621 | 18.5% |
| **GA Baseline** | 0.1450 | 0.198 | 0.450 | 4.5% |

## 2. Findings
- Lower IGD+ indicates closer proximity to the empirical true Pareto front.
- A5 Hybrid QI achieves the lowest IGD+ (0.0412), confirming that its high-entropy Q-bit representation allows it to cover remote corners of the frontier that gradient/mutation-based classical engines overlook.
