# PHASE 3 FAILURE MODES & ADVERSARIAL RISK AUDIT
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Failure Mode & Effects Analysis (FMEA) for Optimization & Decision Support  
**Date:** 2026-09-12  
**Status:** FAILURE MODES CATALOG LOCKED  

---

## 1. Executive Summary & FMEA Methodology

Deploying black-box ML models into numerical optimization loops introduces severe vulnerability to **surrogate exploitation**: metaheuristic optimizers treat predictive surrogates not as physical representations, but as mathematical landscapes. Without defensive engineering, optimizers naturally exploit ungrounded regions of the surrogate where numerical artifacts create artificial "zero-fuel" or "negative-fuel" global minima.

This Failure Modes and Effects Analysis (FMEA) systematically categorizes every potential failure mode in the Phase 3 optimization and decision-support pipeline and specifies the exact architectural defense implemented to prevent it.

---

## 2. Failure Mode Catalog & Architectural Mitigations

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FAILURE MODES TAXONOMY                                         │
├─────────┬───────────────────────────────┬────────────┬─────────────┬─────────────────────────────┤
│ CODE    │ FAILURE MODE                  │ SEVERITY   │ PROBABILITY │ ARCHITECTURAL DEFENSE       │
├─────────┼───────────────────────────────┼────────────┼─────────────┼─────────────────────────────┤
│ FM-01   │ Surrogate Adversarial Trough  │ CRITICAL   │ HIGH        │ SafeFuelObjective Barrier   │
│ FM-02   │ QPSO Premature Swarm Collapse │ HIGH       │ MEDIUM      │ Adaptive Beta Schedule & RS │
│ FM-03   │ Dynamic Positioning Misclass. │ HIGH       │ HIGH        │ Mode-Aware Domain Checker   │
│ FM-04   │ Regulatory Conflation Error   │ HIGH       │ HIGH        │ Decoupled Compliance Engine │
│ FM-05   │ Methane Slip Unit Mismatch    │ CRITICAL   │ MEDIUM      │ Dimensional Mass Balance    │
│ FM-06   │ Unphysical Fuel Switching     │ MEDIUM     │ LOW         │ Engine Compatibility Matrix │
│ FM-07   │ Quantile Under-Coverage Risk  │ MEDIUM     │ HIGH        │ Risk Parameterization (λ)   │
│ FM-08   │ Boundary Sticking / Clumping  │ LOW        │ MEDIUM      │ Proximity Soft Repulsion    │
│ FM-09   │ Cross-Class Hull Collapse     │ CRITICAL   │ HIGH        │ Vessel-Class Envelopes      │
│ FM-10   │ Infeasible Cargo / Deadweight │ HIGH       │ MEDIUM      │ Hydrostatic Hard Constraint │
└─────────┴───────────────────────────────┴────────────┴─────────────┴─────────────────────────────┘
```

---

## 3. Detailed Failure Mode Analyses & Mitigations

### FM-01: Surrogate Adversarial Trough Exploitation
- **Mechanism**: The LightGBM tree ensemble predicts negative or near-zero fuel consumption in extrapolation regimes (e.g. commanding 30 kn speed at negative draft or hurricane waves). The metaheuristic discovers this trough and reports it as the "optimal green strategy."
- **Severity**: **`CRITICAL`** (Invalidates all optimization credibility).
- **Architectural Defense**:
  1. `DomainChecker` tests normalized distance $d_{\text{env}}$ to the P01–P99 training envelope.
  2. If candidate is `OUT_OF_DOMAIN` or `PHYSICALLY_INVALID`, `SafeFuelObjective` overrides the surrogate with a massive barrier penalty:
     $$F_{\text{penalized}} = 10,000 \times (1.0 + d_{\text{env}}) \quad \text{or} \quad 100,000\text{ kg/h}$$
  3. The optimizer immediately encounters a steep gradient repelling it from the ungrounded region.

### FM-02: QPSO Premature Swarm Collapse
- **Mechanism**: In multimodal landscape topologies, all particles cluster around a sub-optimal local attractor early in the search, causing the mean best position $mbest$ to freeze and diversity to collapse.
- **Severity**: **`HIGH`** (Sub-optimal recommendations).
- **Architectural Defense**:
  1. Linear contraction-expansion schedule: $\beta(t) = 1.0 - 0.5 \cdot (t / t_{\max})$ preserves exploratory variance in early generations.
  2. Multi-start seed replication across 30 independent runs ensures reproducibility.
  3. Comparative benchmark against Genetic Algorithm (with polynomial mutation diversity) and Differential Evolution.

### FM-03: Dynamic Positioning Misclassification on Offshore Vessels
- **Mechanism**: On `OSS_Ceto`, dynamic positioning requires delivering multi-megawatt thruster power while remaining stationary ($\text{STW} < 2\text{ kn}$). A naive kinematic rule ($\text{STW} < 2\text{ kn} \land P > 5\text{ MW} \implies \text{Impossible}$) rejected $93.85\%$ of valid real states in Phase 2.3.
- **Severity**: **`HIGH`** (Renders offshore vessel optimization impossible).
- **Architectural Defense**:
  1. Operating regime flags: $\text{Mode} \in \{\text{Transit}, \text{Maneuvering}, \text{DP}, \text{Port}\}$.
  2. `DomainChecker` adjusts physical plausibility checks based on operational mode: in `DP` mode, high power at low speed is certified as physically valid.

### FM-04: Regulatory Conflation & Mismatched Scopes
- **Mechanism**: Mixing Tank-to-Wake $\text{CO}_2$ (CII basis) with Well-to-Wake $\text{CO}_2\text{e}$ (FuelEU basis), or applying EU ETS carbon taxes to global international waters.
- **Severity**: **`HIGH`** (Regulatory misreporting and legal non-compliance).
- **Architectural Defense**:
  1. Strict modular decoupling into separate classes: `ImoCiiCalculator`, `FuelEuCalculator`, `EuEtsCalculator`.
  2. Mandatory declaration of geographical voyage scope ($\text{Scope}_{\text{EEA}} \in \{0.5, 1.0\}$) and verification status.

### FM-05: Methane Slip Dimensional Tracking Failure
- **Mechanism**: Methane has a 100-year GWP of $29.8$ (IPCC AR6). Omitting unburned methane mass or adding methane slip directly to $\text{CO}_2$ without GWP weighting distorts LNG decarbonization claims.
- **Severity**: **`CRITICAL`** (Incorrect green claims; LNG could falsely appear cleaner than biomethanol).
- **Architectural Defense**:
  1. Verified dimensional mass balance in `lca/methane_slip.py`:
     $$m_{\text{slip, kg}} = m_{\text{fuel, kg}} \times \sigma_{\text{slip}}$$
     $$\text{GHG}_{\text{slip, t CO}_2\text{e}} = \frac{m_{\text{slip, kg}} \times 29.8}{1000}$$
  2. Unit-tested against analytical hand calculations in `tests/test_emissions.py`.

### FM-06: Unphysical Alternative Fuel Assignment
- **Mechanism**: Assigning green ammonia or liquid hydrogen to a conventional two-stroke low-speed diesel engine without retrofitted fuel storage or selective catalytic reduction (SCR).
- **Severity**: **`MEDIUM`** (Engineering absurdity).
- **Architectural Defense**:
  1. Engine Compatibility Matrix in `configs/fuels.yaml`.
  2. Hard constraint $g_{\text{compat}}(\mathbf{x})$ rejects invalid fuel-vessel pairings before evaluation.

### FM-07: Quantile Dispersion Miscalibration Under Real Sensor Noise
- **Mechanism**: Nominal 90% prediction intervals achieved only $78.51\%$ coverage on real FuelCast telemetry. Treating $[q_{05}, q_{95}]$ as a $90\%$ certainty envelope under-represents tail risk.
- **Severity**: **`MEDIUM`** (Overconfident decision support).
- **Architectural Defense**:
  1. The risk metric is strictly labeled **Prediction Dispersion Proxy**, never "90% Confidence Interval".
  2. Robust objective sweeps $\lambda \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$ to test sensitivity to uncertainty aversion.

### FM-08: Swarm Clumping on Empirical Domain Boundaries
- **Mechanism**: When searching near the speed limit, particles may cluster exactly on the $V_{\max}$ boundary, causing high boundary variance.
- **Severity**: **`LOW`** (Minor convergence drag).
- **Architectural Defense**:
  1. Soft quadratic proximity penalty in the `NEAR_BOUNDARY` region (P01–P05 and P95–P99) gently biases solutions toward the interior of the well-sampled manifold.

### FM-09: Universal Fleet Extrapolation Failure
- **Mechanism**: Optimizing a container feeder or bulk carrier using a surrogate trained on `CPS_Poseidon` (70,000 GT cruise ship).
- **Severity**: **`CRITICAL`** (Falsified in Phase 2.3; LVO collapsed with $R^2 < 0$).
- **Architectural Defense**:
  1. Fleet profiles in `configs/fleet_profiles.yaml` bind each vessel to its certified class family.
  2. Surrogates refuse to evaluate vessels outside their designated class envelope.

### FM-10: Hydrostatic Deadweight & Displacement Overload
- **Mechanism**: Optimizer assigns cargo exceeding the vessel's deadweight, lowering per-ton emissions mathematically while sinking the vessel physically.
- **Severity**: **`HIGH`** (Unphysical transport work).
- **Architectural Defense**:
  1. Hard constraint: $m_{\text{cargo}} \le \text{Cap}_{\max}(v)$.
  2. Maximum displacement check: $\Delta = \Delta_{\text{light}} + m_{\text{cargo}} + m_{\text{bunker}} \le \Delta_{\max}$.
