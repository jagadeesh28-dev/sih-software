# Slide 3: Frozen End-to-End System Architecture

## Architecture Flow Diagram

```text
                  REAL VESSEL TELEMETRY
                            |
                            v
                     INPUT VALIDATION
                            |
                            v
                  PHYSICAL PLAUSIBILITY
                            |
                            v
                        OOD GUARD
                            |
             +--------------+--------------+
             |                             |
         IN-DOMAIN                        OOD
             |                             |
             v                             v
        MODEL LAYER                    REJECT /
        |         |                   EMERGENCY
        |         |
      QI-C1   MODEL-REAL-04
        |         |
        +----+----+
             |
             v
      UNCERTAINTY GATE
             |
             +--------------+--------------+
             |                             |
           ACCEPT                   HIGH UNCERTAINTY
             |                             |
             v                             v
      QI-C1 / VERIFIED               MODEL-REAL-04
             |
             v
     FUEL SCENARIO ENGINE
             |
             v
  ALTERNATIVE FUEL SCENARIOS
             |
             v
   EMISSIONS CALCULATION
             |
             v
MULTI-OBJECTIVE FLEET OPTIMIZATION
             |
             v
HUMAN-IN-THE-LOOP DECISION SUPPORT
```

---

## Architectural Principles & Boundaries
1. **Hierarchical Routing**: Models never predict in a vacuum; every inference is preceded by domain validation and followed by uncertainty verification.
2. **Dual-Model Cross-Check**: Both QI-C1 (6 features) and MODEL-REAL-04 (14 features) evaluate the state in parallel; large discrepancies trigger operator warnings.
3. **Graceful Degradation**: Sensor fault $\rightarrow$ fall back to reference model; Severe storm $\rightarrow$ fall back to first-principles hydrodynamic bounds.
4. **Advisory Decision Support**: The platform outputs recommendations and trade-off frontiers for ship masters and fleet operations; it is **not** an autonomous vessel controller.
