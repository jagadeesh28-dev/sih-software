# SIH26138 Egreen Quanta — Final Hostile Jury Defense & Cross-Examination Guide

**Role:** Defense of Scientific Integrity for SIH26138 (Egreen Quanta)  
**Standard:** Uncompromising Scientific Honesty, Forensic Traceability, and Zero Handwaving  
**Audit Date:** September 18, 2026  
**Target Audience:** Senior Academics, Optimization Experts, Naval Architects, Maritime Regulators, and Hostile SIH Evaluators

---

## Question 1: "Why quantum-inspired if DE performs better?"
* **Scientifically Correct Answer:**  
  "Our empirical benchmarks show that classical Differential Evolution (DE) coupled with C0 repair and Deb's feasibility-first rule is indeed superior for continuous speed and cargo optimization, achieving the lowest physical fuel burn ($3.3936\text{ t}$ vs. $3.4483\text{ t}$, $p = 1.02 \times 10^{-7}$) and faster runtime ($6.19\text{ s}$ vs. $7.51\text{ s}$). Therefore, our operational engine is classical DE. We retain the quantum-inspired (QI) representation strictly as an exploratory research engine because its probability amplitude superposition preserves higher categorical Shannon entropy ($3.85\text{ bits}$ vs. greedy deterministic collapse) across discrete route and fuel choices. We do not force QI to be the operational winner where classical optimization is empirically superior."
* **Evidence:**  
  `results/raw/fair_mode_30seeds.csv`, `results/raw/A5.csv`, `audit/BENCHMARK_INTEGRITY_REPAIR.md` §2, paired Wilcoxon test ($p = 1.02 \times 10^{-7}$).
* **Strongest Attack Point:**  
  "Then your quantum-inspired algorithm is completely unnecessary for your core operational goal."
* **Response to Attack Point:**  
  "For pure scalar fuel minimization on this benchmark, yes—classical DE is sufficient and preferred. That is why our Option D architecture freezes classical MODE/DE as the primary operational engine. The QI module is maintained in the research interface specifically for combinatorial categorical diversity exploration in large-scale multi-fuel fleet assignments."
* **What NOT to Say:**  
  *Never say:* "Quantum-inspired will beat DE once the fleet gets larger," or "Quantum tunneling overcomes local minima in continuous variables."
* **Confidence Level:** **HIGH (100% backed by paired benchmark data)**.

---

## Question 2: "What exactly do the Q-bits contribute?"
* **Scientifically Correct Answer:**  
  "Q-bits contribute a probabilistic parameterization of discrete categorical decisions (fuel type, operating mode, shore connection, and demand assignment). By updating continuous phase angles $\theta$ via unitary rotation gates rather than greedy discrete bit-flips, the population maintains a superposition-like distribution over discrete combinations. This preserves exploratory diversity and categorical Shannon entropy across generations, preventing premature convergence to a single fuel/route combination."
* **Evidence:**  
  `src/representation/qbit_representation.py`, `audit/representation_benchmark.md` (R5 entropy = 3.91 bits vs. R1 integer = 2.14 bits).
* **Strongest Attack Point:**  
  "An Estimation of Distribution Algorithm (EDA) or simple categorical probability vector does the exact same thing without quantum terminology."
* **Response to Attack Point:**  
  "Mathematically, Dirichlet-Q and QIEA rotation gates are isomorphic to bounded categorical probability updates. We explicitly document this equivalence in our novelty audit. The value lies in the smooth trigonometric rotation dynamics that couple with our conditional observation operator, not in any physical quantum phenomenon."
* **What NOT to Say:**  
  *Never say:* "Q-bits provide quantum entanglement" or "Q-bits evaluate all combinations simultaneously in parallel universes."
* **Confidence Level:** **HIGH (Mathematically verified)**.

---

## Question 3: "Didn't Deb, rather than Q-bits, solve your feasibility problem?"
* **Scientifically Correct Answer:**  
  "Yes, absolutely. Our ablation experiment A0 $\to$ A1 isolates Deb's feasibility-first comparison rule from the representation. Adding Deb's rule alone increased run feasibility from $66.7\%$ to $100.0\%$ ($p = 1.8 \times 10^{-6}$), whereas adding Q-bits without Deb (A0) left feasibility at $66.7\%$. Deb's rule is the primary mathematical driver of feasibility restoration. Q-bits govern diversity, not feasibility enforcement."
* **Evidence:**  
  `audit/BENCHMARK_INTEGRITY_REPAIR.md` Table 2 (A0 $\to$ A1 jump in feasibility from 66.7% to 100.0%).
* **Strongest Attack Point:**  
  "Earlier versions of your slides claimed that quantum-inspired optimization solved the fleet feasibility problem."
* **Response to Attack Point:**  
  "That earlier causal attribution was confounded and scientifically incorrect. Our forensic audit disentangled the components: Deb's tournament rule enforces feasibility, C0 repair resolves combinatorial collisions, and Q-bits govern categorical diversity. We have formally retracted the claim that Q-bits cause feasibility."
* **What NOT to Say:**  
  *Never say:* "Q-bits and Deb solved it together equally." (Deb is mathematically dominant for constraint satisfaction).
* **Confidence Level:** **VERY HIGH (Definitive ablation proof)**.

---

## Question 4: "Why shouldn't I simply use DE?"
* **Scientifically Correct Answer:**  
  "For day-to-day single-objective or scalar voyage dispatch, you SHOULD simply use DE. In fact, our system's primary operational engine is MODE / DE with C0 repair and Deb rules. We only invoke the QI exploratory engine when a fleet manager needs to discover non-obvious combinatorial alternative-fuel strategies across multiple non-dominated Pareto trade-offs."
* **Evidence:**  
  `audit/FINAL_FROZEN_BENCHMARK_PROTOCOL.md` (Option D architecture: MODE/DE as primary engine).
* **Strongest Attack Point:**  
  "Then why is the project titled 'Quantum-Inspired Fleet Optimization'?"
* **Response to Attack Point:**  
  "The research mandate of SIH26138 was to evaluate whether quantum-inspired representations offer advantages for green fleet dispatch. By conducting rigorous controlled benchmarking, we scientifically bounded where QI helps (discrete categorical diversity) and where classical optimization is superior (continuous parameter tuning). A scientific project that honestly reports where an advanced method loses is far more defensible than one that manufactures false superiority."
* **What NOT to Say:**  
  *Never say:* "DE gets stuck in local minima so you must use QI." (DE achieved lower fuel burn than QI in our tests).
* **Confidence Level:** **VERY HIGH**.

---

## Question 5: "Your Q-bit representation already exists in prior literature. What is actually new?"
* **Scientifically Correct Answer:**  
  "We make zero claim of having invented QIEA (Han & Kim, 2002), QPSO (Sun et al., 2004), or d-QPSO (Lukemire et al., 2019). The novelty of this project is strictly domain-specific and architectural: the first formulation of a mixed-variable maritime fleet optimization problem integrating real high-frequency telemetry, hydrodynamic Holtrop-Mennen resistance, residual machine learning, statutory maritime decarbonization constraints (FuelEU Maritime, IMO CII, EU ETS), and a modular solver architecture."
* **Evidence:**  
  `PHASE5/PHASE5_NOVELTY_AUDIT.md`, `audit/FINAL_CLAIM_LEDGER.md` Claim 19.
* **Strongest Attack Point:**  
  "If the optimization math is known and the physics equations are 1982 Holtrop-Mennen, what is the research contribution?"
* **Response to Attack Point:**  
  "The research contribution is the principled coupling of naval architecture physics with ML residual learning to eliminate adversarial unphysical solutions, combined with an open, reproducible benchmark showing the exact limits of quantum-inspired representations under strict constraint handling."
* **What NOT to Say:**  
  *Never say:* "We invented a novel Dirichlet-Q quantum gate never seen before in mathematics."
* **Confidence Level:** **HIGH**.

---

## Question 6: "Your real dataset contains only three vessels. Why should I trust recommendations for a larger fleet?"
* **Scientifically Correct Answer:**  
  "You should trust the ML residual model ONLY for vessel classes geometrically similar to the three calibrated hulls (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`). For uncalibrated vessel classes or fleet sizes scaled up to 100 vessels, our system activates an automated Mahalanobis DomainChecker that detects out-of-domain geometry and falls back to calibrated hydrodynamic physics (Holtrop-Mennen & Kwon added resistance). We do not blindly extrapolate ML models to vessels on which they were not trained."
* **Evidence:**  
  `prediction/domain_checker.py`, `audit/new_vessel_ood_test.md` (100% OOD interception rate).
* **Strongest Attack Point:**  
  "Then your 100-vessel scaling benchmark is purely synthetic."
* **Response to Attack Point:**  
  "Yes. The 100-vessel benchmark is strictly a computational scalability stress test over dimension $D=600$. We explicitly distinguish our real 3-vessel calibration dataset (173,986 rows) from our synthetic computational scaling scenarios."
* **What NOT to Say:**  
  *Never say:* "The GBDT model generalizes across all world shipping because neural networks learn general physics."
* **Confidence Level:** **HIGH**.

---

## Question 7: "Is your 100-vessel fleet real?"
* **Scientifically Correct Answer:**  
  "No. The 100-vessel fleet is a synthetic benchmark instance ($D = 600$) created by replicating and parameterizing vessel classes to evaluate algorithm execution runtime, memory footprint, and numerical stability at scale. Our real telemetry calibration is strictly based on 3 commercial vessels."
* **Evidence:**  
  `audit/scalability_report.md` §1, `audit/FINAL_CLAIM_LEDGER.md` Claim 15.
* **Strongest Attack Point:**  
  "You claimed earlier that Egreen Quanta manages commercial fleets of 100 ships."
* **Response to Attack Point:**  
  "That was inaccurate phrasing in preliminary demonstration materials. We have audited every document and strictly categorized the 100-vessel experiments as synthetic computational scaling tests."
* **What NOT to Say:**  
  *Never say:* "The 100 vessels are real ships whose identities are protected by NDA."
* **Confidence Level:** **ABSOLUTE (Honest scientific disclosure)**.

---

## Question 8: "Why did your earlier benchmark claim +64% HV?"
* **Scientifically Correct Answer:**  
  "The historical '+64% Hypervolume' claim was the result of an unscientific benchmark asymmetry: baseline NSGA-III was run without C0 repair and without Deb's feasibility-first rule, resulting in a 20% infeasibility rate and a degraded Hypervolume of $150.67\text{M}$. When NSGA-III was re-tested under identical conditions (receiving the same C0 repair and Deb rules as A5), its feasibility reached $100\%$ and its Hypervolume reached $247.07\text{M}$, statistically indistinguishable from A5's $247.11\text{M}$ ($p = 0.6089$). We permanently retracted the +64% claim."
* **Evidence:**  
  `results/raw/fair_nsga3_30seeds.csv`, `audit/BENCHMARK_INTEGRITY_REPAIR.md` §1.
* **Strongest Attack Point:**  
  "That means your original benchmark was biased to make your algorithm look good."
* **Response to Attack Point:**  
  "Yes, the original benchmark had a methodological flaw in constraint-handling fairness. When our audit identified this flaw, we corrected the code, re-ran the 30 seeds under matched conditions, published the corrected numbers, and retracted the invalid claim. That is how scientific integrity works."
* **What NOT to Say:**  
  *Never say:* "NSGA-III is still 64% worse in certain complex edge cases."
* **Confidence Level:** **ABSOLUTE (Fully documented in audit logs)**.

---

## Question 9: "Why did your runtime previously say 2.67x faster?"
* **Scientifically Correct Answer:**  
  "The legacy '2.67x faster' claim was derived from a comparison between a vectorized implementation of A5 and an unvectorized serial Python baseline on an uncalibrated laptop during initial prototyping. In our standardized, frozen benchmark under identical hardware and single-threaded execution, classical MODE runs in $6.19\text{ s}$ while A5 runs in $7.51\text{ s}$. Classical MODE is faster than A5. The 2.67x claim has been retracted."
* **Evidence:**  
  `audit/RUNTIME_PROVENANCE.csv`, `results/raw/fair_mode_30seeds.csv`, `results/raw/A5.csv`.
* **Strongest Attack Point:**  
  "Your QI algorithm is actually slower than classical methods."
* **Response to Attack Point:**  
  "Yes, A5 has an approximate 21% runtime overhead ($7.51\text{ s}$ vs. $6.19\text{ s}$) due to quantum amplitude updates, trigonometric evaluations, and Shannon entropy tracking. We report this overhead openly in our runtime provenance table."
* **What NOT to Say:**  
  *Never say:* "A5 is faster in compiled C++ or on GPU." (Our benchmark was in Python on CPU).
* **Confidence Level:** **ABSOLUTE (Verified)**.

---

## Question 10: "Is your algorithm actually quantum?"
* **Scientifically Correct Answer:**  
  "No. The algorithm is 100% classical software executed on standard classical x86_64 CPUs. 'Quantum-inspired' means the algorithm borrows mathematical concepts from quantum mechanics—specifically probability amplitude state vectors, superposition principles, and unitary rotation matrices—to design classical heuristic search operators. It is not quantum computing."
* **Evidence:**  
  `audit/FINAL_FROZEN_BENCHMARK_PROTOCOL.md` §5 (Intel/AMD CPU execution in Python).
* **Strongest Attack Point:**  
  "Then calling it 'quantum' is marketing hype."
* **Response to Attack Point:**  
  "The term 'Quantum-Inspired Evolutionary Algorithm' (QIEA) is standard academic nomenclature established by Han & Kim in 2002 and extensively published in IEEE Transactions on Evolutionary Computation. However, to eliminate any potential misunderstanding, we state prominently on slide 1: 'All computations are classical CPU heuristics; zero quantum hardware utilized.'"
* **What NOT to Say:**  
  *Never say:* "It simulates quantum superposition at the hardware level."
* **Confidence Level:** **ABSOLUTE**.

---

## Question 11: "Where is the quantum computer?"
* **Scientifically Correct Answer:**  
  "There is no quantum computer. No quantum processor, QPU, dilution refrigerator, or physical qubits are used. The software runs on a standard laptop or cloud server."
* **Evidence:**  
  `src/algorithms/hybrid_qi.py` (Plain NumPy code).
* **Strongest Attack Point:**  
  "Why did you enter a problem under quantum optimization if you don't use a quantum computer?"
* **Response to Attack Point:**  
  "Current Noisy Intermediate-Scale Quantum (NISQ) computers cannot solve mixed-integer non-linear constrained fleet dispatch problems with 18 to 600 continuous and categorical variables under strict maritime constraints. Quantum-inspired classical algorithms run today on standard maritime IT infrastructure without cryogenic hardware."
* **What NOT to Say:**  
  *Never say:* "We are ready to plug into IBM Q or D-Wave next month."
* **Confidence Level:** **ABSOLUTE**.

---

## Question 12: "Does CVaR guarantee safety?"
* **Scientifically Correct Answer:**  
  "No. Conditional Value-at-Risk ($\text{CVaR}_{0.80}$) is a risk-penalization metric that penalizes expected tail loss in the worst 20% of weather scenarios. It does NOT guarantee physical storm safety. Physical safety is enforced by strict hard constraints: maximum engine power limits (MCR), wave height operational envelopes, and minimum steerage speeds. CVaR provides risk-averse economic dispatch, not a structural safety warranty."
* **Evidence:**  
  `optimization/cvar.py`, `PHASE4_UNCERTAINTY_MODEL.md`.
* **Strongest Attack Point:**  
  "If a rogue wave hits, your optimizer can't stop the ship from capsizing."
* **Response to Attack Point:**  
  "Correct. Strategic voyage planning software cannot override shipboard damage control. Our system avoids voyage plans that route vessels into forecasted sea states exceeding naval architectural safety envelopes."
* **What NOT to Say:**  
  *Never say:* "CVaR guarantees zero risk in rough seas."
* **Confidence Level:** **VERY HIGH**.

---

## Question 13: "What happens when a new vessel enters the fleet?"
* **Scientifically Correct Answer:**  
  "When a new vessel profile is ingested, the system executes two steps: First, its naval architectural particulars (length, beam, draft, displacement, block coefficient) are loaded into the Holtrop-Mennen physical resistance model. Second, the DomainChecker evaluates the Mahalanobis distance of its geometry against our training hull database. If flagged as unseen/out-of-domain, the system automatically disables the ML residual model and relies on the calibrated hydrodynamic physics model until sea-trial noon reports are collected for calibration."
* **Evidence:**  
  `prediction/domain_checker.py`, `audit/new_vessel_ood_test.md`.
* **Strongest Attack Point:**  
  "Physics models have 10–20% error without calibration."
* **Response to Attack Point:**  
  "That is true, and our OOD test explicitly reports that pure Holtrop-Mennen baseline MAE rises to $185\text{ kg/h}$ on uncalibrated hulls. However, an uncalibrated physics model with bounded, explainable error is infinitely safer than an extrapolating ML model that might predict unphysical negative power."
* **What NOT to Say:**  
  *Never say:* "The ML model works on any ship out of the box."
* **Confidence Level:** **HIGH**.

---

## Question 14: "What happens if your fuel prediction is wrong?"
* **Scientifically Correct Answer:**  
  "Our system includes a multi-layered safety barrier: First, the `SafeFuelObjective` clamps predictions between empirical naval architectural minimums and maximum engine fuel rack limits. Second, the CVaR uncertainty model accounts for predictive variance ($\sigma \approx 246\text{ kg/h}$) across weather states. Third, the output presented to the fleet manager is decision support—displaying expected fuel burn alongside confidence intervals—allowing the master mariner to adjust voyage reserves."
* **Evidence:**  
  `prediction/inference.py`, `audit/adversarial_objective_test.md`.
* **Strongest Attack Point:**  
  "If your prediction is 15% off, your schedule and bunkering plan fails."
* **Response to Attack Point:**  
  "Our MAPE is $14.63\%$, which is well within standard industry noon-report variance ($\pm 15\%$). Bunkering reserves in maritime operations include a standard 10–15% safety margin, which our decision-support interface explicitly calculates."
* **What NOT to Say:**  
  *Never say:* "Our model is 99% accurate and never wrong."
* **Confidence Level:** **HIGH**.

---

## Question 15: "Can the operator understand why the system selected a vessel/fuel/speed?"
* **Scientifically Correct Answer:**  
  "Yes. Instead of a single 'black-box' recommendation, our decision-support interface displays four explainable Pareto-optimal operational strategies: Strategy A (Minimum Fuel / Slow Steaming), Strategy B (Minimum OPEX / Conventional Fuel), Strategy C (Greenest / Bio-Methanol + Shore Power), and Strategy D (Balanced Robust / Tail-Risk Mitigated). For every strategy, a breakdown card shows the exact fuel cost, carbon tax liability, delay risk, and constraint margins, allowing the superintendent to understand the trade-offs."
* **Evidence:**  
  `PHASE4_SIH_STORY.md` §4, Decision card mockups in documentation.
* **Strongest Attack Point:**  
  "Explainability in the UI doesn't explain how the neural network or GBDT made its prediction."
* **Response to Attack Point:**  
  "The GBDT predicts only the residual delta over Holtrop-Mennen physics. Because the underlying physics model decomposes resistance into friction, wave-making, and aerodynamic drag, the superintendent can see physical power requirements directly, while feature attributions (SHAP values) explain the operational residual."
* **What NOT to Say:**  
  *Never say:* "The AI automatically knows the best route so explanation is unnecessary."
* **Confidence Level:** **HIGH**.

---

## Question 16: "What happens if the API or prediction model fails?"
* **Scientifically Correct Answer:**  
  "The architecture has a deterministic physical fallback hierarchy: If the LightGBM ML inference engine fails, throws an exception, or encounters corrupted input, the evaluator falls back directly to the analytic Holtrop-Mennen naval physics engine. If telemetry feeds drop out, the ingestion pipeline activates median and Kalman imputation."
* **Evidence:**  
  `audit/telemetry_corruption_test.md`, `audit/failure_injection.md`.
* **Strongest Attack Point:**  
  "Have you tested live server failure during optimization?"
* **Response to Attack Point:**  
  "Yes. In our failure injection test (`audit/failure_injection.md`), dropping the surrogate inference service caused zero crashes: 100% of candidate evaluations fell back to analytic hydrodynamic resistance."
* **What NOT to Say:**  
  *Never say:* "The system is running on distributed cloud so it cannot fail."
* **Confidence Level:** **HIGH**.

---

## Question 17: "Can the system operate without the QI module?"
* **Scientifically Correct Answer:**  
  "Yes. The optimization engine is decoupled through the abstract `BaseFleetOptimizer` interface. The system operates fully using classical MODE / DE, NSGA-III, or standard GA. In fact, for production deployment, we recommend the classical MODE engine."
* **Evidence:**  
  `src/algorithms/base.py`, `audit/FINAL_REPOSITORY_MAP.md` Component F.
* **Strongest Attack Point:**  
  "Then why did you spend months on quantum-inspired optimization?"
* **Response to Attack Point:**  
  "Because investigating and rigorously bounding whether quantum-inspired representations offer advantages in complex maritime combinatorial spaces was the specific scientific problem we set out to answer. Proving that classical DE is superior for continuous optimization while QI aids categorical diversity is a valuable, published scientific result."
* **What NOT to Say:**  
  *Never say:* "No, without the QI module the whole system collapses."
* **Confidence Level:** **ABSOLUTE**.

---

## Question 18: "What is the actual customer value?"
* **Scientifically Correct Answer:**  
  "The commercial value to a fleet operator is threefold: 1. Regulatory liability reduction: optimizing speed, fuel selection, and shore power to minimize FuelEU Maritime penalties (€2,400/t) and EU ETS allowance costs (€90/t); 2. Transparent multi-objective trade-offs between bunker fuel costs and schedule demurrage; 3. Data-driven voyage planning grounded in real high-frequency telemetry rather than static charter-party tables."
* **Evidence:**  
  `PHASE4_REGULATORY_MODEL.md`, `PHASE4_SIH_STORY.md`.
* **Strongest Attack Point:**  
  "Commercial shipping already uses voyage optimization software (e.g., WeatherNews, StormGeo, ZeroNorth)."
* **Response to Attack Point:**  
  "Commercial packages typically optimize individual voyages for conventional single-fuel ships against weather. Egreen Quanta focuses on heterogeneous fleet allocation across multi-fuel options (VLSFO, LNG, Bio-methanol), cold-ironing shore power selection, and compliance under 2024/2025 European statutory carbon pricing."
* **What NOT to Say:**  
  *Never say:* "We will put StormGeo and ZeroNorth out of business overnight."
* **Confidence Level:** **HIGH**.

---

## Question 19: "Is this optimization autonomous?"
* **Scientifically Correct Answer:**  
  "No. Egreen Quanta is strictly an advisory Decision Support System (DSS) for fleet superintendents, technical managers, and chartering desks. It generates feasible, Pareto-optimal operational strategies with full constraint compliance. The final voyage order is always issued by the human master mariner and shoreside superintendent."
* **Evidence:**  
  `audit/FINAL_CLAIM_LEDGER.md` Claim 20, `PHASE3_ARCHITECTURE.md`.
* **Strongest Attack Point:**  
  "If it's not autonomous, why do you need algorithms running in seconds?"
* **Response to Attack Point:**  
  "Because human dispatchers evaluate what-if scenarios in real time during chartering negotiations: 'What if port congestion delays berth by 12 hours? What if bunker fuel prices spike 20%?' A 6-second response allows interactive exploration, whereas overnight optimization does not."
* **What NOT to Say:**  
  *Never say:* "The system sends commands directly to the ship's autopilot and engine governor."
* **Confidence Level:** **ABSOLUTE**.

---

## Question 20: "What exactly have you invented?"
* **Scientifically Correct Answer:**  
  "We have not invented a new branch of mathematics. We have developed a scientifically validated, open-benchmark Decision Support platform that integrates:
  1. Real commercial high-frequency telemetry (FuelCast) calibrated to GBDT residual models over naval architectural hydrodynamics.
  2. A principled C0 bipartite Hungarian repair operator and Deb feasibility comparator that guarantees 100% feasibility in constrained fleet dispatch.
  3. An empirical boundary characterization showing that while Q-bit representations preserve discrete categorical entropy, classical DE is superior for continuous maritime optimization.
  4. An end-to-end statutory regulatory dispatch engine covering FuelEU Maritime, IMO CII, and EU ETS."
* **Evidence:**  
  Complete codebase `sih26138_platform`, 134/134 passing unit tests, and verified audit ledgers.
* **Strongest Attack Point:**  
  "So it's software engineering and benchmark auditing, not fundamental computer science."
* **Response to Attack Point:**  
  "Applied operations research and rigorous reproducibility engineering ARE fundamental science. Eliminating false quantum claims, correcting unfair benchmarks, and proving what works under identical mathematical controls is the highest standard of scientific integrity."
* **What NOT to Say:**  
  *Never say:* "We invented a revolutionary quantum paradigm."
* **Confidence Level:** **ABSOLUTE**.
