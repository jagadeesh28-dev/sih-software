# AUDIT #12: IMPLEMENTATION FORENSICS & CODE LEAK AUDIT
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §16 Implementation Forensics & Code Sanity  
**Auditors:** Scientific Validation Engineer & Senior Software Architect  
**Date:** September 15, 2026  

---

## 1. Code Forensics Scope & Methodology

A rigorous forensic code scan was executed across all modules in `src/`, `optimization/`, and `experiments/` to detect potential methodological flaws, including:
1. Seed leakage or fixed random seed contamination.
2. Oracle leakage (using known optimal coordinates to guide search).
3. Benchmark-specific "if seed == X" hardcoded branches.
4. Accidental repair decoder leakage into baseline algorithms (A0, A1, A3, DE, PSO, GA).
5. Asymmetric evaluation budget consumption or evaluation caching.
6. Shared mutable state across algorithm runs.

---

## 2. Component-by-Component Code Audits

### 2.1 Baseline Algorithms Integrity
- **A0 (Plain QPSO, `src/algorithms/qpso.py`):**  
  Scanned for `FleetSolutionRepairer` or `repair_vector`. **Result: 0 occurrences.** A0 executes canonical continuous Delta-potential QPSO with raw floating-point bounds clipping.
- **A1 (QPSO + Deb, `src/algorithms/qpso_deb.py`):**  
  Scanned for repair operators or discrete transitions. **Result: 0 occurrences.** A1 differs from A0 strictly through the invocation of `CommonFleetEvaluator.deb_prefers()` during the $p_{\text{best}}$ and $g_{\text{best}}$ update step.
- **A2 (QPSO + Decoder, `src/algorithms/qpso_decoder.py`):**  
  Invokes `self.repairer.repair_vector(X[i])` prior to evaluation, as mandated by the A2 ablation definition.
- **A3 (Discrete QPSO, `src/algorithms/discrete_qpso.py`):**  
  Scanned for Deb comparator or repair operators. **Result: 0 occurrences.** A3 updates discrete categorical dimensions using CPMPSO velocity/probability matrices.
- **A4 (Heterogeneous QI, `src/algorithms/hybrid_qi.py`):**  
  Uses Q-bit rotation gates and Dirichlet quantum vectors. Scanned for Deb comparator or repair. **Result: 0 occurrences.** Evaluates strictly via additive scalar penalty.
- **Classical Baselines (`de.py`, `pso.py`, `ga.py`, `random_search.py`):**  
  Zero repair decoders; zero Deb feasibility rules. All classical baselines minimize standard penalized scalar fitness.

### 2.2 Oracle & Hardcoded Branching Scan
Searched for keywords `oracle`, `optimal`, `target_speed`, `if seed ==`, `elif seed ==`:
- **Result:** **Zero hardcoded branching found.**
- All algorithms initialize particles/vectors uniformly between `xl` and `xu` via `rng.uniform(xl, xu)`.
- No algorithm utilizes pre-seeded or warm-started solutions from previous runs.

### 2.3 Evaluation Budget Enforcement
All algorithms inherit from `BaseFleetOptimizer` and evaluate candidates strictly through:
```python
out = evaluator.evaluate(X[i])
```
The loop termination check:
```python
if evaluator.evaluation_count >= eval_cap:
    break
```
is enforced on every particle evaluation, ensuring that no algorithm ever exceeds the 2,500 physical evaluation ceiling.

---

## 3. Shared State & Memory Isolation
- No global variables store intermediate search states across runs.
- `CommonFleetEvaluator` is newly constructed for every single seed in `runner.py`:
  ```python
  comm_eval = CommonFleetEvaluator(evaluator, max_budget=budget)
  ```
- Random number generation is scoped per optimizer instance:
  ```python
  rng = np.random.RandomState(seed)
  ```

---

## 4. Audit Verdict: PASS
The codebase is clean, completely modular, and free of cheat-branches, oracle leaks, or accidental operator cross-contamination.
