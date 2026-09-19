# Phase 5 System Architecture: Option C Hybrid QI-HFO
## Heterogeneous Quantum-Inspired Heterogeneous Fleet Optimizer

---

## 1. Architectural Philosophy

Standard metaheuristics typically treat optimization problems as either purely continuous ($\mathbb{R}^D$) or purely discrete ($\mathbb{Z}^D$). When applied to heterogeneous maritime fleet deployment, this leads to structural failure:
- Pure continuous optimizers (like canonical QPSO) round continuous floats to discrete indices. This generates zero-gradient plateaus, traps particles in non-viable categorical combinations, and induces penalty inversion.
- Pure discrete optimizers (like binary GAs) struggle with continuous physical dynamics (hydrodynamic hull friction, voluntary/involuntary speed loss, non-linear fuel consumption curves).

**Option C (Hybrid QI-HFO)** resolves this by establishing a **structurally matched heterogeneous architecture**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HYBRID QI-HFO INTEGRATED ARCHITECTURE                    │
│                                                                             │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │   DISCRETE / CATEGORICAL TIER   │   │         CONTINUOUS TIER         │  │
│  │     (Quantum-Inspired QIEA)     │   │      (Quantum-Behaved PSO)      │  │
│  │                                 │   │                                 │  │
│  │  • 2-State Q-bits (Shore Power) │   │  • Speed per vessel v (knots)   │  │
│  │  • Dirichlet-Q (Fuel Mode)      │   │  • Payload cargo (tonnes)       │  │
│  │  • Conditional Obs (Assignment) │   │  • Delta-well attraction (mbest)│  │
│  └────────────────┬────────────────┘   └────────────────┬────────────────┘  │
│                   │                                     │                   │
│                   └──────────────────┬──────────────────┘                   │
│                                      ▼                                      │
│                   ┌─────────────────────────────────────┐                   │
│                   │      PRINCIPLED REPAIR OPERATOR     │                   │
│                   │  • Eliminates demand collisions     │                   │
│                   │  • Verifies vessel compatibility    │                   │
│                   │  • Validates deadweight capacity    │                   │
│                   └──────────────────┬──────────────────┘                   │
│                                      ▼                                      │
│                   ┌─────────────────────────────────────┐                   │
│                   │        COMMON FLEET EVALUATOR       │                   │
│                   │  • Real FuelCast neural surrogates  │                   │
│                   │  • Weather scenarios & wave loss    │                   │
│                   │  • IMO CII & FuelEU compliance      │                   │
│                   │  • CVaR distributionally-robust risk│                   │
│                   └──────────────────┬──────────────────┘                   │
│                                      ▼                                      │
│                   ┌─────────────────────────────────────┐                   │
│                   │  DEB'S FEASIBILITY-FIRST SELECTION  │                   │
│                   │  1. Feasible beats Infeasible       │                   │
│                   │  2. Lower objective among feasible  │                   │
│                   │  3. Lower violation among infeasible│                   │
│                   └──────────┬───────────────────────┬──┘                   │
│                              │                       │                      │
│                              ▼                       ▼                      │
│                   ┌─────────────────────┐ ┌─────────────────────┐           │
│                   │  Q-BIT PHASE UPDATE │ │ QPSO POSITION UPDATE│           │
│                   │  Unitary Rotations  │ │ Delta-Well Dynamics │           │
│                   └─────────────────────┘ └─────────────────────┘           │
│                                      │                                      │
│                                      ▼                                      │
│                   ┌─────────────────────────────────────┐                   │
│                   │       PARETO ARCHIVE & NICHING      │                   │
│                   │  Non-dominated sorting (5-D)        │                   │
│                   │  [Fuel, OPEX, GHG, Delay, Risk]     │                   │
│                   └─────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Discrete Representation Tier (QIEA)
1. **Shore Power Binary Q-Bit**:
   - State: $|\psi_v\rangle = \alpha_v|0\rangle + \beta_v|1\rangle$, with $|\alpha_v|^2 + |\beta_v|^2 = 1$.
   - Phase parameterization: $\alpha_v = \cos(\theta_v)$, $\beta_v = \sin(\theta_v)$.
   - Measurement: $P(\text{shore}=1) = \sin^2(\theta_v)$.
2. **Categorical Fuel Vector (Dirichlet-Q)**:
   - Amplitude vector $\mathbf{q}_v = [q_{v,0}, \dots, q_{v,K-1}]$ over $K=5$ fuel choices.
   - Constrained by vessel profile: $\mathbf{q}_v \leftarrow \mathbf{q}_v \odot \mathbf{m}_v^{\text{compat}}$.
   - Update rule: Regularized probability rotation toward the best performing fuel mode.
3. **Combinatorial Demand Observation Operator**:
   - Amplitude matrix $\Theta \in \mathbb{R}^{V \times D}$ representing vessel-demand matching probabilities.
   - Conditional observation guarantees that $\sum_{v=1}^V d_{v,k} = 1$ for all mandatory cargo demands by construction, eliminating combinatorial demand assignment collisions.

### 2.2 Continuous Representation Tier (QPSO)
- Continuous variables (commanded speed $v_{\text{cmd}}$ and payload cargo $m_{\text{cargo}}$) are optimized using quantum delta-potential well dynamics.
- Mean best attractor:
  $$\mathbf{m}_{\text{best}} = \frac{1}{M} \sum_{i=1}^M \mathbf{p}_{\text{best},i}$$
- Local stochastic attractor:
  $$\mathbf{p}_{i} = \boldsymbol{\phi} \odot \mathbf{p}_{\text{best},i} + (1 - \boldsymbol{\phi}) \odot \mathbf{g}_{\text{best}}, \quad \boldsymbol{\phi} \sim U(0, 1)^D$$
- Delta-potential contraction-expansion update:
  $$\mathbf{x}_{i}(t+1) = \mathbf{p}_i \pm \beta(t) \cdot |\mathbf{m}_{\text{best}} - \mathbf{x}_i(t)| \cdot \ln\left(\frac{1}{\mathbf{u}}\right), \quad \mathbf{u} \sim U(0, 1)^D$$
  where $\beta(t)$ decays linearly from $\beta_{\text{start}} = 0.9$ to $\beta_{\text{end}} = 0.4$.

### 2.3 Principled Repair Operator
- Runs prior to evaluation to guarantee that no illegal candidate is sent to the physical evaluation pipeline.
- If an unguided or stochastic update generates duplicate demands, incompatible fuels, or deadweight breaches, the repair operator performs a minimal distance projection onto the feasible manifold.
- Tracks repair rate and evaluates whether repair causes artificial collapse of swarm diversity.

### 2.4 Deb's Feasibility-First Selection Rule
- Replaces naive scalar fitness comparison to permanently eliminate penalty inversion:
  $$\mathbf{x}_A \succ \mathbf{x}_B \iff \begin{cases}
  f(\mathbf{x}_A) < f(\mathbf{x}_B) & \text{if } v(\mathbf{x}_A) = 0 \text{ and } v(\mathbf{x}_B) = 0 \\
  \text{True} & \text{if } v(\mathbf{x}_A) = 0 \text{ and } v(\mathbf{x}_B) > 0 \\
  \text{False} & \text{if } v(\mathbf{x}_A) > 0 \text{ and } v(\mathbf{x}_B) = 0 \\
  v(\mathbf{x}_A) < v(\mathbf{x}_B) & \text{if } v(\mathbf{x}_A) > 0 \text{ and } v(\mathbf{x}_B) > 0
  \end{cases}$$
  where $v(\mathbf{x})$ is the total constraint violation magnitude.

### 2.5 Multi-Objective Pareto Archive
- Maintains non-dominated solutions across 5 distinct operational criteria:
  1. Total Fuel Consumption (tonnes)
  2. Total OPEX ($)
  3. Well-to-Wake GHG Emissions ($\text{tCO}_2\text{e}$)
  4. Schedule Delay Hours (hours)
  5. Distributionally-Robust CVaR Risk ($)
- Computes exact 2D hypervolume and multi-dimensional spacing to benchmark trade-off quality against NSGA-III.
