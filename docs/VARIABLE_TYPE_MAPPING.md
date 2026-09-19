# Variable Type Mapping Specification
## SIH26138 — Egreen Quanta: Heterogeneous Fleet Optimization

---

## 1. Overview and Rationale

In Phase 4, the optimization vector for a fleet of $V$ vessels was treated as an unpartitioned continuous hypercube $\mathbf{x} \in \mathbb{R}^{6V}$. Categorical variables (such as vessel cargo demand assignment and fuel mode) were naively rounded to the nearest integer. This caused:
1. **Integer Plateau Stagnation**: Continuous gradients across categorical thresholds were zero almost everywhere, causing standard QPSO velocity/attractor dynamics to drift uncontrollably.
2. **Combinatorial Demand Collision**: Multiple vessels rounded to the same demand index (e.g., two vessels assigned to Demand-A), creating hard constraint violations that triggered catastrophic penalty inversion.

Phase 5 resolves this by explicitly partitioning the decision space into **Continuous**, **Binary**, and **Categorical** domains, assigning dedicated representation and mutation/update operators to each variable class.

---

## 2. Fleet Decision Vector Architecture

Each vessel $v \in \{1, \dots, V\}$ has 6 decision dimensions. For a fleet of $V$ vessels, total dimension $D = 6V$. For the primary benchmark ($V=3$, 18 dimensions):
- Vessels: `CPS_Poseidon` ($v=1$), `CPS_Triton` ($v=2$), `OSS_Ceto` ($v=3$).
- Cargo Demands: `DEMAND-A`, `DEMAND-B`, `DEMAND-C`.

### Variable Specification Table

| Index ($d$) | Variable Name | Domain Type | Allowed / Valid Domain | Continuous Bounds $[x_l, x_u]$ | Assigned Optimizer | Decoder / Mapping | Repair Rule | Dependent Constraints |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **0** | `assigned_demand` | **Categorical / Combinatorial** | $\{0, 1, 2, 3\}$ (0: Unassigned, 1: Dem-A, 2: Dem-B, 3: Dem-C) | $[0.0, 3.0]$ | **QIEA (Q-bit matrix)** in A4/A5; QPSO in A0-A3 | Rounded to nearest int in A0-A3; Conditional observation in A4/A5 | Greedy Hungarian matching: ensure each mandatory demand is assigned to exactly one compatible vessel | Hard: Exactly-once demand fulfillment; Vessel family compatibility; DWT capacity |
| **1** | `cargo_tonnes` | **Continuous** | $[0, \text{DWT}_v]$ tonnes | $[0.0, \text{DWT}_v]$ | **QPSO (Delta-well)** | Direct continuous float | Clipped to $[0, \text{DWT}_v]$; Set to demand cargo quantity if assigned | Hard: Deadweight limit; Soft: Fuel consumption payload effect |
| **2** | `speed_knots` | **Continuous** | $[v_{\min}, v_{\max}]$ knots | $[v_{\min}, v_{\max}]$ | **QPSO (Delta-well)** | Direct continuous float | Clipped to $[v_{\min}, v_{\max}]$; Minimum speed enforced to meet schedule | Hard: Safe navigation speed envelope; Soft: Voyage deadline schedule delay |
| **3** | `fuel_type` | **Categorical** | $\{0, 1, 2, 3, 4\}$ (0: VLSFO, 1: LNG, 2: Bio-methanol, 3: Ammonia, 4: Hydrogen) | $[0.0, 4.0]$ | **Dirichlet-Q vector** in A4/A5; QPSO in A0-A3 | Rounded to nearest int in A0-A3; Dirichlet-Q multinomial sample in A4/A5 | Filtered by vessel profile `compatible_fuels`; if invalid, mapped to default compliant fuel (e.g. VLSFO) | Hard: Engine-fuel technical compatibility; FuelEU Maritime compliance penalty |
| **4** | `operating_mode` | **Categorical** | $\{0, 1, 2, 3\}$ (0: Transit, 1: Maneuvering, 2: DP, 3: Port) | $[0.0, 3.0]$ | **Dirichlet-Q vector** in A4/A5; QPSO in A0-A3 | Rounded to nearest int in A0-A3; Categorical sample in A4/A5 | Set to 0 (Transit) for voyage legs | Operational profile validity; Aux engine power |
| **5** | `use_shore_power` | **Binary** | $\{0, 1\}$ (0: False, 1: True) | $[0.0, 1.0]$ | **Q-bit (2-state)** in A4/A5; QPSO in A0-A3 | Threshold $\ge 0.5 \to 1$, else $0$ in A0-A3; Q-bit $\|\beta\|^2$ sample in A4/A5 | Masked by port shore power readiness (cannot use if port lacks infrastructure) | Hard: Port electrical readiness; Soft: Port OPEX / GHG reduction |

---

## 3. Decision Vector Partitioning Matrix

For a 3-vessel heterogeneous fleet:

```
Dimension Index:
 0: Poseidon Demand   [Categorical] -> QIEA / Discrete
 1: Poseidon Cargo    [Continuous]  -> QPSO
 2: Poseidon Speed    [Continuous]  -> QPSO
 3: Poseidon Fuel     [Categorical] -> Dirichlet-Q / Discrete
 4: Poseidon Mode     [Categorical] -> Dirichlet-Q / Discrete
 5: Poseidon Shore    [Binary]      -> Q-bit / Discrete
 6: Triton Demand     [Categorical] -> QIEA / Discrete
 7: Triton Cargo      [Continuous]  -> QPSO
 8: Triton Speed      [Continuous]  -> QPSO
 9: Triton Fuel       [Categorical] -> Dirichlet-Q / Discrete
10: Triton Mode       [Categorical] -> Dirichlet-Q / Discrete
11: Triton Shore      [Binary]      -> Q-bit / Discrete
12: Ceto Demand       [Categorical] -> QIEA / Discrete
13: Ceto Cargo        [Continuous]  -> QPSO
14: Ceto Speed        [Continuous]  -> QPSO
15: Ceto Fuel         [Categorical] -> Dirichlet-Q / Discrete
16: Ceto Mode         [Categorical] -> Dirichlet-Q / Discrete
17: Ceto Shore        [Binary]      -> Q-bit / Discrete
```

### Summary of Partitions
- **Continuous Variables (6 total)**: Dimensions 1, 2, 7, 8, 13, 14. Managed via QPSO delta-potential contraction-expansion dynamics.
- **Binary Variables (3 total)**: Dimensions 5, 11, 17. Managed via 2-state quantum bit rotations $\|\psi\rangle = \alpha\|0\rangle + \beta\|1\rangle$.
- **Categorical Variables (9 total)**: Dimensions 0, 3, 4, 6, 9, 10, 12, 15, 16.
  - Assignment: Dimensions 0, 6, 12. Managed via conditional observation guaranteeing bijective or valid demand matching.
  - Fuel Selection: Dimensions 3, 9, 15. Managed via Dirichlet-Q vectors over authorized fuel subsets.
  - Operating Mode: Dimensions 4, 10, 16. Managed via uniform or scenario-driven discrete states.

---

## 4. Decoder & Repair Pipeline

```
Raw Solution Candidate
         │
         ▼
┌──────────────────────────────────────────────┐
│ STEP 1: Type Partitioning                   │
│ Split continuous vs. categorical vs. binary  │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ STEP 2: Categorical Decoding & Matching      │
│ Decode demand indices; identify collisions   │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ STEP 3: Repair Operator (if enabled)         │
│ - Resolve duplicate demand assignments       │
│ - Ensure 100% vessel compatibility           │
│ - Validate cargo vs. deadweight capacity     │
│ - Replace incompatible fuel choices          │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ STEP 4: Continuous Projection                │
│ Clip speed and cargo to physical bounds      │
└──────────────────────────────────────────────┘
         │
         ▼
To Common Evaluator
```

This mapping strictly guarantees that the optimization engine matches the mathematical structure of the maritime fleet deployment problem.
