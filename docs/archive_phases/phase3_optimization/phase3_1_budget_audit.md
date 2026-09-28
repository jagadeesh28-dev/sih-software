# Phase 3.1 — Evaluation Budget Audit (2,500 vs 50,000)

## Questions and Forensic Audit Answers

### A. Why was 2,500 evaluations used instead of 50,000?
- **Computational Cost:** Benchmarking revealed that each individual chromosome evaluation through `FleetEvaluationEngine` requires **33.41 ms** (approx. 30 evaluations/second).
- This latency is driven by executing pure-Python predictive inference:
  1. Feature formatting & DataFrame instantiation (~0.5 ms)
  2. LightGBM ML inference (~2 ms)
  3. Three LightGBM quantile regression predictions (~6 ms)
  4. First-principles Holtrop-Mennen physics evaluation (~5 ms)
  5. Multi-dimensional domain envelope distance calculation (~2 ms)
  6. Kinematic involuntary speed loss, emissions, costs, and regulatory accounting (~15 ms).
- At **33.41 ms/eval**:
  - 2,500 evaluations = **83.5 seconds per run**. For 150 benchmark runs (30 seeds x 5 optimizers), total compute was **3.48 hours**.
  - 50,000 evaluations = **1,670 seconds (27.8 minutes) per run**. For 150 runs, total compute would require **69.5 hours (~3 days)** of non-stop CPU execution.
- Therefore, $N_{\text{eval}} = 2,500$ was used as an engineering compromise.

### B. Was 2,500 documented as a fast/regression tier?
- Yes, in `PHASE3_BENCHMARK_PROTOCOL.md`, Section 4 defined standard vs gold-standard tiers. However, the report did not clearly label the 30-seed benchmark as a reduced evaluation tier.

### C. Did all algorithms receive exactly the same evaluation budget?
- **Yes.** Every optimizer (QPSO, Canonical PSO, GA, DE, Random Search) evaluated exactly 2,500 objective queries per run:
  - DE: 50 population x 50 generations = 2,500 evals.
  - GA: 50 population x 50 generations = 2,500 evals.
  - PSO: 50 particles x 50 iterations = 2,500 evals.
  - QPSO: 50 particles x 50 iterations = 2,500 evals.
  - Random Search: exact budget loop = 2,500 evals.

### D. Were initialization evaluations counted consistently?
- **Yes.** Initialization of the population (50 candidates) was included as generation/iteration 0 in the 2,500 budget.

### E. Did invalid candidates count as evaluations?
- **Yes.** When a candidate violated domain bounds or physical constraints, it was fully evaluated through `SafeFuelObjective` and `FleetConstraintManager`, returning the penalized objective and consuming 1 evaluation.

### F. Did repair operations cause hidden evaluations?
- **No.** Projection and boundary clipping were performed in parameter space prior to querying `eval_fn()`.

### G. Does iteration x population equal actual evaluations?
- **Yes.** $50 \times 50 = 2,500$ evaluations exactly across all population-based metaheuristics.
