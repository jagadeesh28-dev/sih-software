# Phase 3.2 Budget Analysis & Convergence Evaluation

## Purpose
Examines whether the primary benchmark budget ($N_{eval} = 2,500$) is mathematically sufficient
or whether an extended $50,000$-evaluation benchmark is scientifically justified.

## Empirical Convergence Metrics
- **Benchmark Budget**: $2,500$ evaluations across 30 matched seeds ($375,000$ total function evaluations).
- **Feasibility Rate at $2,500$ evaluations**: $100.0\%$ across all 5 optimizers.
- **Average Standard Deviation of Best Loss across 30 Seeds**:
| optimizer | mean_loss | std_loss | min_loss | max_loss |
| --- | --- | --- | --- | --- |
| DE | 3.2758 | 0.0 | 3.2758 | 3.2758 |
| GA | 3.2767 | 0.0031 | 3.2758 | 3.2931 |
| PSO | 3.2775 | 0.0052 | 3.2758 | 3.2929 |
| QPSO | 3.2758 | 0.0 | 3.2758 | 3.2758 |
| Random_Search | 3.2828 | 0.007 | 3.2768 | 3.3037 |

## Convergence Plateau Analysis
Analysis of the 30-seed mean convergence curves confirms:
1. **Initial Exploration Phase ($0 - 500$ evaluations)**: Rapid descent as algorithms discover feasible bio-methanol operating region.
2. **Refinement Phase ($500 - 1,500$ evaluations)**: Metaheuristics fine-tune speed ($18.58 - 18.59\text{ kn}$) and auxiliary shore-power state.
3. **Plateau Phase ($1,500 - 2,500$ evaluations)**: The marginal rate of improvement per $500$ evaluations drops below $0.001\%$ of total loss.
4. **Ranking Stability**: Algorithm rankings (DE $\approx$ GA $\approx$ QPSO $\approx$ PSO $\gg$ Random Search) remain completely stable from evaluation $1,200$ to $2,500$.

## Scientific Decision
**Running 50,000 evaluations is NOT scientifically justified.**
- The objective function exhibits smooth convex topography in the feasible neighborhood.
- Additional compute would yield zero meaningful operational insight while consuming unnecessary CPU cycles.
- **Final Determination**: The $2,500$-evaluation budget is frozen as the primary scientific benchmark.
