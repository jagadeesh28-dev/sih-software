# Engineering Limitations, Risk Boundaries & Negative Results

> **OOD figures updated (FRESHLY COMPUTED):** the OOD guard was revalidated. Earlier figures in this document (e.g. 96.55% severe recall) are HISTORICAL and did not describe deployed behaviour. Current: 0.0% in-domain FPR; severe 100.0%, moderate 100.0% recall at d_env 1.50. See docs/ood_validation.md.

**System**: Egreen Quanta Decision-Support Platform  
**Audit Standard**: Transparent Scientific Accounting  
**Audit Date**: September 2026  

---

## 1. Domain & Operational Telemetry Boundaries

### 1.1 Limited Hull Geometries
The empirical validation of Egreen Quanta relies on continuous telemetry from three specific vessel hulls:
- `CPS_Poseidon`: Large cruise passenger vessel ($105,422$ records).
- `CPS_Triton`: Small cruise ferry ($25,347$ records).
- `OSS_Ceto`: Offshore platform supply vessel ($43,205$ records).

**Boundary**: The models have **not** been validated on bulk carriers, container mega-ships ($>15,000\text{ TEU}$), oil tankers (VLCCs), or inland waterways. Extrapolation to unrepresented hull forms without re-calibration will induce significant epistemic uncertainty.

### 1.2 Unmeasured Green-Fuel Telemetry
- **Limitation**: The telemetry dataset contains **zero empirical sensor records** for green alternative fuels (bio-methanol, green ammonia, liquid hydrogen).
- **Reality**: Commercial vessels operating on these fuels are exceptionally rare in global shipping.
- **System Posture**: All green fuel consumption and emissions outputs are **thermodynamic energy-equivalence scenario simulations** derived from invariant shaft work ($E = P_B \cdot t$). They must not be cited as measured real-world fuel rates.

---

## 2. Algorithmic Constraints & Negative Results

### 2.1 Matrix Product States (MPS) Tensor Network Failure
- **Experiment**: An explicit tensor-network regression architecture (Matrix Product State with bond dimension $\chi \in \{4, 8, 16\}$) was trained to predict residual fuel consumption.
- **Outcome**: The MPS model failed to achieve competitive training loss, suffered from numerical instability during gradient backpropagation through tensor contractions, and produced test $\text{MAE} > 800\text{ kg/h}$.
- **Honest Interpretation**: "The tested MPS tensor-network formulation was not viable under the evaluated training configuration." MPS is not claimed to be fundamentally impossible, but it is definitively unviable under current engineering constraints.

### 2.2 Rejection of Quantum Advantage Claims
- **Hardware Reality**: All algorithms in this repository run on standard x86-64 classical CPUs and GPUs.
- **No Quantum Speedup**: Quantum-inspired heuristics (QIEA, QPSO) simulate quantum phenomena (superposition, tunneling) using classical pseudorandom number generators.
- **Competitive Parity**: QIEA performs on statistical parity with Classical Genetic Algorithms ($p = 0.684$). Any claim of "quantum advantage" or "quantum supremacy" is scientifically unfounded and prohibited.

---

## 3. Uncertainty & OOD Guard Operational Boundaries

### 3.1 Wide High-Speed Uncertainty Intervals
- At operating speeds exceeding $16.0\text{ knots}$, hydrodynamic wave-making resistance increases with $v^4$ to $v^6$.
- Conformal prediction intervals at nominal $90\%$ coverage expand to $1,564.93\text{ kg/h}$ for QI-C1 and $2,273.70\text{ kg/h}$ for MODEL-REAL-04.
- **Operational Advisory**: Wide prediction intervals at high speeds reflect real physical turbulence and environmental stochasticity. Operators should treat high-speed point estimates as advisory ranges rather than exact scalar predictions.

### 3.2 OOD Guard as a Protective Screen, Not an Autopilot Guard
- The multi-dimensional envelope distance guard intercepts severe operational deviations ($d_{\text{env}} > 1.50$) with $96.55\%$ recall.
- **Boundary**: Passing the OOD check simply indicates that the operational state lies within the training envelope; it does **not** prove that the ship is navigating safely or that sea conditions are benign.

---

## 4. Certification & Autonomous Control Prohibition
- **PROHIBITION**: Under no circumstances should Egreen Quanta be connected to a ship's autopilot, engine throttle governor, or automated dynamic positioning (DP) system.
- **REGULATORY STATUS**: The software has not undergone classification society certification (e.g., DNV, Lloyd's Register, ABS, ClassNK) or IMO MSC/MEPC formal approval.
- **PERMITTED USE**: The system is strictly authorized as an **offline, advisory decision-support prototype** to assist shoreside fleet managers and on-board chief engineers with voyage planning and emissions benchmarking.
