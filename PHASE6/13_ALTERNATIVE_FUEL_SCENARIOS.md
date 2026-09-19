# PHASE 6 — STEP 13: ALTERNATIVE FUEL SCENARIO MODELING & EMISSIONS ACCOUNTING
## SIH26138 — Egreen Quanta
### Thermodynamic Energy Equivalent Transformation, Well-to-Wake (WtW) Emissions, and Regulatory Scenarios

**Date:** September 19, 2026  
**Auditor:** Maritime Propulsion Specialist, Regulatory Emissions Auditor  
**Scientific Discipline Enforcement:**  
> **MANDATORY SCIENTIFIC INTEGRITY RULE:**  
> The 173,974 real telemetry records in this platform represent conventional fossil fuels (VLSFO, MGO, Marine Diesel).  
> Alternative fuel calculations (LNG, Green Methanol, Green Ammonia, Liquid Hydrogen) are **NOT EMPIRICALLY VALIDATED SENSOR PREDICTIONS**.  
> They are formally classified as: **PHYSICS-BASED THERMODYNAMIC SCENARIOS**.

---

## 1. Thermodynamic Energy Equivalency Formulation

Rather than predicting alternative fuel mass flow via a naive black-box model, the system leverages the invariant mechanical energy required to propel the hull:

$$E_{shaft} = \int_{0}^T P_B(t) \, dt \quad [\text{kWh}]$$

Because mechanical resistance $R_{total}$ and delivered shaft power $P_B$ depend solely on vessel hydrodynamics and metocean resistance, the required shaft energy $E_{shaft}$ is invariant to the fuel stored in the bunker tank.

The instantaneous fuel mass flow rate for any alternative fuel $f$ is derived from first-principles thermodynamics:
$$\dot{m}_f = \frac{P_B}{\text{LHV}_f \times \eta_f(L)} \times 3600 \quad [\text{kg/h}]$$
where:
- $P_B$ is the engine brake power ($\text{kW}$).
- $\text{LHV}_f$ is the lower heating value ($\text{MJ/kg}$).
- $\eta_f(L)$ is the brake thermal efficiency of the energy converter (internal combustion engine or PEM/SOFC fuel cell) as a function of engine load fraction $L = P_B / P_{MCR}$.

---

## 2. Documented Literature Parameters for Maritime Fuels

All scenario parameters are drawn directly from IMO Fourth GHG Study (2020) and FuelEU Maritime Regulation (EU) 2023/1805:

| Fuel Type | Fuel Code | Baseline State | Lower Heating Value ($\text{LHV}_f$, MJ/kg) | Engine / Converter Type | Brake Thermal Efficiency ($\eta_f$, nominal) | WtT Factor ($g\text{CO}_2e/\text{MJ}$) | TtW Factor ($g\text{CO}_2e/\text{MJ}$) | Total WtW Factor ($g\text{CO}_2e/\text{MJ}$) | Source Authority | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VLSFO** | `vlsfo` | Liquid (Conventional) | **41.0** | 2-Stroke Low-Speed Diesel | **48.5%** | 13.5 | 77.0 | **90.5** | IMO GHG 4 (2020) | **Empirically Validated (Ground Truth)** |
| **MGO** | `mgo` | Liquid (Conventional) | **42.7** | 4-Stroke Medium-Speed | **46.0%** | 14.4 | 75.0 | **89.4** | IMO GHG 4 (2020) | **Empirically Validated (Ground Truth)** |
| **LNG (Otto)** | `lng` | Cryogenic Liquid ($-162^\circ\text{C}$) | **48.0** | Dual-Fuel Otto Cycle | **47.0%** | 18.5 | 56.5 + Methane Slip | **78.2** | FuelEU Maritime Annex I | **PHYSICS-BASED SCENARIO** |
| **e-Methanol** | `e_methanol` | Liquid ($20^\circ\text{C}$) | **19.9** | Dual-Fuel Diesel Injection | **46.5%** | 5.2 (Renewable) | 68.8 (Biogenic) | **12.0 (Net)** | FuelEU Maritime Annex I | **PHYSICS-BASED SCENARIO** |
| **e-Ammonia** | `e_ammonia` | Liquid ($-33^\circ\text{C}$) | **18.6** | Dual-Fuel Ammonia Engine | **45.0%** | 8.5 (Renewable) | 0.0 + $\text{N}_2\text{O}$ Slip | **14.2 (Net)** | DNV Maritime Forecast 2050 | **PHYSICS-BASED SCENARIO** |
| **Liquid $\text{H}_2$** | `lh2` | Cryogenic Liquid ($-253^\circ\text{C}$) | **120.0** | PEM Fuel Cell + Inverter | **55.0%** | 12.0 (Electrolysis) | 0.0 (Zero Tailpipe) | **12.0 (Net)** | IMO GHG 4 (2020) | **PHYSICS-BASED SCENARIO** |

---

## 3. Emissions Accounting Framework (TtW, WtT, WtW)

To prevent double counting and ensure full regulatory compliance, emissions are strictly partitioned into three independent layers:
1. **Tank-to-Wake (TtW):** Direct operational tailpipe emissions combustion from the ship's funnel:
   $$\text{GHG}_{TtW} = \dot{m}_f \times \text{LHV}_f \times \text{EF}_{TtW} \times 10^{-6} \quad [\text{tCO}_2\text{e/h}]$$
2. **Well-to-Tank (WtT):** Upstream extraction, refining, transport, bunkering, and leakage emissions prior to boarding the vessel.
3. **Well-to-Wake (WtW):** Full lifecycle intensity:
   $$\text{GHG}_{WtW} = \text{GHG}_{WtT} + \text{GHG}_{TtW}$$

### Regulatory Metric Isolation:
Regulatory indices are computed downstream and **NEVER** blended into the telemetry prediction loss function:
- **FuelEU Maritime Compliance Penalty:** Evaluated against the declining greenhouse gas intensity targets ($91.16\text{ gCO}_2\text{e/MJ}$ baseline declining to $-80\%$ by 2050).
- **EU ETS Maritime Cost:** Applied strictly to TtW operational $\text{CO}_2$ emissions ($100\%$ on intra-EU voyages, $50\%$ on extra-EU voyages) priced at $\$90/\text{tCO}_2$.
- **CII (Carbon Intensity Indicator):** Evaluated as $\text{AER} = \frac{\sum \text{Fuel} \times C_F}{\text{DWT} \times \text{Distance}}$ against IMO A–E rating thresholds.
