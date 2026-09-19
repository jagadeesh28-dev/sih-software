# Egreen Quanta (SIH26138): Complete Repository Inventory & Forensic Audit

**Auditor:** Independent Senior Scientific Validation Lead  
**Audit Standard:** Strict Scientific Integrity / Software Quality Standards (ISO/IEC 25010)  
**Date:** 18 September 2026  
**Scope:** 100% Repository Forensic Inventory of `sih26138_platform`

---

## 1. System Inventory by Architectural Subsystem

### 1.1 Data & Ingestion Subsystem (`data/`)
* **`data/ingestion.py`**: Ingests raw telemetry and noon reports. Enforces data cleaning, unit conversion, and physical range sanity filtering.
* **`data/schemas/__init__.py`**: Defines canonical schemas (`SensorRecord`, `VoyageProfile`, `FleetSpecification`). Prevents unvalidated type mutations.
* **`data/raw/` / `data/processed/`**: Stores FuelCast telemetry datasets.
  - *Dependencies:* `pandas`, `numpy`, `pydantic`.
  - *Randomness:* None (deterministic).
  - *Scientific Risk:* Low, provided time-series index ordering is preserved.

### 1.2 Hydrodynamic Physics Subsystem (`physics/`)
* **`physics/holtrop_mennen.py`**: Implements the 1982 Holtrop-Mennen empirical naval architecture power prediction equations (ITTC-78 standard resistance).
* **`physics/resistance_model.py`**: Computes total vessel resistance $R_T = R_F(1+k_1) + R_W + R_{AA} + \Delta R_{\text{wave}}$.
* **`physics/stawave2.py`**: Evaluates wave added resistance using Kwon / STAwave-2 transfer functions ($\Delta R \propto H_s^2$).
  - *Dependencies:* `numpy`, `scipy`.
  - *Randomness:* None.
  - *Scientific Risk:* Holtrop-Mennen was calibrated on displacement hulls; accuracy degrades on unconventional hull forms.

### 1.3 Machine Learning Residual Predictor (`prediction/`)
* **`prediction/residual_model.py`**: LightGBM gradient-boosted decision tree predicting $\Delta \dot{m}_f$ residuals over Holtrop-Mennen baseline.
* **`prediction/baseline_models.py`**: Pure naval physics benchmark and linear polynomial baselines.
* **`prediction/inference.py`**: Frozen inference wrapper with `SafeFuelObjective` barrier clamping.
  - *Dependencies:* `lightgbm`, `scikit-learn`, `numpy`.
  - *Randomness:* Seed-frozen during inference.
  - *Scientific Risk:* High risk if exposed to out-of-distribution (OOD) drafts or extreme storm speeds without physical barrier fallback.

### 1.4 Regulatory & Decarbonization Subsystem (`regulations/`, `lca/`)
* **`regulations/fueleu.py`**: Codifies statutory compliance under EU Regulation 2023/1805 ($89.336\text{ gCO}_2\text{e/MJ}$ target; €2,400/t deficit penalty).
* **`regulations/cii.py`**: Codifies IMO MARPOL Annex VI Reg 28 Carbon Intensity Indicator boundaries (ratings A through E).
* **`regulations/ets.py`**: Evaluates EU ETS maritime allowance liabilities based on market carbon pricing ($90.00/\text{tCO}_2$).
* **`lca/ttw.py` & `lca/wtw.py`**: Implements IMO 2024 Life-Cycle GHG Guidelines (MEPC.376(80)) covering Well-to-Tank and Tank-to-Wake ($CO_2, CH_4$ slip, $N_2O$).
  - *Dependencies:* Standard math.
  - *Randomness:* None.
  - *Scientific Risk:* Low, statutory formulas are directly audited against official legislative texts.

### 1.5 Optimization & Metaheuristic Subsystem (`optimization/`, `src/algorithms/`)
* **`optimization/common_evaluator.py` / `src/evaluator/common_evaluator.py`**: Canonical `evaluate(x)` interface ensuring bitwise fairness.
* **`optimization/constraints.py`**: Deb's feasibility-first pairwise comparison rules.
* **`optimization/repair.py` / `src/representation/repair.py`**: Deterministic C0 repair heuristic pipeline.
* **`optimization/pareto.py`**: Non-dominated sorting and bounded epsilon-archive manager.
* **`optimization/differential_evolution.py`**: Classical DE/rand/1/bin continuous search engine.
* **`optimization/qpso.py`**: Delta-potential well Quantum-Behaved Particle Swarm Optimization.
* **`optimization/nsga3.py`**: Reference-direction hyperplane multi-objective evolutionary algorithm.
* **`optimization/d_qpso.py`**: Mixed-variable coordinate-exchange QPSO (Lukemire et al., 2019).
* **`optimization/q_moead.py` / `optimization/moead.py`**: Subproblem decomposition multi-objective engines.
* **`src/representation/qbit_representation.py`**: Q-bit rotation gates, Dirichlet-Q vectors, and conditional demand sampling.
* **`src/algorithms/hybrid_qi.py`**: Candidate A5/QI-HFO integrated framework.
  - *Dependencies:* `numpy`, `pymoo` (for ref dirs).
  - *Randomness:* Fully controlled via explicit random seed passing.
  - *Scientific Risk:* High risk if repair is applied asymmetrically or penalty functions bleed into Deb comparators.

### 1.6 Scenarios & Climatological Subsystem (`scenarios/`)
* **`scenarios/weather.py`**: Four metocean environmental states ($\text{SCEN-W1}$ to $\text{SCEN-W4}$, significant wave height $0.5\text{ m}$ to $3.5\text{ m}$).
* **`optimization/cvar.py`**: Conditional Value-at-Risk ($\text{CVaR}_{0.80}$) tail-loss evaluator over scenario distributions.
  - *Dependencies:* `numpy`.
  - *Randomness:* Controlled scenario sampling.
  - *Scientific Risk:* Moderate; CVaR provides risk penalization, not absolute storm guarantees.

---

## 2. Forensic Code Anomaly & Risk Detection

| Forensic Check Item | Repository Status | Findings & Verification |
| :--- | :---: | :--- |
| **Evaluator Symmetry** | **PASSED** | Single common evaluator (`CommonFleetEvaluator`) called by all algorithms. No engine-specific evaluator logic. |
| **Repair Parity** | **PASSED** | `FleetSolutionRepairer` executes identically for all candidate vectors before evaluation. |
| **Unit Consistency** | **PASSED** | Verified conversion constants (knots $\to$ m/s: 0.514444; NM $\to$ km: 1.852; kg $\to$ tonnes: 1e-3). |
| **Seed Sequestration** | **PASSED** | All stochastic calls instantiate explicit random generators (`np.random.default_rng(seed)` or `seed` parameter). |
| **Data Leakage** | **PASSED** | Temporal split manifest (`07_REAL_SPLIT_MANIFEST.json`) enforces voyage-isolated holdouts. |
| **Constraint Validity** | **PASSED** | Hard physical bounds ($v_{\min} \le v \le v_{\max}$, $P \le \text{MCR}$) checked prior to cost calculation. |
| **Dead Code / Stubs** | **CLEAN** | All imported modules are actively executed in Phase 5 benchmarks. |
| **Hidden Defaults** | **AUDITED** | All hyperparameter settings ($\beta_{\text{start}}=0.9, \beta_{\text{end}}=0.4, F=0.8, CR=0.9$) are documented in configuration files. |
