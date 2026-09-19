# Frozen Scientific Benchmark Protocol: Canonical Option-D Architecture
**Frozen Date:** September 18, 2026
**Benchmark Authority:** SIH26138 Scientific Validation Gate
**Repository Root:** `sih26138_platform`

## 1. Canonical Algorithm Dictionary

```
========================================================================================================================
CANONICAL ALGORITHM INVENTORY (14 Mutually Exclusive Implementations)
========================================================================================================================
ID    Canonical Name              Representation                 Constraint Handling          Multi-Objective Engine
------------------------------------------------------------------------------------------------------------------------
A0    Plain QPSO                  Continuous Box (R^18)          Static Additive Penalty      None (Scalar)
A1    QPSO + Deb                  Continuous Box (R^18)          Deb Feasibility-First        None (Scalar)
A2    QPSO + Deb + Repair         Continuous Box (R^18)          Deb + C0 Hungarian Repair    None (Scalar)
A3    QPSO + Deb + Repair + Arch  Continuous Box (R^18)          Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
A4    Discrete QPSO               Classical Discrete (Perm)      Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
A5    Complete Hybrid QI          Multi-State Q-Bit + Cont QPSO  Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
A6    Q-Bit + Classical DE        Multi-State Q-Bit + Cont DE    Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
M08   Standard DE (Phase 4)       Continuous Box (R^18)          Static Additive Penalty      None (Scalar)
M09   Fair MODE (Operational)     Continuous Box (R^18)          Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
M10   Standard NSGA-III           Continuous Box (R^18)          Static Additive Penalty      Das-Dennis Ref Points
M11   Fair NSGA-III (Benchmark)   Continuous Box (R^18)          Deb + C0 Hungarian Repair    Bounded Epsilon-Pareto
M12   Canonical PSO               Continuous Box (R^18)          Static Additive Penalty      None (Scalar)
M13   Canonical GA                Real-Coded Chromosome          Static Additive Penalty      None (Scalar)
M14   Uniform Random Search       Uniform Random Sampling        Post-hoc Constraint Check    None (Scalar)
========================================================================================================================
```

## 2. Experimental Execution Protocol
1. **Instances:** Standard Heterogeneous Fleet Instance ($D=18$, 3 vessels $	imes$ 6 decision variables: demand, speed, fuel, shore power, cargo, draft).
2. **Seeds:** Exactly 30 matched random seeds (`1001` to `1030`).
3. **Budget:** Exactly 2,500 objective evaluations per run ($50 	ext{ pop} 	imes 50 	ext{ iterations}$).
4. **Evaluator:** Strict singleton [`CommonFleetEvaluator`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/evaluator/common_evaluator.py) wrapping calibrated GBDT residual models on real FuelCast data.
5. **Hypervolume Reference Point:** Fixed at $[500.0	ext{ tonnes}, \$500,000]$ for unnormalized Fuel vs OPEX, or $[1.2, 1.2, 1.2, 1.2, 1.2]$ for normalized 5D frontiers.
6. **Hardware:** AMD64 x86_64, Windows, single CPU thread per run.
