# Egreen Quanta — Final Release Checklist (SIH 2026)

**Release Classification**: `VERIFIED CONTROLLED RELEASE`  
**System Type**: Controlled Maritime Decision-Support Prototype  
**Evaluation Standard**: SIH26138 Problem Statement  

---

## 1. Release Verification Matrix

- [x] **Dataset verified**: Exactly 173,974 validated rows across 3 vessels (`CPS_Poseidon`: 105,422, `CPS_Triton`: 25,347, `OSS_Ceto`: 43,205). Exactly 12 trailing null rows cleanly removed; zero interior interpolation.
- [x] **Dataset hash verified**: SHA256 hashes of all 3 Parquet files match between disk, manifest, and release gate.
- [x] **Model hash verified**: `model_real_04.txt`, `qi_c1.txt`, `domain_checker.json`, and `conformal_quantiles.json` hashes match.
- [x] **QI-C1 verified**: Seed 42 MAE = 244.86 kg/h ($R^2 = 0.9500$); 30-seed matched mean MAE = 237.96 ± 5.46 kg/h ($R^2 = 0.9530 \pm 0.0018$). Canonical 6 QIEA features (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `fuel_type`).
- [x] **Baseline verified**: `MODEL-REAL-04` Seed 42 MAE = 246.91 kg/h ($R^2 = 0.9503$); 30-seed matched mean MAE = 248.12 ± 0.81 kg/h ($R^2 = 0.9501 \pm 0.0003$).
- [x] **Phase 6/7 reconciliation verified**: Resolved historical reporting discrepancies. Point evaluation vs 30-seed matched means distinguished; categorical `fuel_type` feature confirmed included in canonical 6 QIEA subset.
- [x] **Uncertainty verified**: Split conformal prediction evaluated at nominal 90% level. `QI-C1` coverage = 93.56%, `MPIW` = 1,564.93 kg/h (31.17% sharper than baseline `MODEL-REAL-04` coverage = 95.05%, `MPIW` = 2,273.70 kg/h).
- [x] **OOD verified**: Evaluated on 2,000 real in-domain test samples (0.0% FPR) and 1,998 synthetic scenarios. Severe OOD recall = 96.55% at primary threshold $d_{\text{env}} = 1.50$ and 100.0% at warning threshold $d_{\text{env}} = 1.00$.
- [x] **Safety verified**: 1,000/1,000 invalid stress tests safely rejected (100.0%); 16/16 edge cases passed; 10/10 failure injections safely recovered.
- [x] **Optimizer verified**: 825,000 evaluations frozen (Phase 5). Distinction maintained between penalized objective optimum ($J^*_{\text{pen}} \approx 873.2265\text{ t}$) and pure physical grid minimum ($3.2369\text{ t}$).
- [x] **Alternative fuels verified**: Evaluated via invariant shaft work energy equivalence ($E_{\text{shaft}} = P_B \cdot t = m_f \cdot \text{LHV}_f \cdot \eta_f$); labeled strictly as "Scenario Estimate" rather than measured telemetry.
- [x] **Claim ledger verified**: All 7 non-negotiable claim rules verified compliant. Prohibited terms ("quantum advantage", "quantum computer", "quantum supremacy", "autonomous controller") rejected across all documentation.
- [x] **README verified**: Top-level README accurately reflects system architecture, verified metrics, limitations, reproduction steps, and decision-support classification.
- [x] **Demo verified**: All 7 production demonstration scenes execute without error in `scripts/demo_scenarios.py` with jury-friendly prediction summary cards.
- [x] **SIH presentation content verified**: 14 presentation slides (`01_problem.md` through `14_jury_questions.md`) created and structured.
- [x] **Jury questions prepared**: 40+ rigorous questions with Short Answer, Technical Answer, and Grounded Metric Evidence in `presentation/jury_questions.md`.
- [x] **Reproduction works**: Master reproduction script `reproduce_release.py` and `scripts/release_gate.py` pass all 10 release gates (G1–G10) in under 2 seconds.
- [x] **All tests pass**: Complete test suite passes cleanly under pytest.
- [x] **Git tree clean**: Working directory clean and synchronized.
- [x] **Final SHA recorded**: Commit SHA recorded and verified in release manifest and reproduction summary.
- [x] **Release manifest matches final SHA**: `release/release_manifest.json` tracks the exact final commit SHA.
