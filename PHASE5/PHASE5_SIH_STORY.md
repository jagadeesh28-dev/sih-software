# THE EGREEN QUANTA STORY: SCIENTIFIC INTEGRITY IN MARITIME OPTIMIZATION
**Project Code:** SIH26138  
**Title:** Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Team Narrative for SIH 2026 Grand Finale**

---

> *"We did not assume quantum-inspired optimization was better. We experimentally investigated where it helps, where it fails, and what architecture is scientifically defensible."*

---

## Act I: The Maritime Decarbonization Dilemma

Global commercial shipping accounts for nearly **3% of global greenhouse gas emissions**. In response, the International Maritime Organization (IMO) has mandated strict Carbon Intensity Indicator (CII) rating thresholds, while the European Union has enacted the FuelEU Maritime regulation, penalizing vessels that burn high-carbon fossil fuels with severe monetary fines.

For a fleet operating dozens of commercial vessels across diverse global trade lanes, the operational decision space is vast and combinatorial:
- Which vessel should serve which cargo charter?
- What cruising speed balances schedule punctuality against fuel burn ($P \propto V^3$)?
- What fuel mode—Heavy Fuel Oil (HFO), Marine Gas Oil (MGO), Liquefied Natural Gas (LNG), or Bio-MGO—should each ship switch to across different maritime zones?
- How do we optimize fuel, operating cost, and carbon emissions simultaneously without violating deadweight limits, arrival windows, or regulatory pooling rules?

This is the challenge of **Green Fleet Deployment**.

---

## Act II: Grounding in Reality — Real High-Frequency Telemetry

Most academic and competition submissions rely on idealized cubic formulas ($F = c \cdot V^3$) or synthetic random tables. **Egreen Quanta began with real industrial physics.**

We acquired and processed the open, peer-reviewed **DTU FuelCast** high-frequency maritime sensor telemetry dataset collected from active commercial vessels (*CPS Poseidon*, *CPS Triton*, and *OSS Ceto*):
- Millions of rows of high-frequency shaft power readings, engine RPM, GPS speed-over-ground, speed-through-water, displacement drafts, and concurrent Copernicus meteorological reanalysis data (significant wave height, wave period, ocean current velocity, and wind force).
- Trained multi-layer perceptron neural surrogate models that capture non-linear sea-margin hydrodynamics, trim dependencies, and Specific Fuel Oil Consumption (SFOC) curves with validated test-set $R^2 > 0.98$.

Our optimization algorithms do not query a toy formula; they query real vessel hydrodynamics calibrated against active commercial voyages.

---

## Act III: The Journey Through Phases 3 and 4

### Phase 3: The Simple Fleet & The Illusion of Easy Success
In Phase 3, we tested optimization on a homogeneous, continuous-speed fleet. Canonical algorithms—and even simple stochastic search—easily discovered feasible operating speeds. The optimization landscape appeared smooth and forgiving.

### Phase 4: The Heterogeneous Fleet Reality Shock
In Phase 4, we expanded the problem to a realistic, heterogeneous commercial fleet:
- 20 vessels, 4 alternative fuel types, 10 distinct cargo demands, deadweight constraints, strict port arrival windows, and FuelEU compliance pooling.
- We benchmarked canonical **Quantum-Behaved Particle Swarm Optimization (QPSO)** against classical metaheuristics across 30 matched random seeds (1001–1030) with an equal budget of 2,500 evaluations.

**The Unexpected Discovery:**
Canonical QPSO failed to find a feasible solution in **4 out of 30 runs (Seeds 1005, 1021, 1025, 1029)**, resulting in an $86.67\%$ feasibility rate, whereas classical Differential Evolution (DE) achieved $100\%$ feasibility.

Many teams would have swept this negative result under the rug, tuned the seeds, or quietly hidden the failures behind inflated averages. **We chose scientific honesty.**

---

## Act IV: Forensic Analysis — Why Did Plain QPSO Fail?

We conducted a forensic post-mortem on the failed QPSO trajectories:
1. **100% Assignment Constraint Failure:** In every failed run, the failure was caused by demand-to-vessel assignment collisions. Floating-point continuous QPSO particles rounded to identical categorical vessel indices, leaving some cargo demands unserved and overloading others.
2. **The Penalty Inversion Trap:** An infeasible assignment had a constraint penalty of approximately $\$51,000$. Meanwhile, a valid feasible candidate that experienced a temporary 2-hour schedule delay received a contractual delay penalty of $\$109,292$.
3. **The Stagnation Spiral:** Because classical QPSO used an additive penalty function ($J = f(x) + \text{penalty}$), the particle swarm rejected the feasible route in favor of the cheaper infeasible candidate. The quantum swarm's contraction-expansion radius collapsed around an invalid combinatorial state. The swarm froze.

---

## Act V: The Phase 5 Architecture — The Heterogeneous QI Framework

Instead of forcing continuous QPSO to handle discrete decisions, we designed the **Heterogeneous Quantum-Inspired Hybrid Fleet Optimizer (QI-HFO)**:
1. **Variable Partitioning:** Match representation directly to variable nature.
2. **Q-Bit Probabilistic Discrete Search (QIEA):** Use quantum probability amplitudes ($|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$) and Dirichlet quantum vectors to represent discrete cargo allocation and fuel mode selection.
3. **Delta-Potential Continuous QPSO:** Use continuous wave-packet collapse dynamics exclusively for continuous physical variables (speed and cargo weight).
4. **Principled Domain Decoder:** Guarantee bijective demand allocation so that structural assignment collisions are mathematically impossible.
5. **Deb's Feasibility-First Comparator:** Eliminate penalty inversion by enforcing that any feasible solution strictly dominates any infeasible solution.
6. **Multi-Objective Pareto Archive:** Track the true three-way trade-off between Fuel Consumption, Operating Cost, and GHG Emissions.

---

## Act VI: The A0–A5 Ablation — What Actually Fixed the Failure?

To answer our scientific question with uncompromising rigor, we designed an exact 6-stage ablation ladder and tested it across **30 matched seeds (1001–1030)** under an identical **2,500-evaluation budget** ($825,000$ total evaluations):

| Ablation Stage | Core Mechanism | Feasibility Rate | Mean Objective | Swarm Diversity | The Scientific Takeaway |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **A0 (Plain QPSO)** | Continuous QPSO, floating discretization | 80.0% (24/30) | 12,202.67 | 176.23 | Reproduces Phase 4 failure mode (penalty inversion). |
| **A1 (QPSO + Deb)** | A0 + Deb's feasibility-first rules | **100.0%** (30/30) | 2,003.35 | 171.19 | **Feasibility restored immediately without quantum modifications.** |
| **A2 (QPSO + Repair)**| A0 + Deterministic assignment repair | **100.0%** (30/30) | 3.39 | **5.75** | Feasibility restored, but greedy repair collapsed diversity. |
| **A3 (Discrete QPSO)**| CPMPSO discrete transitions | 86.67% (26/30) | 6,802.94 | 168.49 | Discrete transitions alone cannot escape penalty traps. |
| **A4 (Heterogeneous)** | Q-Bit discrete amplitudes + Continuous QPSO | **100.0%** (30/30) | 3.72 | **189.54** | **Q-Bits preserve diversity while maintaining 100% feasibility.** |
| **A5 (Full Hybrid)** | Full integrated multi-objective framework | **100.0%** (30/30) | **3.45** | **0.66 (Pareto)**| Discovers broad non-dominated Pareto frontier. |

### The Honest Scientific Truth:
- Did quantum-inspired mechanics fix the Phase 4 feasibility failure? **No. Deb's feasibility-first constraint handling fixed it (A1 achieved 100% feasibility).**
- What did the quantum-inspired representation actually contribute? **It prevented diversity collapse. While deterministic repair reduced swarm diversity to 5.75, Q-bit probability amplitudes maintained a diversity of 189.54, exploring alternative green fuel combinations and discovering a Pareto Hypervolume of $247.11 \times 10^6$ (+64% over NSGA-III).**

---

## Act VII: Benchmarking Against Classical Baselines

We compared Egreen Quanta against standard industry baselines:
- **Small-Scale Exact Validation ($J^* = 873.2265$):** A5 achieved an exact **0.0% optimality gap** within 500 evaluations.
- **Differential Evolution (DE):** DE achieved 100% feasibility and remains an outstanding single-objective classical baseline.
- **High-Dimensional Scalability ($D=30$ to $D=600$):** As the fleet scaled to 100 vessels ($D=600$), A5 scaled sub-quadratically, executing at **593.1 evaluations/second** and running **2.67x faster than DE**.

---

## Act VIII: The SIH Competitive Edge

Why does Egreen Quanta stand out in the SIH 2026 Grand Finale?

1. **Grounded in Real Science:** We used real DTU telemetry and honest physics, not fabricated formulas.
2. **Defensible Novelty:** We do not claim to have "invented quantum computing." We demonstrated a legitimate, peer-review-grade system integration combining Q-bit mechanics with domain-specific maritime decoders.
3. **Uncompromising Transparency:** We openly reported negative results (A3 failure) and proved that constraint handling, not quantum magic, was the true cure for feasibility failures.
4. **Complete Production-Ready Stack:** From the modular Python optimization engine (`src/`) to the interactive dispatch dashboard and publication-quality figures, Egreen Quanta is ready for operational deployment.

---

## Conclusion

The true value of innovation is not in making grand, unsupported claims. It is in having the technical competence to uncover why an algorithm fails, the scientific integrity to report the facts, and the engineering skill to build an architecture that delivers verifiable, reproducible excellence.

**Egreen Quanta is Green Maritime Optimization done right.**
