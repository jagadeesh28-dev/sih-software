# System Architecture: Egreen Quanta Production Platform
**Classification**: Controlled Decision-Support Prototype (SIH 2026 Ready)  
**Status**: 1.0.0-verified | **Audit Date**: September 2026  

---

## 1. End-to-End System Architecture

The complete runtime architecture of the Egreen Quanta platform follows a hardened, multi-tier pipeline designed to guarantee safety, transparency, and traceability:

```
                          REAL VESSEL TELEMETRY
                                    │
                                    ▼
                         INPUT VALIDATION LAYER
                   (Schema contracts, non-null, types)
                                    │
                                    ▼
                         PHYSICAL PLAUSIBILITY
                   (Hydrodynamic bounds, STW, draft)
                                    │
                                    ▼
                                OOD GUARD
                          (Envelope Distance)
                             /             \
                   IN-DOMAIN (dist ≤ 1.5)  OOD (dist > 1.5)
                            │                      │
                            ▼                      ▼
                       MODEL LAYER              REJECT /
                     ┌───────────┐             EMERGENCY
                     │           │
                   QI-C1    MODEL-REAL-04
                     │           │
                     └─────┬─────┘
                           ▼
                    UNCERTAINTY GATE
               (Conformal Interval Sharpness)
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          NORMAL        HIGH UNC.     INVALID
             │             │             │
             ▼             ▼             ▼
          SERVE QI      FALLBACK      PHYSICS
                     (MODEL-REAL-04) EMERGENCY
                           │
                           ▼
                  FUEL SCENARIO ENGINE
                           │
                           ▼
                 ALTERNATIVE-FUEL MODEL
             (Invariant Shaft Work: E = P_B*t)
                           │
                           ▼
                  EMISSIONS CALCULATOR
                  (WtT, TtW, WtW GHGs)
                           │
                           ▼
                   FLEET OPTIMIZATION
             (Multi-Objective DE / QPSO Engine)
                           │
                           ▼
                   HUMAN-IN-THE-LOOP
                   DECISION SUPPORT
```

---

## 2. Layer Specifications

### Layer 1: Input Validation & Sanitization
- **Purpose**: Strict barrier against malformed or malicious payloads.
- **Rules**: Rejects missing required keys (`stw_kn`, `draft_m`, `displacement_t`), `NaN`, `Inf`, and type mismatches. Normalizes categorical variables to canonical domain vocabulary (`vessel_type`, `fuel_type`).

### Layer 2: Hydrodynamic Physical Plausibility Gate
- **Purpose**: Enforces physical laws of naval architecture.
- **Rules**: Bounded checks on speed ($0 - 35\text{ kn}$), draught ($1 - 25\text{ m}$), displacement ($500 - 400,000\text{ t}$), wind ($0 - 60\text{ m/s}$), waves ($0 - 20\text{ m}$). Negative speeds and zero draught are rejected before invoking ML models.

### Layer 3: Empirical Out-of-Distribution (OOD) Guard
- **Purpose**: Detects operational drift and extreme weather beyond training hull experience.
- **Metric**: Multi-dimensional normalized envelope distance ($d_{\text{env}}$) calibrated on the $104,384$-record training set.
- **Action**: Core domain ($d_{\text{env}} \le 1.0$) allows normal serving; boundary states ($1.0 < d_{\text{env}} \le 1.5$) trigger reference fallback; severe states ($d_{\text{env}} > 1.5$) trigger emergency physics or rejection.

### Layer 4: Dual-Model Execution & Reference Cross-Check
- **Primary Path (`QI-C1`)**: 6 QIEA-selected features (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `fuel_type`) with LightGBM boosting on physics residuals.
- **Reference Anchor (`MODEL-REAL-04`)**: Full 14-feature hybrid physics model.
- **Cross-Check**: If $|\text{pred}_{\text{QI}} - \text{pred}_{\text{M04}}| > 500\text{ kg/h}$, the system routes to `MODEL-REAL-04` with `confidence: MEDIUM` and logs an operator warning.

### Layer 5: Conformal Uncertainty Calibration Gate
- **Method**: Inductive conformal prediction calibrated on $34,794$ forward temporal validation records.
- **Guarantee**: Satisfies nominal $90\%$ and $95\%$ marginal coverage floors ($93.56\%$ and $96.49\%$ empirical coverage on test split).
- **Sharpness Benefit**: QI-C1 produces $31.17\%$ narrower prediction intervals than the baseline ($1,564.93\text{ kg/h}$ vs $2,273.70\text{ kg/h}$).

### Layer 6: Alternative Fuel Engine (Invariant Shaft Work)
- **Principle**: Alternative fuels are evaluated as thermodynamic scenario simulations based on invariant delivered shaft work:
  $$E = P_B \cdot t = \dot{m}_f \cdot \text{LHV}_f \cdot \eta_f$$
  $$\dot{m}_{f,\text{alt}} = \frac{E}{\text{LHV}_{\text{alt}} \cdot \eta_{\text{alt}}}$$
- **Fuels Modeled**: VLSFO, MGO, Bio-Methanol, Green Ammonia, Liquid Hydrogen.

### Layer 7: Fleet Multi-Objective Optimization & Decision Support
- **Algorithms**: Differential Evolution (DE) for primary scalar fuel minimization; QPSO for diverse multi-objective Pareto front exploration.
- **Constraints**: Enforces voyage arrival deadlines, machinery power limits, and CII carbon intensity targets via Deb feasibility-first rules.
- **Human-in-the-Loop**: The platform strictly generates advisory recommendations; it does not interface with autopilot or engine governors.
