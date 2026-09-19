# SIH26138 Egreen Quanta — The Final Technical & Scientific Story

**Project Title:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Theme:** Advanced Operations Research, Maritime Decarbonization & Benchmark Scientific Integrity  
**Date of Scientific Closure:** September 18, 2026  
**Core Maxim:** *Evidence > Marketing. Science > Novelty Claims. Reproducibility > Impressive Numbers. Honest Benchmarking > Algorithm Promotion.*

---

## 1. The Starting Hypothesis and the "Quantum Trap"

Like many ambitious computational engineering projects, Egreen Quanta began with an enticing premise:
> *"Can quantum-inspired algorithms revolutionize commercial maritime fleet dispatch, slash fuel burn, and guarantee compliance with global emissions mandates?"*

Initial prototypes showed what appeared to be miraculous results:
- 100% fleet schedule and capacity feasibility!
- A staggering "+64% Hypervolume expansion over NSGA-III"!
- A "2.67x computational speedup"!
- "Sub-linear complexity across 100 vessels"!

In an uncritical environment, these headlines would have formed the core of a pitch deck. In a rigorous scientific audit, however, these numbers triggered intense skepticism. An independent validation team was brought in to conduct an adversarial forensic audit under strict scientific rules:
1. *No fabrication.*
2. *No changing problem formulations to favor an algorithm.*
3. *No quantum claims on classical hardware.*
4. *Zero tolerance for confounded causal claims.*

What followed was an extraordinary scientific journey of deconstruction, forensic debugging, and ultimate architectural vindication.

---

## 2. The Forensic Deconstruction: Unmasking Confounded Causality

### Discovery 1: The Feasibility Illusion
Early claims asserted that quantum probability amplitudes (Q-bits) "solved the maritime constraint satisfaction problem" by exploring combinatorial states in superposition.
To test this, the audit team constructed an ablation ladder from A0 to A5:
- **A0 (Plain QPSO with static penalty):** Achieved only $66.7\%$ feasibility.
- **A1 (Plain QPSO + Deb's feasibility-first rule):** Feasibility immediately jumped to **$100.0\%$** ($p = 1.8 \times 10^{-6}$).
- **A2 (A1 + Deterministic C0 Repair):** Guaranteed zero combinatorial collisions.

**The Verdict:** The quantum representation had **zero** measurable role in solving feasibility. Feasibility was restored entirely by Kalyanmoy Deb's classical 2000 feasibility-first tournament comparator and a deterministic Hungarian bipartite repair operator. Attributing feasibility to Q-bits was an unscientific confounding of variables.

### Discovery 2: The "+64% NSGA-III" Benchmark Injustice
The historical claim that our hybrid framework outperformed NSGA-III by $+64\%$ in Hypervolume ($247.11\text{M}$ vs. $150.67\text{M}$) was audited.
When the code was inspected, a glaring asymmetry was uncovered:
The hybrid algorithm had received C0 repair and Deb's feasibility-first comparator, while the baseline NSGA-III implementation was denied repair and evaluated under an arbitrary static penalty cliff, causing a 20% failure rate!

When NSGA-III was given the exact same C0 repair and Deb comparator:
- NSGA-III feasibility rose from $80.0\%$ to **$100.0\%$**.
- NSGA-III Hypervolume rose from $150.67\text{M}$ to **$247.07\text{M}$**.
- The difference between NSGA-III ($247.07\text{M}$) and A5 ($247.11\text{M}$) evaporated: $p = 0.6089$ (statistically indistinguishable).

The "+64% claim" was a benchmark artifact of unequal constraint handling. It was immediately and permanently retracted.

### Discovery 3: Classical Differential Evolution Outperforms QPSO
When classical Multi-Objective Differential Evolution (MODE / DE) was subjected to the same fair benchmark (identical C0 repair, Deb rules, 2,500 evaluations, 30 matched seeds):
- **MODE / DE achieved the lowest physical fuel burn:** $3.3936\text{ t}$ vs. A5's $3.4483\text{ t}$ ($p = 1.02 \times 10^{-7}$).
- **MODE / DE executed 21% faster:** $6.19\text{ s}$ vs. A5's $7.51\text{ s}$.

Classical vector difference mutation ($v = x_{r1} + F(x_{r2} - x_{r3})$) proved mathematically superior to QPSO's delta-potential well updates for continuous speed and draft optimization.

---

## 3. The Pure Representation-Isolation Experiment

Rather than discarding quantum-inspired methods entirely or pretending DE was inferior, the team designed the definitive scientific test:
**The Pure Representation-Isolation Experiment (C1 vs. C2).**

We held everything constant:
- Same continuous optimizer: Differential Evolution ($F=0.8, CR=0.9$)
- Same population size ($N=50$) and budget ($2,500$ evaluations)
- Same 30 matched seeds ($1001 \to 1030$)
- Same `CommonFleetEvaluator` and real FuelCast GBDT models
- Same C0 repair operator and Deb feasibility comparator
- Same Pareto reference points ($[500\text{t}, \$500\text{k}]$)

**Only the categorical representation was changed:**
- **C1 (Classical):** Classical discrete integer/random-key encoding.
- **C2 (Quantum-Inspired):** Multi-state Q-bits, Dirichlet-Q vectors, and conditional demand observation operators with unitary rotation gates.

### The Scientific Finding:
The results revealed the true, bounded value of quantum-inspired representations:
1. **Scalar Fuel Burn:** C1 and C2 achieve virtually identical physical fuel optimization ($p > 0.05$). Q-bits do not beat classical arithmetic for continuous trajectory optimization.
2. **Categorical Diversity & Entropy:** C2 consistently maintains higher categorical Shannon entropy ($3.85\text{ bits}$ vs. integer collapse) across generations. While deterministic repair causes classical encodings to prematurely collapse onto a single fuel or route choice, the quantum probability amplitude superpositions continuously explore alternative-fuel and cold-ironing combinations.

---

## 4. The Final Synthesis: Option D Architecture

With the evidence in hand, the team did not force an algorithm into a role it didn't earn. We adopted **Option D**:

1. **Primary Operational Engine — Classical MODE / DE + Deb + C0 Repair:**
   - Deployed for everyday shoreside fleet dispatch.
   - Lowest physical fuel consumption ($3.3936\text{ t}$).
   - 100% feasibility guaranteed.
   - Sub-7-second execution.

2. **Research & Exploration Engine — Heterogeneous QI + DE/QPSO:**
   - Deployed when fleet managers need to discover wide non-dominated Pareto trade-offs across emerging decarbonization pathways (e.g., bio-methanol transitions, cold-ironing electrification).
   - Preserves high categorical entropy across discrete decision variables.

3. **Grounded Common Core:**
   - **Real Telemetry:** 173,986 rows from 3 commercial vessels in FuelCast (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`).
   - **Hydrodynamic Physics Base:** Holtrop-Mennen empirical naval architecture resistance coupled with STAwave-2 wave added drag.
   - **Residual Machine Learning:** LightGBM GBDT predicting operational residuals over physics baseline ($R^2 = 0.9501$, $\text{MAE} = 246.97\text{ kg/h}$).
   - **Domain Barrier:** Mahalanobis DomainChecker preventing unphysical extrapolation.
   - **Statutory Decarbonization:** Rigorous codification of FuelEU Maritime (€2,400/t deficit penalty), IMO CII (A–E rating), and EU ETS (€90/t allowance liabilities).
   - **Uncertainty Management:** $\text{CVaR}_{0.80}$ tail-risk evaluation over 4 metocean weather scenarios.

---

## 5. What Makes Egreen Quanta Truly Winning

In competitive technical evaluations, many teams present exaggerated claims that collapse under technical scrutiny:
- They claim "quantum supremacy" on classical laptops.
- They claim "100-vessel validation" based on synthetic toy models.
- They claim their algorithm beats all others, hiding unfair constraint setups.

Egreen Quanta stands apart because **every claim has been audited, every benchmark is reproducible, and every limitation is openly disclosed**:
- We tell the evaluators: *"All computation is classical CPU heuristic; zero physical quantum hardware is utilized."*
- We tell the evaluators: *"Our real telemetry calibration covers 3 ships; the 100-vessel scenario is a synthetic scalability benchmark."*
- We tell the evaluators: *"Classical DE is our operational engine because it beats QPSO on physical fuel; Q-bits provide categorical diversity, not continuous optimization magic."*
- We tell the evaluators: *"Deb's rule solved feasibility, not quantum mechanics."*

By holding our project to the highest standard of scientific integrity, SIH26138 (Egreen Quanta) proves that applied operations research, naval architecture, and honest scientific benchmarking create an unassailable, real-world maritime decision-support platform.
