# AUDIT #19: SIH 2026 JURY PRESENTATION GUIDELINES & SAFE CLAIMS
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §19 SIH Presentation Safe Claims Guide  
**Auditor:** SIH Technical Architect & Prior-Art / Novelty Auditor  
**Date:** September 15, 2026  

---

## 1. Section A: Safe to Say (Peer-Review Verified)

The following statements are 100% grounded in empirical data, mathematically verified, and safe to present to the SIH 2026 evaluation jury:

1. **"Egreen Quanta is a quantum-inspired classical metaheuristic, not quantum computing."**
2. **"Our framework employs heterogeneous variable partitioning: Q-bit probability vectors for discrete fleet decisions and Delta-potential QPSO for continuous operational variables."**
3. **"Constraint handling—specifically Deb's feasibility-first selection rule—was the primary factor that restored 100% feasibility, eliminating the Phase 4 QPSO failure mode."**
4. **"Deterministic repair guarantees constraint feasibility but causes severe population diversity collapse ($D = 5.75$). Q-bit representation maintains high diversity ($D = 189.54$), preventing premature swarm stagnation."**
5. **"All fuel consumption, hydrodynamics, and emissions models are calibrated directly on high-frequency sensor telemetry from the open DTU FuelCast dataset."**
6. **"Across 30 matched random seeds under equal 2,500-evaluation budgets, A5 achieved 100% run-level feasibility and zero constraint penalty incursions."**
7. **"Under identical evaluation budgets, A5 achieved a +64.0% higher hypervolume than the reference multi-objective baseline NSGA-III ($247.11 \times 10^6$ vs. $150.67 \times 10^6$)."**
8. **"Classical Differential Evolution (DE) achieved 100% feasibility and remains an exceptionally strong single-objective baseline."**
9. **"A5 and DE achieved comparable scalar physical fuel efficiency ($3.45$ vs. $3.70$), while A5 provides a complete multi-objective Pareto trade-off frontier."**
10. **"Our scientific contribution is an architectural system integration that unifies quantum-inspired operators, domain decoders, and real sensor surrogates into an operational maritime dispatch system."**

---

## 2. Section B: Say ONLY with Strict Qualification

The following statements are factually supported by our data, but must be accompanied by precise methodological boundaries:

1. **"A5 executed 2.67x faster than DE at $D=600$ (1.69 s vs. 4.49 s)."**  
   *Mandatory Qualification:* State clearly that this speedup reflects our NumPy-vectorized Python implementation rather than theoretical lower asymptotic complexity.
2. **"A5 achieved a 0.0% optimality gap against small-scale exhaustive search."**  
   *Mandatory Qualification:* Specify that the 0.0% gap applies to the **total penalized objective** ($J^* = 873.23$), where continuous speeds eliminated contractual schedule delay penalties. On pure unpenalized physical loss, the grid minimum was $3.2369$ and A5 achieved $4.5203$ within 500 evaluations.
3. **"Observed runtime scaled sub-linearly with dimension."**  
   *Mandatory Qualification:* State that empirical power-law regression yielded $b = 0.58 \pm 0.23$ ($R^2 = 0.76$) across the tested range of $D=30$ to $D=600$ under a fixed evaluation budget of 1,000 evaluations.
4. **"A5 demonstrated superior hypervolume compared to baselines."**  
   *Mandatory Qualification:* Specify that this comparison is against the multi-objective baseline **NSGA-III**, since DE was tested in a single-objective scalar configuration.

---

## 3. Section C: NEVER SAY (Strictly Forbidden & Discredited)

The following claims are scientifically false, mathematically contradicted, or ethically unacceptable. Any team member making these statements will be immediately disqualified:

1. ❌ **"We developed a quantum computing algorithm running on quantum computers."** *(False: Runs on classical x86 CPU).*
2. ❌ **"We achieved quantum supremacy or exponential quantum speedup."** *(False: No quantum hardware).*
3. ❌ **"We have physical quantum qubits."** *(False: Simulated probabilistic amplitudes).*
4. ❌ **"A5 is universally superior to all classical optimization algorithms."** *(False: DE is practically matched on physical fuel).*
5. ❌ **"We invented QPSO or QIEA."** *(False: Sun et al. 2004 and Han & Kim 2002 are established prior art).*
6. ❌ **"Egreen Quanta is the first maritime fleet optimizer in existence."** *(False: ABB OCTOPUS and StormGeo BVS exist).*
7. ❌ **"Canonical QPSO is fundamentally defective and unusable."** *(False: A1 proved Deb's rule cures QPSO entirely).*
8. ❌ **"Quantum-inspired mechanics was the sole reason feasibility was restored."** *(False: Deb's rule cured feasibility).*
9. ❌ **"Random search is 96.67% feasible."** *(Misleading: 0.30% candidate feasibility vs. 96.67% run success).*
10. ❌ **"Our tool eliminates all maritime uncertainty and operational risks."** *(Exaggerated commercial claim).*
