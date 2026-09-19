# Slide 13: Roadmap & Future Work

## Technical Roadmap Post-SIH 2026

### Phase 1: Expansion of Real Fleet Telemetry
- Integrate NMEA 0183 / 2000 sensor streams from container carriers, bulk carriers, and chemical tankers.
- Ingest real dual-fuel (LNG / MGO) commercial telemetry.

### Phase 2: Adaptive Onboard Transfer Learning
- Implement Bayesian few-shot fine-tuning to calibrate the 6-feature model on new vessel hulls within 48 hours of sea trials.
- Real-time hull fouling resistance tracking via auto-calibrating physical residual offsets.

### Phase 3: Tensor-Network & Quantum Hardware Prototyping
- Re-examine tensor networks (MPS / TT) with advanced preconditioning, adaptive bond dimension pruning ($\chi$), and density matrix renormalization group (DMRG) optimizers.
- Explore hybrid quantum-classical algorithms on cloud QPUs (e.g., QAOA for discrete vessel routing).

### Phase 4: Full ECDIS Bridge Integration
- Package the decision-support pipeline into an Electronic Chart Display and Information System (ECDIS) overlay.
- Pursue marine classification society Type Approval (DNV / ClassNK / Lloyd's Register) for operational safety compliance.
