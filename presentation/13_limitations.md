# Slide 13: Transparent Scientific Limitations & Negative Findings

## 1. Non-Negotiable Empirical Limitations

1. **Three Real Hulls Only**:
   - Training and validation rely on three specific commercial vessels (*CPS_Poseidon*, *CPS_Triton*, *OSS_Ceto*).
   - Zero-shot transfer to unmodeled hull forms (e.g., container vessels, bulk carriers, VLCCs) requires vessel-specific recalibration.
2. **Alternative Fuels are Scenario Models**:
   - Bio-Methanol, Green Ammonia, and Hydrogen consumption are thermodynamic scenario models based on invariant shaft work ($E_{\text{shaft}} = m \cdot \text{LHV} \cdot \eta_{\text{eng}}$).
   - They are NOT directly measured sensor telemetry from retrofitted dual-fuel engines.
3. **Severe OOD Hurricane States are Synthetic**:
   - In-domain conditions are 100% verified real telemetry.
   - Extreme storm states ($H_s > 10\text{ m}$, wind $> 35\text{ m/s}$) are synthetic boundary simulations generated for safety margin validation.
4. **Human-in-the-Loop Prototype**:
   - The platform is an advisory decision-support tool for master mariners and fleet superintendents.
   - It is NOT certified for autonomous ship maneuvering (lacks DNV/IMO Type Approval).

---

## 2. Rigorous Negative Findings & Honest Benchmarks

### Negative Finding 1: Matrix Product State (MPS) Tensor Network Unviability
- **Hypothesis Tested**: Direct Matrix Product State (MPS) tensor networks could compress maritime time-series features while improving predictive accuracy.
- **Empirical Result**: Severe numerical instability during optimization, slow training convergence, and MAE inferior to gradient boosted decision trees.
- **Action Taken**: Formally documented as an unviable architecture and excluded from the production serving pipeline.

### Negative Finding 2: Classical DE Outperforms Plain QPSO on Constrained Fleet Formulation
- **Hypothesis Tested**: Plain Quantum-Inspired Particle Swarm Optimization (QPSO) would outperform classical Differential Evolution (DE) across voyage scheduling.
- **Empirical Result**:
  - Classical DE achieved **$100.0\%$ feasibility** and best fitness of **$3,976.84$**.
  - Plain QPSO achieved **$80.0\%$ feasibility** and fitness of **$12,203.14$** under strict laytime window equality constraints.
- **Scientific Disclosure**: We report this finding honestly. No quantum superiority or algorithmic dominance is claimed. Classical DE remains the recommended solver for strict schedule equality constraints.

### Negative Finding 3: `vessel_type` Explains Limited Incremental Variance
- In QIEA feature search, `vessel_type` was selected in only $7 / 30$ seeds ($23.3\%$).
- Continuous hydrodynamics (displacement, draft, beam, length) already capture $94.9\%$ of fuel variance; `vessel_type` acts as a discrete partitioner with slight local benefit for *CPS_Triton* ($-1.15\text{ kg/h}$), rather than an orthogonal variance source.
