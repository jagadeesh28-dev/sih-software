# Slide 14: Defense of 22 Hostile Jury Questions (Evidence-Grounded)

## Questions 1–4: Explicit Vessel-Type Feature

### Q1: Where exactly is `vessel_type` used in the prediction model?
**Evidence-Grounded Answer**: In `models/qi_c1_vessel_type.txt` and `src/qi_prediction/serving.py` (lines 142–185). It is the 7th input feature in the booster tree structure, used directly at decision splits alongside continuous hydrodynamics (speed through water, draft, displacement, wind, wave).

### Q2: How do you encode vessel type?
**Evidence-Grounded Answer**: Deterministic integer categorical encoding defined in `models/qi_c1_vessel_type_meta.json`:
- `0`: `passenger_cruise` (*CPS_Poseidon*)
- `1`: `passenger_cruise_small` (*CPS_Triton*)
- `2`: `offshore_supply` (*OSS_Ceto*)
Unknown string types are intercepted by `MODEL-REAL-04` domain guard fallback.

### Q3: Did `vessel_type` actually improve prediction?
**Evidence-Grounded Answer**: Overall fleet test MAE moved from $247.38 \pm 2.25\text{ kg/h}$ to $252.62 \pm 1.70\text{ kg/h}$ ($+5.24\text{ kg/h}$), and $R^2$ from $0.9490$ to $0.9478$ ($-0.0012$, a $0.13\%$ variance difference). However, on localized vessel calibration, *CPS_Triton* error **improved from $81.57\text{ kg/h}$ down to $80.42\text{ kg/h}$** (and $78.67\text{ kg/h}$ on Seed 42).

### Q4: If `vessel_type` did not improve overall fleet accuracy, why include it?
**Evidence-Grounded Answer**: Continuous features (displacement, draft, beam, length) already explain $94.9\%$ of fuel variance. Including explicit `vessel_type` satisfies SIH requirement compliance, enables explicit categorical routing in fleet simulation, and prevents hull-form confusion when displacement ranges overlap between small cruise and offshore vessels.

---

## Questions 5–7: Operational Cost Minimization

### Q5: How do you calculate operational cost?
**Evidence-Grounded Answer**: Executed via `optimization/sih_objective_engine.py`:
$$C_{\text{total}} = C_{\text{fuel}} + C_{\text{electricity}} + C_{\text{OPS}} + C_{\text{carbon}} + C_{\text{schedule}} + C_{\text{FuelEU}}$$
with strict component isolation and zero double-counting.

### Q6: What happens if fuel price changes?
**Evidence-Grounded Answer**: `OperationalCostEngine.evaluate()` accepts dynamic bunkering cost matrices. If VLSFO price doubles from $\$650/\text{t}$ to $\$1,300/\text{t}$, optimal cruising speed automatically shifts downward by $1.8\text{ kn}$ toward deeper slow-steaming.

### Q7: What happens if electricity/shore-power price changes?
**Evidence-Grounded Answer**: Shore-power cost $C_{\text{OPS}} = P_{\text{berth}} \cdot t_{\text{berth}} \cdot p_{\text{grid}} + C_{\text{connection}}$. If $p_{\text{grid}}$ exceeds auxiliary diesel generation cost, the optimizer selects auxiliary fuel unless zero-emission port regulations enforce mandatory cold ironing.

---

## Questions 8–10: Lifecycle GHG Accounting

### Q8: How do you calculate lifecycle GHG?
**Evidence-Grounded Answer**: Under IMO Resolution MEPC.391(81) & EU MRV:
$$\text{GHG}_{\text{WtW}} = \text{GHG}_{\text{WtT}} + \text{GHG}_{\text{TtW}} + \text{Slip}_{\text{slip}}$$
Using audited emissions intensities ($g\text{CO}_2\text{e}/\text{MJ}$) multiplied by lower heating value (LHV) and mass consumed.

### Q9: What is the difference between TtW and WtW?
**Evidence-Grounded Answer**:
- **Tank-to-Wake (TtW)**: Combustion emissions directly from the ship funnel (VLSFO: $3.114\text{ tCO}_2/\text{t fuel}$; Ammonia/Hydrogen: $0.00\text{ tCO}_2/\text{t fuel}$).
- **Well-to-Wake (WtW)**: Complete lifecycle including extraction, refining, transport, and bunkering (VLSFO: $3.590\text{ tCO}_2\text{e}/\text{t}$; Grey Ammonia: $3.80\text{ tCO}_2\text{e}/\text{t}$; Green Ammonia: $0.15\text{ tCO}_2\text{e}/\text{t}$).

### Q10: Are alternative-fuel emissions measured or modeled?
**Evidence-Grounded Answer**: Strictly **modeled thermodynamic scenario simulations** based on invariant shaft work ($E_{\text{shaft}} = m_{\text{fuel}} \cdot \text{LHV} \cdot \eta_{\text{eng}}$). They are NOT empirical sensor measurements from dual-fuel engines.

---

## Questions 11–15: Multi-Objective Fleet Optimization & Pareto Decisions

### Q11: Can the optimizer choose between fuel types?
**Evidence-Grounded Answer**: Yes. Decision variables encode discrete fuel mode selections per leg, subject to vessel fuel-system bunkering compatibility constraints.

### Q12: Can it choose shore power?
**Evidence-Grounded Answer**: Yes. Port berth modes evaluate auxiliary diesel vs OPS (Onshore Power Supply / Cold Ironing) based on grid carbon intensity and port mandate flags.

### Q13: Can the optimizer trade fuel savings against cost?
**Evidence-Grounded Answer**: Yes. When high carbon pricing or FuelEU penalties apply, higher-cost biofuels ($+\$300/\text{t}$) become cost-optimal by eliminating carbon surcharges ($\$90/\text{tCO}_2$).

### Q14: Can the optimizer trade cost against lifecycle GHG?
**Evidence-Grounded Answer**: Yes. Demonstrated in Scene 11: moving from point A ($\$49,385, 208.6\text{ t WtW}$) to point B ($\$89,850, 64.7\text{ t WtW}$) achieves a $69.0\%$ GHG reduction at an $\$81.9\%$ cost increase.

### Q15: Show me a Pareto solution.
**Evidence-Grounded Answer**: Generated in `results/pareto_front.csv` via NSGA-III (50 non-dominated points). Compromise point: Speed $14.2\text{ kn}$, Cost $\$53,420$, WtW GHG $182.4\text{ tCO}_2\text{e}$, Delay $0.0\text{ hours}$.

---

## Questions 16–17: Algorithm Benchmarks & Quantum-Inspired Realism

### Q16: Which algorithm performs best?
**Evidence-Grounded Answer**: Based on our 30-seed benchmark in `results/algorithm_multiobjective_results.csv`:
- **Classical DE** performed best on constrained single-objective voyage fitness: $100\%$ feasibility, best fitness $3,976.84 \pm 24.12$, runtime $0.34\text{ s}$.
- **NSGA-III** performed best on multi-objective Pareto front generation: Hypervolume $0.762 \pm 0.018$.

### Q17: Does QI always beat classical optimization?
**Evidence-Grounded Answer**: **No.** In our voyage benchmark, Plain QPSO achieved $80.0\%$ feasibility and $12,203.14$ fitness, lagging Classical DE ($100\%$ feasibility, $3,976.84$). QIEA demonstrated superior bit-entropy exploration during feature selection ($+44.7\%$), but classical DE was superior on equality-constrained trajectory tuning. We report this without bias.

---

## Questions 18–22: Data Scope, Fallbacks & Operational Boundaries

### Q18: How many real vessels are represented?
**Evidence-Grounded Answer**: Exactly 3 commercial vessels: *CPS_Poseidon* (large cruise), *CPS_Triton* (small cruise), and *OSS_Ceto* (offshore supply), totaling $173,974$ audited telemetry records.

### Q19: What happens for a vessel not represented in training?
**Evidence-Grounded Answer**: The domain guard detects the out-of-domain vessel ID, issues an explicit OOD WARNING, widens conformal prediction intervals to maximum uncertainty bounds, and falls back to hydrodynamic hull reference curves (`MODEL-REAL-04`).

### Q20: What happens if the emission factor is missing?
**Evidence-Grounded Answer**: The engine automatically falls back to default IMO Resolution MEPC.391(81) and EU FuelEU Maritime reference tables, logging a non-critical configuration warning.

### Q21: What happens if fuel price is missing?
**Evidence-Grounded Answer**: The engine falls back to standard Rotterdam / Singapore bunkering indices stored in `configs/pricing_defaults.json`.

### Q22: Can this system autonomously control a vessel?
**Evidence-Grounded Answer**: **No.** It is strictly a human-in-the-loop decision-support system for master mariners and onshore superintendents. It possesses no direct actuator control and has not undergone maritime classification society Type Approval.
