# Production Demonstration Scenarios
### SIH26138 — Egreen Quanta (v1.0.0)

Egreen Quanta includes five live demonstration scenarios executable via `python scripts/demo_scenarios.py`:

---

## Scenario 1: Normal Cruise Operation
- **Vessel Profile:** `CPS_Poseidon` (Container Ship)
- **Operational Conditions:** $STW = 14.5\text{ kn}$, $SOG = 14.2\text{ kn}$, Draft $= 8.5\text{ m}$, Displacement $= 25,000\text{ t}$, Wind $= 6.2\text{ m/s}$, Waves $H_s = 1.4\text{ m}$.
- **Engine Response:** Evaluated via primary engine `QI-C1` in `NORMAL` status.
- **Output:** Predicted fuel consumption rate of $1401.75\text{ kg/h}$ with $90\%$ conformal predictive interval $[523.84, 2279.66]\text{ kg/h}$ (envelope distance: $0.037$, in-domain).

---

## Scenario 2: High Propulsion Demand Surge
- **Operational Shift:** Speed accelerated from $14.5\text{ kn}$ to $19.5\text{ kn}$ ($+34.5\%$ speed increase).
- **Engine Response:** Fuel consumption increases sharply to $2806.72\text{ kg/h}$ ($+100.2\%$ increase from cruise).
- **Fleet Decision Support Action:** Demonstrates non-linear hydrodynamic cubic power relationship ($P \propto V^3$); recommends slow steaming to $15.0\text{ kn}$ to achieve $+24.8\%$ net fuel and emission reductions.

---

## Scenario 3: Alternative Fuel Decarbonization Comparison
- **Methodology:** Evaluated via invariant mechanical shaft work ($E_{shaft} = \int P_B dt$) with verified Lower Heating Values (LHV) and thermal conversion efficiencies.
- **Bunker Comparisons:**
  - **Conventional VLSFO (Baseline):** $1401.75\text{ kg/h}$ ($4.365\text{ tCO}_2/\text{h}$, FuelEU $91.6\text{ g/MJ}$ — Non-Compliant).
  - **Bio-Methanol (Renewable):** $3007.78\text{ kg/h}$ ($4.136\text{ tCO}_2/\text{h}$, FuelEU $15.2\text{ g/MJ}$ — Compliant).
  - **Green Ammonia (Zero-Carbon):** $3357.91\text{ kg/h}$ ($0.000\text{ tCO}_2/\text{h}$, FuelEU $8.5\text{ g/MJ}$ — Compliant).
  - **Liquid Hydrogen (Zero-Carbon):** $460.42\text{ kg/h}$ ($0.000\text{ tCO}_2/\text{h}$, FuelEU $5.0\text{ g/MJ}$ — Compliant).

---

## Scenario 4: Out-of-Distribution (OOD) Event & Safety Rejection
- **Injected Anomaly:** Speed $34.0\text{ kn}$, Draft $22.0\text{ m}$, Wind $48.0\text{ m/s}$, Waves $H_s = 14.0\text{ m}$ (far outside historical training domain).
- **Domain Guard Response:** Normalized envelope distance flagged ($dist = 1.49$); routed to reference fallback `MODEL-REAL-04` with operational boundary warning.
- **Severe OOD Guard:** Inputs exceeding critical distance threshold ($dist > 3.00$) are immediately halted and rejected to prevent ungrounded optimization exploitation.

---

## Scenario 5: Fault Injection & Zero-Downtime Fallback
- **Injected Condition:** Simulated complete failure/unavailability of primary `QI-C1` booster.
- **System Recovery:** Router intercepts failure within $0.01\text{ ms}$ and seamlessly falls back to frozen reference engine `MODEL-REAL-04`.
- **Outcome:** Continuous, uncorrupted fuel prediction ($1907.43\text{ kg/h}$) delivered without application crash or downtime.
