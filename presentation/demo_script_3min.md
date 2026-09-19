# Egreen Quanta: 3-Minute SIH 2026 Jury Demonstration Script

**System**: Controlled Maritime Decision-Support Prototype  
**Problem Statement**: SIH26138  
**Total Duration**: Exactly 180 Seconds (3 Minutes)  
**Presenter Directive**: Focus on executable engineering, live verification cards, and defensible scientific boundaries. Do NOT get lost in abstract quantum mathematics. Show the live system running.

---

## Timeline & Narration Breakdown

### [0:00 – 0:20] The Problem: Maritime Fuel Inefficiency & Regulatory Pressure
- **Speaker Action**: Step forward, point to title slide / terminal showing `Egreen Quanta`.
- **Spoken Narration**:
  > "Honorable Jury, global commercial shipping accounts for nearly 3% of global greenhouse gas emissions. Maritime operators face strict IMO Carbon Intensity Indicator (CII) targets, volatile bunker fuel prices, and severe weather uncertainties.
  > Existing onboard prediction tools either rely on static engine test bed curves that fail under dynamic sea states, or black-box ML models that hallucinate under extreme sea conditions without safety boundaries.
  > We present **Egreen Quanta** — a controlled decision-support platform that integrates real-world vessel telemetry, physics-informed guards, classical quantum-inspired search, and conformal uncertainty quantification to deliver safe, transparent fleet optimization."

---

### [0:20 – 0:45] The Architecture: Defense-in-Depth Pipeline
- **Speaker Action**: Show the architectural flow diagram (Terminal Scene 1).
- **Spoken Narration**:
  > "Rather than deploying an unconstrained neural network, our platform enforces a rigorous multi-stage pipeline:
  > Real-time vessel sensor telemetry first enters strict **Input Validation** and **Physical Plausibility Checks**.
  > An **Out-of-Distribution (OOD) Guard** continuously calculates the state's distance from our verified empirical envelope.
  > In-domain states are routed to our **Quantum-Inspired Predictor (QI-C1)** with paired reference cross-checks from our baseline **MODEL-REAL-04**.
  > Predictions pass through a calibrated **Split Conformal Uncertainty Gate**. If an extreme sea state or booster fault is detected, the system safely falls back to emergency first-principles physics.
  > Validated fuel predictions then drive our **Alternative Fuel Scenario Engine** and **Fleet Multi-Objective Optimizer**."

---

### [0:45 – 1:15] Fuel Prediction: Telemetry Ground Truth & Verification
- **Speaker Action**: Execute `python scripts/demo_scenarios.py` and highlight **Scene 1** and **Scene 2**.
- **Spoken Narration**:
  > "Let us look at live Scene 1. Here is the cruise vessel *CPS_Poseidon* cruising at 14.5 knots in light sea conditions.
  > Notice the live verification block:
  > **Prediction**: 2,740.86 kg/h of VLSFO.
  > **Model**: QI-C1.
  > **Status**: IN-DOMAIN with HIGH confidence.
  > **90% Conformal Range**: [1,958.39, 3,523.33] kg/h.
  > Notice that our uncertainty interval has a width of 1,564.93 kg/h — which is **31.2% sharper** than the standard baseline while provably preserving 93.56% empirical coverage.
  > In Scene 2, when schedule recovery demands an acceleration to 19.5 knots, fuel rate surges by +87.3% to 5,133.94 kg/h, faithfully reflecting cubic hydrodynamic resistance."

---

### [0:15 – 1:40] The Quantum-Inspired Component & Classical Benchmark
- **Speaker Action**: Advance terminal to **Scene 3** / display benchmark comparison table.
- **Spoken Narration**:
  > "A central question: *Why quantum-inspired, and what does it actually do?*
  > We make **no claims of quantum hardware or quantum advantage**. Our algorithm is a classical Quantum-Inspired Evolutionary Algorithm (QIEA) utilizing Q-bit probability vectors $[\alpha, \beta]^T$ and rotation gates for feature selection, combined with Quantum PSO for hyperparameter tuning.
  > We conducted a strict 30-seed matched benchmark against a classical Genetic Algorithm control:
  > Classical GA achieved 237.24 kg/h MAE; our QI-C1 achieved 237.96 kg/h MAE.
  > A Wilcoxon signed-rank test yields $p = 0.684$. This proves **statistical parity with classical methods**.
  > The tangible engineering benefit of the quantum-inspired representation is exploration diversity: QIEA maintained **+44.7% higher population bit-entropy diversity**, enabling it to discover a compact, physically interpretable 6-feature subset."

---

### [1:40 – 2:00] Alternative Fuels: Invariant Shaft Work Physics
- **Speaker Action**: Highlight **Scene 4** table in terminal.
- **Spoken Narration**:
  > "In Scene 4, we evaluate fleet decarbonization. We emphasize that our real sensor telemetry is from conventional marine fuel. Therefore, we do not claim measured green fuel data.
  > Instead, we evaluate alternative fuels using first-principles thermodynamic energy equivalence:
  > $E_{\text{shaft}} = P_B \cdot t = m_{\text{fuel}} \cdot \text{LHV}_f \cdot \eta_f$.
  > For the same delivered cruise shaft work, Liquid Hydrogen consumes 936.28 kg/h due to its high energy density, while Bio-Methanol requires 6,136.84 kg/h.
  > We strictly separate Tank-to-Wake from Well-to-Wake lifecycle emissions, providing operators with actionable scenario estimates."

---

### [2:00 – 2:20] Out-of-Distribution Interception & Safety Fallbacks
- **Speaker Action**: Highlight **Scene 5** (Storm) and **Scene 6** (Failure Injection).
- **Spoken Narration**:
  > "What happens when conditions turn dangerous?
  > In Scene 5, we inject a Beaufort 10 hurricane state: 33 knots speed and 14-meter wave height. The OOD guard detects an envelope distance of 1.37, triggers a WARNING, and reroutes away from QI-C1 to reference models. Across 2,000 real in-domain samples, our guard had a **0.0% false-positive rate**, while achieving **96.55% interception of severe OOD states**.
  > In Scene 6, we inject a runtime C++ memory fault into the booster. The safety supervisor catches the fault in under 2 milliseconds and automatically falls back to our secondary model. In total, the system passed 1,000 adversarial stress tests and 10 live fault injections."

---

### [2:20 – 2:45] Fleet-Level Multi-Objective Optimization
- **Speaker Action**: Highlight **Scene 7** (Fleet Optimization Output).
- **Spoken Narration**:
  > "In Scene 7, we scale from a single vessel to a heterogeneous 3-vessel fleet across multi-leg cargo itineraries under port arrival deadlines.
  > Using a frozen benchmark of 825,000 evaluations across 5 metaheuristics, our optimizer identifies optimal speed profiles [13.8 kn, 14.2 kn, 12.5 kn] that eliminate port deadline penalties while reducing fleet fuel consumption.
  > We maintain complete scientific honesty: we distinguish the penalized objective optimum (873.23 tonnes, which includes feasibility penalties) from the unconstrained physical fuel minimum (3.24 tonnes). The system provides advisory recommendations for human masters, not autonomous vessel control."

---

### [2:45 – 3:00] Conclusions, Honest Limitations & Reproducibility
- **Speaker Action**: Concluding slide / show `reproduce_release.py`.
- **Spoken Narration**:
  > "To conclude:
  > 1. Egreen Quanta is a **verified controlled release** with complete Git SHA traceability and deterministic 10/10 automated release gates.
  > 2. We openly document our limitations: we evaluated 3 commercial vessels, green fuels are scenario-based, and direct tensor-network MPS models proved unviable during research.
  > 3. Every metric you saw today is reproducible with a single command: `python reproduce_release.py`.
  > Thank you, and we welcome your questions!"
