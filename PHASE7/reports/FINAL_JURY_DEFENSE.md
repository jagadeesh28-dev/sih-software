# PHASE 7 — STEP 35: HOSTILE SIH JURY ATTACK DEFENSE
## SIH26138 — Egreen Quanta
### 20 Rigorous Scientific & Engineering Answers Grounded in Concrete Empirical Artifacts

**Date:** September 19, 2026  
**Auditor:** Hostile SIH Jury Reviewer, Principal ML Engineer, Optimization Lead  
**Rule:** Every answer is backed by an auditable file, dataset, or experiment in the repository.

---

### Q1: Why quantum-inspired?
**Answer:** We evaluated quantum-inspired computing because the maritime fleet assignment and hydrodynamic feature-selection landscapes are non-convex, multimodal, and subject to severe combinatorial explosion. QIEA leverages continuous Q-bit probability amplitudes $[\alpha_i, \beta_i]^T$ and rotation gates ($U(\Delta\theta)$) to maintain superposition-like search state diversity, preventing premature convergence to local sub-optima.  
**Artifact:** `src/qi_prediction/qiea.py`, `PHASE6/results/figures/fig10_qi_population_entropy.png`.

---

### Q2: Why not classical GA?
**Answer:** We implemented and benchmarked a matched classical Genetic Algorithm control under identical evaluation budgets (150 evals, 10 population, 15 generations across 30 seeds). While QI-C1 and Classical GA achieved statistically indistinguishable test error ($237.96\text{ kg/h}$ vs $237.24\text{ kg/h}$, $p = 0.684$), QIEA preserved $+44.7\%$ higher population diversity ($0.2814$ vs $0.1945$), providing superior robustness against stagnation in complex non-stationary environments.  
**Artifact:** `PHASE6/results/statistical_comparison.csv`, `PHASE6/results/feature_stability.csv`.

---

### Q3: What did QI actually improve?
**Answer:** QI-C1 improved prediction accuracy over the frozen physics + ML baseline (`MODEL-REAL-04`), reducing test MAE from $246.97\text{ kg/h}$ to $237.96\text{ kg/h}$ ($-3.65\%$ error reduction) and increasing $R^2$ from $0.9501$ to $0.9530$, while eliminating 6 redundant and noisy environmental features. In Phase 5 fleet optimization, the quantum-inspired hybrid framework A5 restored fleet feasibility from $80\%$ to $100\%$ and expanded Pareto hypervolume by $+64.0\%$ over standard NSGA-III.  
**Artifact:** `PHASE6/results/qi_c1_results.csv`, `PHASE5_STATUS.md`.

---

### Q4: What did QI fail to improve?
**Answer:** QI-C1 did *not* outperform the matched classical GA control by a statistically significant margin ($p = 0.684$). Furthermore, candidate QI-C2 (MPS Tensor Network) completely failed to model continuous tabular telemetry, suffering catastrophic gradient divergence across $20/30$ random seeds. We do *not* claim quantum superiority.  
**Artifact:** `PHASE6/09_STATISTICAL_PROTOCOL.md`, `PHASE6/10_FAILURE_ANALYSIS.md`.

---

### Q5: Why did MPS fail?
**Answer:** Matrix Product States (MPS) were designed for discrete 1D lattice spin systems with localized quantum entanglement. Continuous tabular marine telemetry lacks 1D physical locality; cross-feature correlations between draft, speed, and waves create dense multi-body interactions that require exponential bond dimensions ($\chi \gg 64$). Unconstrained SGD training caused canonical gauge drift and explosive gradient explosions ($\text{MAE} > 10^{11}\text{ kg/h}$).  
**Artifact:** `src/qi_prediction/mps_predictor.py`, `PHASE6/results/qi_c2_results.csv`.

---

### Q6: Why did QPSO not become the final prediction engine?
**Answer:** In Phase 6, QPSO was evaluated for online hyperparameter optimization (HPO). While effective offline, running online stochastic particle swarms inside high-throughput real-time dispatch pipelines introduced non-deterministic latency spikes ($>65\text{ ms}$). Optimal hyperparameters were frozen into `production.yaml`, allowing QI-C1 to serve predictions in $<0.1\text{ ms}$ deterministically.  
**Artifact:** `PHASE6/results/runtime_provenance.csv`, `PHASE7/config/production.yaml`.

---

### Q7: What is the baseline?
**Answer:** The baseline is `MODEL-REAL-04`, an audited hybrid model combining theoretical naval architecture (first-principles Holtrop-Mennen calm water resistance, IMO STAwave-2 added wave resistance, and Blendermann wind drag) with a LightGBM ML residual learner trained on all 14 `CONFIG_REAL_A` features. It achieves $R^2 = 0.9501$, $\text{MAE} = 246.97\text{ kg/h}$, and $\text{MAPE} = 14.63\%$.  
**Artifact:** `PHASE6/config/baseline.yaml`, `PHASE7/model_registry.yaml`.

---

### Q8: Is the data real?
**Answer:** Yes. The dataset consists of real-world high-frequency sensor telemetry from the Danish Technical University (DTU) FuelCast maritime research initiative, recorded from direct onboard Coriolis mass-flow meters, GPS navigators, echo sounders, and anemometers over 604 commercial vessel-days.  
**Artifact:** `REAL_DATASET_FORENSIC_VERIFICATION.md`, `data/processed/real/fuelcast/`.

---

### Q9: How many records?
**Answer:** Exactly **173,986 raw records** were downloaded across three vessels. During Phase 2.3 data quality cleaning, exactly **12 trailing padding rows** containing null sensor timestamps (0 on Poseidon, 4 on Triton, 8 on Ceto) were removed, yielding an active **validated experimental sample size of 173,974 observations**.  
**Artifact:** `PHASE7/results/data_count_reconciliation.csv`.

---

### Q10: Why three vessels?
**Answer:** The three vessels represent structurally distinct commercial naval hull forms: `CPS_Poseidon` (large container ship, 105,422 rows), `CPS_Triton` (small feeder ship, 25,347 rows), and `OSS_Ceto` (handymax bulk/offshore vessel, 43,205 rows). This multi-hull diversity prevents models from overfitting to a single hydrodynamic hull profile.  
**Artifact:** `PHASE7/00_RELEASE_BASELINE.md`, `PHASE6/results/data_characterization.csv`.

---

### Q11: Does it generalize to unseen vessels?
**Answer:** No. Leave-One-Vessel-Out (LOVO) cross-validation demonstrated that zero-shot transfer to an unseen hull increases prediction error by $3.4\times\text{ to }5.2\times$ due to hull-specific block coefficients ($C_B$), wetted surface geometry, and engine curves. Vessel-specific calibration is mandatory.  
**Artifact:** `PHASE6/results/lovo_results.csv`, `PHASE6/08_VALIDATION_PROTOCOL.md`.

---

### Q12: What happens OOD?
**Answer:** The system executes a Mahalanobis / bounding-envelope domain check. If normalized envelope distance $>1.00$, the system enters `NEAR_BOUNDARY` mode and falls back to `MODEL-REAL-04`. If distance $>3.00$ (severe OOD), the prediction engine halts and safely rejects the input, while the optimizer applies a heavy mathematical penalty ($10,000\text{ kg/h}$).  
**Artifact:** `src/qi_prediction/serving.py`, `PHASE7/results/ood_guard_validation.csv`.

---

### Q13: What happens when the model fails?
**Answer:** The platform implements a safe 3-tier fallback architecture: if primary `QI-C1` fails or experiences an exception, execution seamlessly transitions to `MODEL-REAL-04`. If all ML components fail, execution falls back to first-principles theoretical physics (`PhysicsFuelPredictor`). Zero unhandled runtime exceptions leak to the operator.  
**Artifact:** `scripts/demo_scenarios.py` (DEMO 5), `PHASE7/results/failure_injection.csv`.

---

### Q14: What happens if telemetry is corrupted?
**Answer:** The immutable feature contract (`feature_contract.yaml`) enforces strict type and range constraints. Inputs with NaN, Inf, negative speeds, or impossible displacements are intercepted at the ingestion boundary and rejected (100% safe rejection rate across 1,000 automated stress tests).  
**Artifact:** `PHASE7/results/prediction_stress_tests.csv`.

---

### Q15: Is alternative-fuel prediction measured?
**Answer:** No. Real telemetry was measured exclusively on conventional marine fuels (VLSFO, MGO). Green fuels (bio-methanol, green ammonia, liquid hydrogen) are evaluated as **physics-based thermodynamic scenarios** derived from invariant mechanical shaft energy ($E_{shaft} = \int P_B dt$), empirical engine thermal efficiencies, and ISO Lower Heating Values. We explicitly forbid labeling scenario outputs as "experimentally validated".  
**Artifact:** `PHASE6/13_ALTERNATIVE_FUEL_SCENARIOS.md`, `configs/fuels.yaml`.

---

### Q16: What is actually novel?
**Answer:** Algorithmic novelty is strictly disclaimed (QIEA, QPSO, LightGBM, and DE are established literature methods). The novelty lies strictly in the **systems architecture and domain coupling**: (1) coupling naval architectural hydrodynamic resistance with quantum-inspired feature selection, (2) uncertainty-aware CVaR risk integration in fleet routing, and (3) multi-vessel open benchmark validation on real Coriolis telemetry.  
**Artifact:** `PHASE6/15_NOVELTY_AUDIT.md`, `PHASE7/FINAL_CLAIM_LEDGER.yaml`.

---

### Q17: Can you reproduce it?
**Answer:** Yes. Running a single command: `python reproduce_release.py` executes the entire 9-stage verification matrix (data check, model load, baseline, QI-C1, uncertainty, OOD, optimizer safety, end-to-end trace, and claim audit) in under 15 seconds.  
**Artifact:** `reproduce_release.py`, `scripts/reproduce_release.py`.

---

### Q18: Can another team run it?
**Answer:** Yes. The software contains zero hardcoded absolute Windows paths or developer-specific usernames. Dependencies are pinned in `requirements-lock.txt`, and standard installation instructions are provided in `RELEASE/INSTALL.md`.  
**Artifact:** `requirements-lock.txt`, `RELEASE/INSTALL.md`.

---

### Q19: What are the limitations?
**Answer:** Four primary limitations: (1) requires vessel-specific telemetry for calibration (zero-shot transfer fails), (2) green fuels are thermodynamic simulations, (3) continuous MPS tensor networks diverged, and (4) telemetry lacks high sea-state data ($H_s > 6\text{ m}$), requiring conservative uncertainty extrapolation in heavy storms.  
**Artifact:** `RELEASE/LIMITATIONS.md`, `PHASE6/14_LIMITATIONS_AND_BOUNDARIES.md`.

---

### Q20: What would invalidate your claims?
**Answer:** Our claims would be invalidated if: (1) an independent evaluation proved data leakage across chronological train/test splits, (2) the baseline code was shown to use SOG instead of STW, (3) alternative fuels were claimed to be direct sensor measurements, or (4) QIEA was claimed to provide "quantum supremacy". None of these conditions exist in Egreen Quanta.  
**Artifact:** `PHASE7/01_FINAL_CLAIM_AUDIT.md`, `PHASE7/FINAL_RELEASE_GATE.md`.
