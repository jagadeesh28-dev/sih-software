# Limitations and Operational Boundaries
### SIH26138 — Egreen Quanta (v1.0.0)

This document transparently outlines the technical, scientific, and operational boundaries of Egreen Quanta.

---

## 1. Scientific & Modeling Limitations

1. **Absence of Zero-Shot Cross-Vessel Generalization:**
   - As proven in Phase 6 Leave-One-Vessel-Out (LOVO) benchmarking, naval hydrodynamic characteristics vary substantially across hulls. Deploying a model trained on `CPS_Poseidon` to `OSS_Ceto` increases prediction error by $3.4\times\text{ to }5.2\times$. Each vessel class must undergo initial calibration.
2. **Alternative Fuels are Thermodynamic Scenarios:**
   - Direct telemetry was measured exclusively on conventional marine fuels (VLSFO, MGO). Bunker flows for bio-methanol, green ammonia, and liquid hydrogen are calculated from mechanical shaft energy equivalence ($E_{shaft} = \int P_B dt$). They are validated physics-based thermodynamic simulations, not empirical green-fuel measurements.
3. **MPS Tensor Networks Inapplicable to Continuous Telemetry:**
   - Candidate `QI-C2` (Matrix Product State Tensor Train) suffered unconstrained gradient explosions on continuous tabular telemetry. The production path utilizes `QI-C1` (QIEA-FS + LightGBM), which is stable.
4. **Sea-State Sampling Limits:**
   - Historical telemetry predominantly covers sea states with significant wave height $H_s \le 5.5\text{ m}$. In severe storm conditions ($H_s > 6.0\text{ m}$), predictions will be flagged as `NEAR_BOUNDARY` or `OUT_OF_DOMAIN`, with widened uncertainty intervals.

---

## 2. Operational & Deployment Boundaries

1. **Human-in-the-Loop Requirement:**
   - Egreen Quanta is strictly a **Decision Support System (DSS)**. It does not interface directly with vessel throttle actuators or autopilot navigation computers. The shipmaster and fleet operational superintendent retain full authority and responsibility for all sailing commands.
2. **Telemetry Ingestion Latency:**
   - The production serving API processes single-point queries in $<5\text{ ms}$. However, real-time satellite telemetry feeds may experience communication dropouts. In such events, the system maintains dead-reckoning voyage estimates using calm-water physics.
3. **Port & Berth Weather Localities:**
   - Maneuvering inside sheltered harbors or during tug-assisted berthing involves transient engine dynamics not captured by steady-state hydrodynamic formulas. Predictions are intended for open-water transit legs.
