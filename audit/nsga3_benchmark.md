# NSGA-III Multi-Objective Baseline Benchmark
**Algorithm:** Reference-Point-Based Non-Dominated Sorting Genetic Algorithm III (Deb & Jain, 2014)
**Reference Points:** Das-Dennis structured reference points across 5 objectives (Fuel, OPEX, GHG, Delay, CVaR).

## 1. Multi-Objective Metric Comparison

| Algorithm | Feasibility | Hypervolume (^6$) | IGD+ | Spacing ($) | Spread ($\Delta$) | Runtime (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NSGA-III** | 80.0% | .67$ | .0842$ | .142$ | .621$ | **0.878s** |
| **A5 Hybrid QI** | **100.0%** | **.11$** | **.0412$** | **.089$** | **.812$** | 7.514s |
| **Classical MODE** | 100.0% | .45$ | .0560$ | .105$ | .745$ | 1.706s |

## 2. Evaluation Assessment
- **Speed:** NSGA-III is the fastest multi-objective solver (0.878s), but exhibits poor feasibility (80.0%) when unassisted by Hungarian repair operators.
- **Hypervolume Gap:** A5 discovers deeper boundary compromise points across trade-offs (yielding +64.0% HV over NSGA-III), justifying the retention of QI as an offline exploration engine.
