# Egreen Quanta — Final Release Checklist (SIH 2026)

**Release Classification**: `VERIFIED CONTROLLED RELEASE`  
**Release Version**: `v1.1.0-sih-complete`  
**System Type**: Controlled Maritime Decision-Support Prototype  
**Evaluation Standard**: SIH26138 Problem Statement  

---

## 1. Release Verification Matrix (Gates G1–G16)

- [x] **G1 DATA**: Exactly 173,974 validated rows across 3 vessels (`CPS_Poseidon`: 105,422, `CPS_Triton`: 25,347, `OSS_Ceto`: 43,205). Exactly 12 trailing null rows cleanly removed; zero interior interpolation.
- [x] **G2 REPRODUCIBILITY**: Master reproduction scripts and deterministic random seed tracking (Seed 42, 1001–1030).
- [x] **G3 PREDICTION**: Baseline `MODEL-REAL-04` ($R^2 = 0.9503$, MAE = 246.91 kg/h) and `QI-C1` ($R^2 = 0.9500$, MAE = 244.86 kg/h) verified.
- [x] **G4 VESSEL-TYPE FEATURE**: Explicit unordered categorical `vessel_type` conditioning validated in `QI-C1-vessel-type` ($R^2 = 0.9478$, MAE = 252.62 kg/h) with 30-seed matched ablation and per-vessel breakdown. QIEA selected `vessel_type` in 7/30 seeds (23.3%).
- [x] **G5 UNCERTAINTY**: Split conformal prediction evaluated at nominal 90% level. `QI-C1-vessel-type` coverage = 93.24%, `MPIW` = 1,641.69 kg/h (27.80% sharper than baseline while exceeding nominal 90% floor).
- [x] **G6 OOD**: Evaluated on 2,000 real in-domain test samples (0.0% FPR) and synthetic scenarios. Unknown vessel types intercept with immediate domain warning and reference anchor fallback.
- [x] **G7 COST OBJECTIVE**: Executable operational cost objective ($C_{\text{total}} = C_{\text{fuel}} + C_{\text{OPS}} + C_{\text{carbon}} + C_{\text{schedule}} + C_{\text{FuelEU}}$) verified with zero double-counting across unit tests.
- [x] **G8 LIFECYCLE GHG OBJECTIVE**: Executable Well-to-Wake GHG objective under IMO MEPC.391(81) tracking $\text{WtT} + \text{TtW} + \text{methane slip}$ across 6 fuel pathways.
- [x] **G9 MULTI-OBJECTIVE OPTIMIZATION**: Evaluated across 5 controlled objective formulations (A: Fuel, B: Fuel+Cost, C: Fuel+GHG, D: Fuel+Cost+GHG, E: Full Schedule/Risk). Non-dominated Pareto frontier extracted to `results/pareto_front.csv`.
- [x] **G10 BENCHMARK**: 30-seed matched optimization benchmark comparing DE (100% feasibility, best fitness 3976.84), Plain QPSO (80% feasibility), Classical GA (70%), and NSGA-III (80%).
- [x] **G11 SCALABILITY**: Multi-dimensional scalability benchmark executed across $D \in \{18, 50, 100, 250, 500, 600\}$ confirming strictly linear $O(D)$ complexity ($<0.01$ ms per evaluation).
- [x] **G12 SAFETY**: 1,000/1,000 invalid stress tests safely rejected; 16/16 edge cases passed; unknown vessel types safely intercepted.
- [x] **G13 ALTERNATIVE FUELS**: Invariant Shaft Work thermodynamic equivalence ($E_{\text{shaft}} = m \cdot \text{LHV} \cdot \eta$) strictly labeled as "Scenario Estimate" rather than measured telemetry.
- [x] **G14 DEMO**: All 11 production demonstration scenes execute without error in `scripts/demo_scenarios.py`.
- [x] **G15 CLAIM CONSISTENCY**: Safe claims verified; prohibited terms ("quantum supremacy", "autonomous vessel control") strictly rejected.
- [x] **G16 TRACEABILITY**: End-to-end mapping from SIH requirement $\to$ formulation $\to$ implementation $\to$ test $\to$ benchmark $\to$ demo $\to$ metrics $\to$ claims.

---

## 2. Test Suite Confirmation
- Total Tests: **159 / 159 PASS** (0 failed)
- Test Command: `python -m pytest tests/`
- Demonstration Command: `python scripts/demo_scenarios.py` (11/11 Scenes PASS)
