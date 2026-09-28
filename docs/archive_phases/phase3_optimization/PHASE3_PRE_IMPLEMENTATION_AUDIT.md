# PHASE 3 PRE-IMPLEMENTATION AUDIT
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Phase 3 Pre-Implementation Verification & Scientific Audit  
**Author:** Lead Scientific Software Architect, Maritime Optimization Researcher, ML Engineer & Adversarial Validation Engineer  
**Date:** 2026-09-12  
**Repository State:** Commit `20309b214b9540a7363b7365e442a222cd9c49a1` (70/70 Tests Passing)  

---

## 1. Executive Summary & Audit Purpose

Before a single line of Phase 3 optimization code is authored, this self-audit evaluates the exact boundary between **what is scientifically proven**, **what is empirically grounded**, and **what remains an unvalidated assumption**.

Phase 2.3 established a **`CONDITIONAL PASS FOR PHASE 3`**. This audit dissects that verdict to ensure that the fleet optimization engine does not optimize unphysical states, exploit uncalibrated uncertainty, or extrapolate across unsupported vessel classes.

---

## 2. Answers to the 10 Mandatory Pre-Implementation Questions

### Q1: What is already scientifically validated?
1. **Target Provenance on Real Telemetry (PASS)**: Verified that FuelCast `Consumer_Total_MomentaryFuel` derives from dual KROHNE OPTIMASS Coriolis mass-flow meters ($\dot{m}_{\text{inlet}} - \dot{m}_{\text{outlet}}$) measuring true inertial mass flow in $\text{kg/s}$ (converted to $\text{kg/h}$ via $\times 3600$). Zero circularity; zero reconstruction from shaft power.
2. **Hydrodynamic Prediction Without Machinery Telemetry (PASS)**: Verified on 173,974 clean real-world commercial ship records that `CONFIG-REAL-A` (STW, SOG, draft, displacement, wind, waves, current, water depth) captures **94.00% of fuel variance ($R^2 = 0.9400$, $\text{MAE} = 263.91\text{ kg/h}$)** on held-out chronological test sets.
3. **Hybrid Physics + ML Residual Superiority (PASS)**: Verified that `MODEL-REAL-04` (Holtrop-Mennen resistance + LightGBM residual with $\alpha=1.0$) statistically outperforms pure ML ($p = 7.45 \times 10^{-18}$, Wilcoxon signed-rank), achieving fleet-best **$\text{MAE} = 246.97\text{ kg/h}$ ($14.63\%$ MAPE) and $R^2 = 0.9501$**.
4. **Metocean Feature Contribution (PASS)**: Verified that wave and wind features provide genuine predictive signal. Removing waves degrades RMSE by $+29.57\text{ kg/h}$ ($+7.2\%$).
5. **Acoustic Doppler Log Vector Closure (PASS)**: Verified that Doppler log STW and GPS SOG / ocean current satisfy $\vec{V}_{\text{water}} = \vec{V}_{\text{ground}} - \vec{V}_{\text{current}}$ with $r = 0.9980$, bias $-0.007\text{ kn}$, and RMSE $0.297\text{ kn}$ on `CPS_Poseidon`.
6. **Defensive Boundary Interception (PASS)**: Verified that `SafeFuelObjective` successfully repelled 8 out of 8 deliberate adversarial exploits (negative power, ungrounded high speed at zero power, impossible draft, hurricane seas).

### Q2: What is NOT validated?
1. **Zero-Shot Synthetic-to-Real Transfer (FALSIFIED / FAILED)**: Direct transfer of synthetic-trained LightGBM to real ship telemetry failed catastrophically ($R^2 = -0.9447$, $\text{MAE} = 2,028.51\text{ kg/h}$, Bias = $-2,027.19\text{ kg/h}$). Synthetic models cannot predict real ships zero-shot.
2. **Universal Cross-Class Leave-Vessel-Out (FALSIFIED / FAILED)**: LVO across disparate vessel typologies (70k GT cruise vs 11k GT small cruise vs 24k GT offshore supply) collapsed ($R^2 < 0$ on all 3 folds). A model trained on cruise vessels cannot predict an offshore vessel.
3. **Uncertainty Calibration on Real Noise (MISCALIBRATED / UNDER-COVERING)**: Nominal 90% pinball loss prediction intervals $[q_{05}, q_{95}]$ achieved only **$78.51\%$ empirical PICP** on real test telemetry.
4. **Universal Kinematic Rules across Operational Modes (FALSIFIED)**: The rule $\text{STW} < 2\text{ kn} \land P > 5\text{ MW} \implies \text{Impossible}$ falsely rejected $93.85\%$ of legitimate operational states on `OSS_Ceto` during Dynamic Positioning (DP) station-keeping.
5. **Fleet-Wide Real-World Savings (UNPROVEN)**: Optimization has not yet been executed or validated on physical ships. Any claimed fuel or emissions savings remain in silico computational benchmarks.
6. **Quantum Advantage (UNPROVEN / PROHIBITED)**: QPSO is a classical pseudo-quantum heuristic running on von Neumann CPU cores. No quantum hardware or quantum speedup exists.

### Q3: What assumptions are required for Phase 3?
1. **Quasi-Steady Operational Legs**: The voyage can be discretized into operational legs where average speed, weather, and draft are stationary.
2. **Linear Energy-Specific Fuel Conversion**: Alternative fuel mass requirements scale inversely with Lower Heating Value ($\text{LHV}$) adjusted for engine thermal efficiency $\eta_{\text{thermal}}$.
3. **Additive Well-to-Wake Accounting**: Lifecycle emissions equal Well-to-Tank (upstream extraction, synthesis, distribution) plus Tank-to-Wake (combustion and fugitive slip).
4. **Vessel-Class Domain Bounding**: Each vessel belongs to a specific vessel class family with an independent empirical operating envelope fitted on training data.
5. **Fuel Availability & Engine Compatibility**: Alternative fuels can only be assigned to vessels equipped with compatible dual-fuel engines or retrofitted storage tanks.

### Q4: Which assumptions are dangerous?
1. **DANGEROUS: Assuming $F \to 0$ as $V \to 0$**: Cruise vessels burn $1,200 - 2,800\text{ kg/h}$ at zero speed for hoteling, HVAC, and galley operations. Assuming zero baseline fuel leads to unrealistically low fuel estimates for port/maneuvering periods.
2. **DANGEROUS: Mixing Cruise, Cargo, and Offshore in One Surrogate**: Cross-class extrapolation leads to nonsensical resistance estimates due to massive differences in block coefficient ($C_B$), Froude number regimes, and thruster mechanics.
3. **DANGEROUS: Optimizing Directly Against Raw ML**: Gradient-free metaheuristics easily discover ungrounded local minima where LightGBM predicts negative or near-zero fuel at high speeds outside the training manifold.
4. **DANGEROUS: Treating Nominal Quantile Width as Calibrated Risk**: Using $q_{95} - q_{05}$ without acknowledging its $78.51\%$ empirical coverage underestimates real-world operational risk.
5. **DANGEROUS: Merging CII, FuelEU, and IMO WtW into a Single Index**: FuelEU penalizes Well-to-Wake intensity in $\text{g CO}_2\text{e/MJ}$; IMO CII rates Tank-to-Wake annual operational intensity in $\text{g CO}_2\text{/(dwt}\cdot\text{nm)}$; EU ETS taxes carbon emissions in $\text{EUR/tonne}$. Conflating them invalidates regulatory compliance modeling.

### Q5: Which equations require external verification?
1. **Holtrop-Mennen Calm-Water Resistance**: Coefficients for cruise ship azipod appendages and transom immersion must be documented.
2. **Methane Slip in Dual-Fuel Engines**: Re-derived from first principles:
   $$\dot{m}_{\text{CH}_4, \text{slip}} = \dot{m}_{\text{LNG}} \times \sigma_{\text{slip}}$$
   $$\text{GHG}_{\text{slip}} = \dot{m}_{\text{CH}_4, \text{slip}} \times \text{GWP}_{100, \text{CH}_4}$$
   $$\text{Intensity contribution } = \frac{\dot{m}_{\text{CH}_4, \text{slip}} \times \text{GWP}_{100, \text{CH}_4}}{\dot{m}_{\text{LNG}} \times \text{LHV}_{\text{LNG}}}$$
3. **FuelEU Compliance Balance**: Verification of Annex IV equation from Regulation (EU) 2023/1805:
   $$\text{CB} = (\text{Target} - \text{Attained}) \times \sum (M_i \times \text{LHV}_i)$$
4. **IMO CII Reference Lines & Reduction Factors**: Verification of MEPC.338(76) reference line parameters ($a, c$) and annual reduction trajectory ($Z\% = 11\%$ in 2026).
5. **QPSO Position Update Dynamics**: Verification of Sun et al. (2004) delta-potential well equation:
   $$x_{i,d}(t+1) = p_{i,d} \pm \beta(t) |mbest_d - x_{i,d}(t)| \ln(1/u)$$

### Q6: Which data are real?
- FuelCast dataset (`krohnedigital/FuelCast`): 173,974 clean rows across `CPS_Poseidon`, `CPS_Triton`, and `OSS_Ceto`.
- Directly measured: Coriolis fuel mass flow ($\text{kg/s}$), acoustic Doppler log STW ($\text{kn}$), GPS SOG ($\text{kn}$), shaft power ($\text{kW}$), shaft torque ($\text{kNm}$), RPM ($\text{1/min}$), heading, draft ($\text{m}$), displacement ($\text{t}$).
- Reanalysis metocean data joined to telemetry: ECMWF ERA5 wave height ($H_s$), wave period ($T_p$), wave direction ($\theta_w$), wind speed ($V_{\text{wind}}$), ocean current velocity ($V_{\text{curr}}$).

### Q7: Which data are synthetic?
- Fleet-scale voyage scenarios (voyage distances, port pairs, cargo demand allocations, schedule deadlines).
- Alternative fuel pricing fluctuations (VLSFO, LNG, Bio-methanol, Green ammonia, LH2).
- Synthetic scalability fleet generator (5, 20, 50, 100 vessels for computational scaling benchmarks).
- Phase 2 synthetic benchmark dataset (`data/synthetic/synthetic_vessel_telemetry.csv`).

### Q8: Which optimization variables are actually observable?
- **Observable in Real Telemetry**: Speed Through Water (STW), Speed Over Ground (SOG), heading, draft, displacement, shaft power, RPM, shaft torque, wind speed, wave height.
- **Decision Variables (Controllable by Operator)**: Assigned vessel, commanded transit speed ($V_{\text{command}}$), selected fuel type ($F_{\text{type}}$), cargo payload ($m_{\text{cargo}}$), route/operating mode ($\text{Mode} \in \{\text{Transit}, \text{Maneuvering}, \text{DP}, \text{Port}\}$), shore power connection state.

### Q9: Which regulatory inputs are missing in raw telemetry?
- Raw telemetry does NOT contain:
  - Port call geographical boundaries (EU vs non-EU territorial waters).
  - Scope percentages (50% for extra-EU voyages, 100% for intra-EU voyages under FuelEU/EU ETS).
  - Annual cumulative transport work ($\sum \text{DWT} \times \text{Distance}$).
  - Certified bunker delivery notes (BDN) with certified Well-to-Tank emission factors.
- **Resolution**: Phase 3 provides explicit regulatory scenario configurations with transparently declared assumptions.

### Q10: What can legitimately be demonstrated at SIH?
1. **Rigorous Decision Support**: Demonstrating multi-objective tradeoffs between fuel savings, operational costs, Well-to-Wake decarbonization, and voyage schedules.
2. **Defensive AI Optimization**: Proving that unconstrained ML optimizers fail by finding unphysical zero-fuel exploits, while `SafeFuelObjective` guarantees physically grounded solutions.
3. **Fair Benchmark of Quantum-Inspired Metaheuristics**: Showing empirical convergence comparisons between QPSO, PSO, GA, DE, and Random Search under identical 50,000 evaluation budgets.
4. **Vessel-Class Domain Awareness**: Demonstrating that cruise vessels and offshore vessels have fundamentally different operational physics and cannot be optimized with generic models.
5. **Transparent Regulatory Tracking**: Presenting separate, compliant metrics for IMO CII, FuelEU Maritime, and EU ETS costs.

---

## 3. Files Inspected During Audit

1. `prediction/safe_objective.py`: Validated defensive wrapper, penalty structure ($100,000\text{ kg/h}$ hard penalty), disagreement thresholds ($150\text{ kg/h}$, $400\text{ kg/h}$), and risk objective $J(\lambda)$.
2. `prediction/domain_checker.py`: Inspected `PHYSICAL_VALIDITY_BOUNDS` and empirical envelope calculation. Identified need to support vessel-class and mode-aware rules.
3. `prediction/residual_model.py`: Inspected `HybridResidualPredictor` (`MODEL-REAL-04`). Verified strictly separate physics baseline and ML residual learning.
4. `experiments/exp_phase2_3_real_runner.py`: Audited chronological splits, LVO partitions, and 10-seed paired Wilcoxon statistical tests.
5. `lca/fuel_registry.py` & `configs/fuels.yaml`: Inspected fuel pathways, LHVs, WtT, and TtW factors based on IMO MEPC.391(81).
6. `lca/fuel_eu.py`: Audited FuelEU Maritime compliance balance and penalty calculation ($2,400\text{ EUR/t VLSFO equiv}$).
7. `lca/imo_cii.py`: Audited IMO CII calculation, reference line formulas, and rating boundaries (A–E).
8. `lca/methane_slip.py`: Audited methane slip dimensional tracking and GWP100 calculations.
9. `optimization/qpso.py`, `optimization/objective.py`, `optimization/variables.py`: Audited legacy Phase 0/1 optimization skeletons to be superseded by Phase 3 architecture.
10. `16_PHASE2_3_SCIENTIFIC_GATE_REPORT.md` & `17_PHASE2_3_CLAIM_LEDGER.yaml`: Verified baseline results and frozen evidence boundaries.

---

## 4. Pre-Implementation Audit Verdict

```
========================================================================================
                     PRE-IMPLEMENTATION AUDIT VERDICT:
                       PROCEED TO SPECIFICATION DRAFT
========================================================================================
```
The repository foundation is solid, frozen artifacts are identified and safeguarded, and dangerous assumptions have been explicitly cataloged. Implementation of optimization code remains blocked until all 9 Phase 3 specification documents are drafted and approved.
