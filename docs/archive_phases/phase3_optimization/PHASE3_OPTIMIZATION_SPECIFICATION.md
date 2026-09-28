# PHASE 3 OPTIMIZATION SPECIFICATION
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Phase 3 Scientific Specification Document  
**Date:** 2026-09-12  
**Status:** SPECIFICATION LOCKED — PENDING IMPLEMENTATION  

---

## A. Decision Variables & Chromosome Representation

The optimization engine operates on a mixed-variable decision vector $\mathbf{x}$ representing an operational fleet dispatch strategy. For each vessel $v \in \{1, \dots, V\}$ assigned to voyage leg $l \in \{1, \dots, L\}$, the decision vector encapsulates:

$$\mathbf{x} = \left[ v_{\text{assign}}, F_{\text{type}}, V_{\text{command}}, m_{\text{cargo}}, \text{Mode}, S_{\text{shore}}, \alpha_{\text{fuel-mix}} \right]^T$$

### Detailed Variable Specification Table:

| Variable Symbol | Representation | Datatype | Units | Lower Bound | Upper Bound | Domain / Values | Physical Meaning | Real Observability | Synthetic Status | SIH Demo Requirement |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| $v_{\text{assign}}$ | `vessel_id` | Categorical / Discrete | - | 0 | $V-1$ | Indexed vessel ID in fleet registry | Selection of physical ship for voyage leg | Observed in FuelCast | Can be synthesized for fleet scaling | **MANDATORY** |
| $F_{\text{type}}$ | `fuel_type` | Categorical / Discrete | - | 0 | 4 | `0: vlsfo`, `1: fossil_lng`, `2: bio_methanol`, `3: green_ammonia`, `4: liquid_hydrogen` | Primary propulsion fuel choice | Real vessels burn VLSFO/MGO | Synthesized alternative fuels | **MANDATORY** |
| $V_{\text{command}}$ | `speed_knots` | Continuous | $\text{kn}$ | $V_{\min}(v)$ | $V_{\max}(v)$ | Vessel-specific bounds (e.g. $[8.0, 22.0]$ kn for cruise) | Commanded Speed Through Water (STW) | Measured via Doppler log / GPS | Parameterized in scenarios | **MANDATORY** |
| $m_{\text{cargo}}$ | `cargo_allocation_teu_or_tonnes` | Continuous | $\text{TEU}$ or $\text{t}$ | $0.0$ | $\text{Cap}_{\max}(v)$ | $0.0$ to max deadweight / TEU capacity | Carried payload for transport work | Derived from vessel draft/displacement | Parameterized in demand profiles | **MANDATORY** |
| $\text{Mode}$ | `operating_mode` | Discrete | - | 0 | 3 | `0: Transit`, `1: Maneuvering`, `2: DP_Station_Keeping`, `3: Port_Hoteling` | Hydrodynamic & engine operational regime | Classified in FuelCast | Defined per voyage leg | **MANDATORY** |
| $S_{\text{shore}}$ | `use_shore_power` | Binary | $\{0, 1\}$ | 0 | 1 | `0: Shipboard Genset`, `1: Cold Ironing` | Port electrification at berth | Real vessels have shore connection | Scenario toggle | **MANDATORY** |
| $\alpha_{\text{mix}}$ | `dual_fuel_pilot_ratio` | Continuous | $\%$ | $0.01$ | $1.00$ | $0.01$ (pilot MGO) to $1.00$ (pure mono-fuel) | Energy fraction of secondary/pilot fuel in dual-fuel engines | Documented in OEM specs (MAN/WinGD) | Parameterized | Optional / Secondary |

---

## B. Multi-Objective Function Vector

The objective space is formulated as a 5-dimensional vector minimization problem:

$$\min_{\mathbf{x} \in \mathcal{X}} \mathbf{F}(\mathbf{x}) = \left[ f_{\text{fuel}}(\mathbf{x}), f_{\text{cost}}(\mathbf{x}), f_{\text{ghg}}(\mathbf{x}), f_{\text{delay}}(\mathbf{x}), f_{\text{risk}}(\mathbf{x}) \right]^T$$

1. **Fuel Consumption Objective ($f_{\text{fuel}}$)**: Total voyage mass of fuel consumed in metric tonnes:
   $$f_{\text{fuel}}(\mathbf{x}) = \frac{1}{1000} \sum_{l=1}^L \dot{m}_{f, l}(\mathbf{x}) \cdot T_l(\mathbf{x})$$
   where $\dot{m}_{f, l}$ ($\text{kg/h}$) is evaluated strictly by `SafeFuelObjective` and $T_l$ ($\text{h}$) is leg duration.

2. **Operational Cost Objective ($f_{\text{cost}}$)**: Total Voyage OPEX in USD:
   $$f_{\text{cost}}(\mathbf{x}) = C_{\text{fuel}}(\mathbf{x}) + C_{\text{carbon}}(\mathbf{x}) + C_{\text{shore}}(\mathbf{x}) + C_{\text{schedule}}(\mathbf{x}) + C_{\text{penalty}}(\mathbf{x})$$

3. **Well-to-Wake Lifecycle GHG Emissions ($f_{\text{ghg}}$)**: Total carbon-equivalent footprint in metric tonnes $\text{CO}_2\text{e}$:
   $$f_{\text{ghg}}(\mathbf{x}) = \text{GHG}_{\text{WtT}}(\mathbf{x}) + \text{GHG}_{\text{TtW}}(\mathbf{x}) + \text{GHG}_{\text{slip}}(\mathbf{x})$$

4. **Schedule Delay & Punctuality Objective ($f_{\text{delay}}$)**: Schedule penalty in hours or financial demurrage:
   $$f_{\text{delay}}(\mathbf{x}) = \max\left(0, T_{\text{voyage}}(\mathbf{x}) - T_{\text{deadline}}\right) + \kappa_{\text{early}} \max\left(0, T_{\text{earliest}} - T_{\text{voyage}}(\mathbf{x})\right)$$

5. **Risk & Uncertainty Dispersion Objective ($f_{\text{risk}}$)**: Quantile dispersion indicating epistemic and aleatoric prediction risk:
   $$f_{\text{risk}}(\mathbf{x}) = \frac{1}{1000} \sum_{l=1}^L \left( q_{95, l}(\mathbf{x}) - q_{05, l}(\mathbf{x}) \right) \cdot T_l(\mathbf{x})$$

### Optimization Execution Modes:
- **Weighted-Sum Scalarization**: $J_{\text{scalar}}(\mathbf{x}) = \sum_{k=1}^5 w_k \tilde{f}_k(\mathbf{x}) + P_{\text{penalties}}(\mathbf{x})$, where $\sum w_k = 1$ and $\tilde{f}_k$ are range-normalized.
- **$\epsilon$-Constraint Mode**: Minimize $f_{\text{fuel}}(\mathbf{x})$ subject to $f_{\text{cost}} \le \epsilon_{\text{cost}}$, $f_{\text{ghg}} \le \epsilon_{\text{ghg}}$, $f_{\text{delay}} \le \epsilon_{\text{delay}}$.
- **Pareto Multi-Objective Mode**: Generates explicit Pareto-optimal non-dominated fronts using multi-objective metaheuristics (Q-MOEA/D, NSGA-III).

---

## C. Constraints System: Hard vs. Soft Constraints

### Hard Constraints (Infeasibility / Strict Rejection):
1. **Domain Validity Envelope ($g_{\text{domain}}(\mathbf{x}) \le 0$)**: Evaluated via `DomainChecker`. Candidate operational state must lie within the empirical bounding box of the selected vessel class. States flagged `OUT_OF_DOMAIN` or `PHYSICALLY_INVALID` trigger immediate hard barrier penalties ($100,000\text{ kg/h}$).
2. **Vessel Deadweight / Payload Capacity ($g_{\text{capacity}}(\mathbf{x}) \le 0$)**:
   $$m_{\text{cargo}} \le \text{Cap}_{\max}(v)$$
3. **Cargo Demand Satisfaction ($g_{\text{cargo}}(\mathbf{x}) \le 0$)**:
   $$\sum_{v} m_{\text{cargo}, v} \ge \text{Demand}_{\text{cargo}}$$
4. **Physical Speed Window ($g_{\text{speed}}(\mathbf{x}) \le 0$)**:
   $$V_{\min}(v) \le V_{\text{command}} \le V_{\max}(v)$$
5. **Engine MCR Propulsion Limit ($g_{\text{power}}(\mathbf{x}) \le 0$)**:
   $$P_{\text{shaft}}(V_{\text{command}}, \Delta, \text{weather}) \le 0.90 \times \text{MCR}(v)$$
6. **Fuel Compatibility Matrix ($g_{\text{compat}}(\mathbf{x}) = 0$)**:
   $$\text{Compatibility}(v, F_{\text{type}}) == \text{True}$$

### Soft Constraints (Smooth Penalties):
1. **Schedule Punctuality Window**: Desired arrival window $[T_{\text{earliest}}, T_{\text{latest}}]$. Arrival outside this window incurs quadratic penalty cost:
   $$P_{\text{sched}} = \mu_{\text{late}} \cdot \max(0, T_{\text{voyage}} - T_{\text{latest}})^2$$
2. **Empirical Boundary Proximity**: States in the `NEAR_BOUNDARY` region (outside P05–P95 core) incur a gentle proximity penalty proportional to normalized distance to prevent edge-sticking.
3. **CII Target Compliance**: Attained $\text{CII} > \text{Required CII}$ incurs soft penalty representing regulatory risk.
4. **FuelEU GHG Intensity Ceiling**: Attained intensity exceeding $89.34\text{ g CO}_2\text{e/MJ}$ adds statutory financial penalty ($2,400\text{ EUR/t VLSFO equiv}$).

---

## D. Vessel-Class Family Architecture

Due to the falsification of universal cross-class generalization in Phase 2.3, the optimization engine partitions vessels into distinct **Class Families**:

```
                  ┌─────────────────────────────────────────┐
                  │          VESSEL CLASS FAMILIES          │
                  └────────────────────┬────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ PASSENGER/CRUISE │          │ OFFSHORE SUPPLY  │          │      CARGO       │
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│ - High Hotel Load│          │ - DP Station-    │          │ - Transport-Work │
│   (1,200-2,800   │          │   keeping Mode   │          │   Dominant       │
│   kg/h baseline) │          │ - Variable       │          │ - Monohull Bulb  │
│ - Azipod Drives  │          │   Azimuth Power  │          │ - Two-Stroke     │
│ - Froude 0.2-0.3 │          │ - Froude 0.1-0.2 │          │   Direct Drive   │
│ - Target Vessel: │          │ - Target Vessel: │          │ - Target: Feeder │
│   CPS_Poseidon / │          │   OSS_Ceto       │          │   Container Ship │
│   CPS_Triton     │          │                  │          │   Baseline       │
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

**Class Isolation Rules**:
- Each class possesses an independent `DomainChecker` envelope derived strictly from that class's historical training telemetry.
- Cruise models incorporate auxiliary electrical baseline loads.
- Offshore models permit DP mode ($\text{STW} < 2\text{ kn}$ with multi-megawatt thruster power).
- Container/cargo models enforce transport work cargo constraints.

---

## E. Fuel Alternatives Scenario Framework

All alternative fuel coefficients are grounded in **IMO Resolution MEPC.391(81)** (2024 LCA Guidelines):

| Fuel Key | Description | Density ($\text{kg/m}^3$) | LHV ($\text{MJ/kg}$) | WtT Factor ($\text{g CO}_2\text{e/MJ}$) | TtW $\text{CO}_2$ ($\text{g/g}$) | Methane Slip $\sigma_{\text{slip}}$ | Price ($\text{USD/t}$) | Vol. Mult. | Cargo Pen. ($\%$) | Data Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `vlsfo` | Very Low Sulphur Fuel Oil | 940.0 | 40.2 | 13.5 | 3.114 | 0.000 | 620.0 | 1.0 | 0.0% | IMO MEPC.391(81) / Clarksons |
| `fossil_lng` | Liquefied Natural Gas | 450.0 | 48.0 | 18.5 | 2.750 | 0.022 (LPDF) | 680.0 | 1.8 | 2.0% | IMO MEPC.391(81) / ICCT 2024 |
| `bio_methanol` | Certified E-Biomethanol | 792.0 | 19.9 | 15.0 | 1.375 | 0.000 | 950.0 | 2.3 | 3.5% | IMO MEPC.391(81) / Methanol Inst. |
| `green_ammonia` | Renewable Ammonia ($\text{NH}_3$) | 681.0 | 18.6 | 8.0 | 0.000 | 0.000 | 1100.0 | 2.7 | 5.0% | IMO MEPC.391(81) / DNV 2024 |
| `liquid_hydrogen`| Cryogenic Liquid $\text{H}_2$ | 71.0 | 120.0 | 12.0 | 0.000 | 0.000 | 4200.0 | 4.8 | 9.5% | IMO MEPC.391(81) / IEA 2024 |

---

## F. Well-to-Wake Lifecycle Emission Model

$$\text{WtW} = \text{WtT} + \text{TtW}$$

For consumed fuel mass $m_f$ ($\text{kg}$):
1. **Total Chemical Energy**:
   $$E_{\text{fuel}} = m_f \times \text{LHV} \quad (\text{MJ})$$
2. **Well-to-Tank (Upstream) Emissions**:
   $$\text{GHG}_{\text{WtT}} = \frac{E_{\text{fuel}} \times \text{Factor}_{\text{WtT}}}{10^6} \quad (\text{tonnes CO}_2\text{e})$$
3. **Tank-to-Wake (Combustion) Emissions**:
   $$\text{GHG}_{\text{TtW, CO}_2} = \frac{m_f \times C_f}{1000} \quad (\text{tonnes CO}_2)$$
   $$\text{GHG}_{\text{TtW, N}_2\text{O}} = \frac{m_f \times \text{Factor}_{\text{N}_2\text{O}} \times \text{GWP}_{100, \text{N}_2\text{O}}}{10^6} \quad (\text{tonnes CO}_2\text{e})$$
4. **Methane Slip Emissions (LNG LPDF Engines)**:
   $$m_{\text{slip}} = m_f \times \sigma_{\text{slip}} \quad (\text{kg})$$
   $$\text{GHG}_{\text{slip}} = \frac{m_{\text{slip}} \times \text{GWP}_{100, \text{CH}_4}}{1000} \quad (\text{tonnes CO}_2\text{e})$$
   where $\text{GWP}_{100, \text{CH}_4} = 29.8$ (IPCC AR6 basis).

---

## G. Operational Cost Model

$$C_{\text{total}} = C_{\text{fuel}} + C_{\text{carbon}} + C_{\text{shore}} + C_{\text{schedule}} + C_{\text{fueleu\_penalty}}$$

- **Fuel Cost**: $C_{\text{fuel}} = \frac{m_f}{1000} \times P_{\text{fuel}}$
- **Carbon Tax Cost (EU ETS / Global Carbon Levy)**:
  $$C_{\text{carbon}} = \text{Scope}_{\text{ETS}} \times \text{GHG}_{\text{TtW}} \times P_{\text{carbon}}$$
  where $P_{\text{carbon}}$ defaults to $90.0\text{ USD/tonne CO}_2$ (configurable) and $\text{Scope}_{\text{ETS}} \in \{0.5, 1.0\}$.
- **Shore Power Electricity Cost**:
  $$C_{\text{shore}} = P_{\text{hotel, kW}} \times T_{\text{port, h}} \times \text{Tariff}_{\text{kWh}} + \text{Fee}_{\text{connect}}$$
- **Schedule Demurrage Penalty**:
  $$C_{\text{schedule}} = \max(0, T_{\text{voyage}} - T_{\text{deadline}}) \times \text{Rate}_{\text{demurrage, USD/h}}$$

---

## H. Route, Speed, and Weather Resistance Model

1. **Involuntary Speed Loss in Heavy Seas**:
   $$V_{\text{actual}} = \max\left(V_{\min}, V_{\text{command}} - c_{\text{loss}} \cdot H_s \cdot \cos(\theta_{\text{rel}})\right)$$
   where $c_{\text{loss}} \approx 0.15\text{ kn/m}$ for cruise hulls and $\theta_{\text{rel}}$ is relative wave heading.
2. **Voyage Duration**:
   $$T_{\text{transit}} = \frac{D_{\text{voyage}}}{V_{\text{actual}}} \quad (\text{hours})$$
   $$T_{\text{voyage}} = T_{\text{transit}} + T_{\text{maneuvering}} + T_{\text{port}}$$
3. **Fuel Flow Rate via Calibrated Hybrid Model (`MODEL-REAL-04`)**:
   $$\dot{m}_f = \text{SafeFuelObjective}(V_{\text{actual}}, T_{\text{draft}}, \Delta, H_s, T_p, V_{\text{wind}}, \dots)$$

---

## I. Uncertainty-Aware Optimization & Risk Formulations

Phase 2.3 demonstrated that nominal 90% pinball loss intervals achieve $78.51\%$ empirical coverage on real telemetry. Therefore:
- The base fuel estimate is set to the median prediction $q_{50}$.
- Robust optimization evaluates the risk-adjusted fuel objective:
  $$J_{\text{robust}}(\lambda) = q_{50} + \lambda \cdot (q_{95} - q_{05})$$
- We evaluate $\lambda \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$.
- Default benchmark setting: $\lambda = 0.5$.

---

## J. Optimization Algorithms Suite

1. **QPSO (Quantum-Behaved Particle Swarm Optimization)**:
   - Classical metaheuristic based on quantum delta-potential well dynamics (Sun et al., 2004).
   - Contraction-expansion schedule: $\beta(t) = \beta_{\text{start}} - (\beta_{\text{start}} - \beta_{\text{end}}) \cdot (t / t_{\max})$.
   - Completely classical CPU execution; no quantum computing claims.
2. **Standard PSO (Particle Swarm Optimization)**:
   - Canonical velocity-position updates with inertia weight $w$ and acceleration coefficients $c_1, c_2$.
3. **GA (Genetic Algorithm)**:
   - Real-coded tournament selection, SBX crossover, and polynomial mutation.
4. **DE (Differential Evolution)**:
   - Classical $\text{DE/rand/1/bin}$ with mutation factor $F=0.8$ and crossover probability $CR=0.9$.
5. **Random Search (Baseline)**:
   - Uniform random sampling across bounded decision space.

---

## K. Fixed Baseline Operational Policies

All optimizers are compared against standard commercial operating baselines:
- **BASELINE-1 (Max Speed)**: Commanded speed at upper limit $V_{\max}$ on VLSFO.
- **BASELINE-2 (Nominal Speed)**: Standard design cruising speed (e.g. 18 kn for cruise, 12 kn for OSV) on VLSFO.
- **BASELINE-3 (Fuel-Minimizing Speed)**: Minimum feasible speed $V_{\min}$ that satisfies the hard deadline on VLSFO.
- **BASELINE-4 (Cost-Minimizing Strategy)**: Speed and fuel choice minimizing total OPEX under current fuel and carbon prices.
- **BASELINE-5 (Green / Decarbonized Strategy)**: Zero/low-carbon fuel selection (e-methanol or ammonia) with cold ironing.
- **BASELINE-6 (Random Feasible Strategy)**: Randomly sampled feasible candidate.

---

## L. Fair Benchmarking Protocol

1. **Strict Evaluation Budget**: All algorithms receive exactly $N_{\text{eval}} = 50,000$ objective function evaluations (fast suite: $5,000$).
2. **Paired Seeds**: 30 independent pseudo-random seeds (minimum 10) shared across all algorithms.
3. **Statistical Significance**: Paired Wilcoxon signed-rank test on identical seeds, calculating $W$-statistic, $p$-value, Hodges-Lehmann median difference, and rank-biserial effect size $r$.
4. **Fairness Gate**: Algorithms cannot stop early unless convergence criteria are uniformly applied.

---

## M. Evaluation Metrics

- **Single-Objective**: Best objective value, mean, median, standard deviation, 95% confidence interval, convergence trajectory (objective vs evaluations).
- **Multi-Objective / Pareto**:
  - Hypervolume ($HV$) with fixed reference point $R_{\text{ref}}$.
  - Generational Distance ($GD$) and Inverted Generational Distance ($IGD$) against true/empirical non-dominated front.
  - Spacing Metric ($S$) measuring solution spread.
  - Number of Pareto-optimal solutions ($|P^*|$).
  - Feasibility Rate ($\%$ of swarm in-domain).

---

## N. Mandatory Ablation Studies

- **A1: No Physics Component**: Replacing `MODEL-REAL-04` with pure ML `MODEL-REAL-02`.
- **A2: No Environmental Information**: Zeroing wave height and wind speed in optimization.
- **A3: Risk-Neutral vs Risk-Averse**: Comparing $\lambda = 0.0$ against $\lambda = 0.5, 1.0, 2.0$.
- **A4: Regulatory Constraints Ablation**: Disabling FuelEU and CII constraints.
- **A5: Single vs Multi-Objective**: Comparing weighted-sum against true Pareto fronts.
- **A6: SafeFuelObjective Safety Ablation**: Optimizing directly against unconstrained LightGBM to demonstrate adversarial exploitation.

---

## O. Failure Criteria

An optimization run is declared **`FAILED`** if:
1. The returned solution violates any hard physical or domain constraint.
2. The optimizer returns a solution inside the adversarial trough (unphysical low fuel at high speed).
3. The feasibility rate is $< 50\%$ across the evaluation budget.
4. The algorithm fails to converge within $N_{\text{eval}}$ evaluations.
5. Seed variance across 30 runs exceeds $30\%$ of the mean objective.

---

## P. SIH Demonstration Requirements

The interactive SIH scenario demonstrates the primary trade-off narrative:
- **Input Controls**: Vessel selector (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`), voyage distance ($500\text{ nm}$), cargo demand ($10,000\text{ t}$), weather severity (Calm, Moderate, Storm), fuel price sliders, carbon tax toggle ($90\text{ USD/t}$), schedule deadline ($36\text{ h}$).
- **Output Comparison**: Side-by-side comparison table of **Current Strategy** vs. **Optimized Strategy**.
- **Interactive Pareto Front**: Plot showing Cost vs. WtW GHG Emissions with selectable operating presets:
  1. *Fuel Priority*: Maximum fuel economy.
  2. *Cost Priority*: Lowest total OPEX including ETS.
  3. *Green Priority*: Maximum WtW GHG reduction.
  4. *Balanced Decision*: Recommended compromise operating point.
- **Explainability Card**: Auto-generated text: *"Reducing transit speed from 19.5 kn to 16.2 kn extends voyage time by 4.2 hours but cuts fuel consumption by 24.8% and avoids $14,200 in FuelEU penalties while meeting schedule requirements."*

---

## Q. Research Claims: Allowed vs. Prohibited

### Strictly Prohibited Claims:
- "Quantum computers or quantum speedup were utilized."
- "Quantum advantage was proven."
- "Universal fleet-wide optimization is validated."
- "Real-world commercial fuel savings are confirmed."
- "Autonomous vessel navigation is enabled."

### Strictly Allowed Claims:
- "QPSO was benchmarked as a classical quantum-inspired metaheuristic against standard PSO, GA, DE, and Random Search."
- "Fuel consumption was evaluated using a vessel-class calibrated hybrid physics + ML surrogate wrapped with SafeFuelObjective."
- "Optimization demonstrated multi-objective Pareto trade-offs under verified IMO and EU regulatory constraints."
- "Optimization was constrained strictly to the empirical telemetry envelope of the evaluated commercial vessels."
