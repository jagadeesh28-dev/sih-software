# Smart India Hackathon 2026: Final Executive Technical Report
**Project Title**: Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Problem Statement ID**: SIH26138  
**Release Level**: Verified Controlled Release (v1.0.0)  
**System Classification**: Controlled Maritime Decision-Support Prototype  
**Date**: September 2026  

---

## 1. Executive Summary & Problem Context
International maritime shipping carries over $80\%$ of global trade and generates over $1$ billion tonnes of $\text{CO}_2$ annually. Maritime operators must comply with stringent IMO regulatory regimes—including the Carbon Intensity Indicator (CII), Energy Efficiency Existing Ship Index (EEXI), and the EU Emissions Trading System (EU ETS)—or face severe financial penalties and port detention.

Existing maritime software solutions suffer from a stark dichotomy:
1. **Traditional Physics Estimators**: Fast but inaccurate, exhibiting errors exceeding $1,500\text{ kg/h}$ due to unmodeled hull fouling and non-linear sea-state dynamics.
2. **Black-Box Deep Learning**: Vulnerable to unphysical predictions, extreme out-of-distribution hallucinations during oceanic storms, and catastrophic failure modes with zero fallback mechanisms.

**Egreen Quanta** bridges this divide. We present a production-hardened, scientifically auditable decision-support platform that combines:
- A **hybrid physics-guided residual predictor** anchoring machine learning to hydrodynamic laws.
- **Quantum-inspired combinatorial optimization** (QIEA and QPSO) for feature selection and diverse multi-objective Pareto front exploration.
- **Inductive conformal prediction** providing finite-sample guaranteed uncertainty intervals.
- A **multi-dimensional domain guard** intercepting out-of-distribution storm states.
- A **thermodynamic invariant shaft-work engine** simulating alternative green fuel scenarios.

---

## 2. Core Scientific Contributions

### 1. Hybrid Hydrodynamic Residual Modeling
Rather than predicting raw fuel consumption directly, Egreen Quanta predicts the **hydrodynamic residual** between measured telemetry and first-principles Holtrop-Mennen resistance equations:
$$\hat{y}_{\text{total}}(\mathbf{x}) = f_{\text{phys}}(\mathbf{x}) + \hat{r}_{\text{ML}}(\mathbf{x})$$
This guarantees that predictions respect physical scaling laws across speeds, draughts, and weather conditions.

### 2. Quantum-Inspired Combinatorial Optimization
- **Quantum-Inspired Evolutionary Algorithm (QIEA)**: Employs probabilistic qubit registers and rotation gates to explore the $2^{14}$ feature space, selecting a compact 6-feature subset that eliminates 8 redundant sensor channels while maintaining statistical parity with full 14-feature models.
- **Quantum-Behaved Particle Swarm Optimization (QPSO)**: Exploits delta-potential well wave-function sampling to maintain $+44.7\%$ higher population diversity ($H=0.2814$ vs $0.1945$), escaping local minima in non-convex multi-leg fleet routing.

### 3. Conformal Uncertainty & Sharpness
Using inductive conformal prediction calibrated on $34,794$ forward temporal records:
- Both `MODEL-REAL-04` ($95.05\%$) and `QI-C1` ($93.56\%$) exceed the $90.0\%$ nominal coverage floor.
- `QI-C1` achieves a **$31.17\%$ sharper prediction interval** ($1,564.93\text{ kg/h}$ vs $2,273.70\text{ kg/h}$), providing operators with tighter, actionable decision bounds.

---

## 3. The 7-Scene Demonstration Protocol
During jury presentation, the live demonstration script (`python scripts/demo_scenarios.py`) executes seven sequential scenes:
1. **Scene 1 — Normal Cruise**: Poseidon at $14.5\text{ kn}$, predicting $2,740.9\text{ kg/h}$ with $[1,958.4, 3,523.3]\text{ kg/h}$ range.
2. **Scene 2 — High Demand**: Acceleration to $19.5\text{ kn}$, demonstrating non-linear power scaling ($5,133.9\text{ kg/h}$).
3. **Scene 3 — Slow Steaming**: Speed reduction from $18.0$ to $15.0\text{ kn}$, demonstrating $24.8\%$ simulated scenario savings.
4. **Scene 4 — Alternative Green Fuels**: Energy-equivalent consumption and emissions across VLSFO, MGO, Bio-Methanol, Green Ammonia, and Liquid H2.
5. **Scene 5 — Injected OOD Storm State**: Extreme conditions ($H_s = 14\text{ m}$, wind $48\text{ m/s}$) intercepted by the domain guard and routed safely.
6. **Scene 6 — Fault Injection**: Simulated booster memory crash, gracefully falling back to `MODEL-REAL-04` with zero downtime.
7. **Scene 7 — Fleet Multi-Objective Optimization**: Heterogeneous vessel route and speed assignment achieving zero deadline violations.

---

## 4. Scientific Honesty & Release Gate Certification
In accordance with SIH engineering standards, this release strictly enforces scientific honesty:
- **Zero Quantum Supremacy Claims**: Algorithms are classical quantum-inspired heuristics; no quantum computers were used.
- **Statistical Parity**: QI-C1 is competitive with classical genetic algorithms ($p=0.684$), not universally superior.
- **Transparent Green Fuel Basis**: Alternative fuel values are explicitly labeled thermodynamic simulations, not empirical telemetry.
- **Prototype Status**: The system is an advisory decision-support prototype, not certified for autonomous ship control.

**Overall Release Gate Verdict**: **`VERIFIED CONTROLLED RELEASE` (10/10 Gates Passed)**.
