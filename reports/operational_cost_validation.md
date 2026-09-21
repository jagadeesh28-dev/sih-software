# Scientific Validation Report: Operational Cost Minimization Objective (SIH26138)

## 1. Executive Summary
Under SIH26138, fleet operations cannot be optimized solely on physical fuel mass. Real-world fleet deployment requires an executable operational expenditure (OPEX) objective reflecting fluctuating bunker costs, port electricity tariffs, carbon pricing instruments (EU ETS), and charter demurrage penalties.

This report documents the mathematical formulation, implementation, unit testing, and empirical evaluation of the **Operational Cost Objective** in `SIHObjectiveEngine`.

---

## 2. Mathematical Formulation
The voyage operational cost is defined by a strictly non-overlapping additive formulation:

$$C_{\text{total}} = C_{\text{fuel}} + C_{\text{OPS}} + C_{\text{carbon}} + C_{\text{schedule}} + C_{\text{FuelEU}}$$

### Term Definitions and Accounting Boundaries
1. **Fuel Bunker Cost ($C_{\text{fuel}}$)**:
   $$C_{\text{fuel}} = m_{\text{fuel}} \cdot P_{\text{bunker}}(f)$$
   where $m_{\text{fuel}}$ is the total fuel consumed (tonnes), and $P_{\text{bunker}}(f)$ is the scenario price per tonne ($/t) derived from `configs/fuels.yaml`.
2. **Onshore Power Supply Cost ($C_{\text{OPS}}$)**:
   $$C_{\text{OPS}} = \begin{cases} (P_{\text{hotel}} \cdot t_{\text{berth}} \cdot P_{\text{electricity}}) + F_{\text{connect}} & \text{if OPS enabled and vessel compatible} \\ 0 & \text{otherwise} \end{cases}$$
   where $P_{\text{hotel}}$ is the auxiliary hoteling load (kW), $t_{\text{berth}}$ is port duration (hours), $P_{\text{electricity}}$ is the port power tariff ($/kWh), and $F_{\text{connect}}$ is the fixed connection fee.
3. **Carbon Pricing / EU ETS Cost ($C_{\text{carbon}}$)**:
   $$C_{\text{carbon}} = E_{\text{fossil\_CO2}} \cdot P_{\text{carbon}} \cdot \alpha_{\text{ETS\_scope}}$$
   where $E_{\text{fossil\_CO2}}$ is the combustion $\text{CO}_2$ from fossil fuel fractions (tonnes), $P_{\text{carbon}}$ is the carbon price ($90.00/t $\text{CO}_2$), and $\alpha_{\text{ETS\_scope}}$ is the regulatory geographic scope factor ($1.0$ intra-EU, $0.5$ extra-EU). Biogenic $\text{CO}_2$ (e.g. from bio-methanol) is explicitly zero-rated under EU ETS rules.
4. **Schedule / Demurrage Penalty Cost ($C_{\text{schedule}}$)**:
   $$C_{\text{schedule}} = \max(0.0, t_{\text{voyage}} - t_{\text{deadline}}) \cdot R_{\text{penalty}}$$
   where $R_{\text{penalty}}$ is the hourly demurrage rate ($2,500/hour).
5. **FuelEU Maritime Compliance Penalty ($C_{\text{FuelEU}}$)**:
   Penalizes voyages where the Well-to-Wake GHG intensity exceeds the regulatory compliance limit ($91.16\ \text{gCO}_2\text{e/MJ}$).

---

## 3. Configuration & Parameter Registry
The objective engine reads pricing dynamically from version-controlled configuration files without hardcoding:

| Fuel / Energy Carrier | Baseline Price | Unit | Source / Standard |
|:---|---:|:---:|:---|
| VLSFO (0.5% S) | $620.00 | USD / metric tonne | Global Bunker Index 2026 |
| MGO (0.1% S) | $850.00 | USD / metric tonne | Rotterdam/Singapore Average |
| Fossil LNG | $750.00 | USD / metric tonne | Henry Hub + Liquefaction |
| Bio-Methanol | $1,050.00 | USD / metric tonne | Renewable Methanol Scenario |
| Green Ammonia | $1,100.00 | USD / metric tonne | Green Hydrogen Carrier Projections |
| Liquid Hydrogen | $4,200.00 | USD / metric tonne | Cryogenic Storage Projections |
| Port Grid Electricity | $0.18 | USD / kWh | EU Port OPS Tariff Average |
| Port OPS Fixed Fee | $500.00 | USD / port call | Typical Terminal Shore Connection |
| Carbon Price (EU ETS) | $90.00 | USD / t $\text{CO}_2$ | EU ETS Compliance 2026 |

---

## 4. Empirical Validation & Price Sensitivity
The implementation was audited for exact dimensional linearity and zero double-counting across unit tests in `tests/test_sih_requirements.py`:

### Sensitivity Analysis Results
1. **Bunker Price Elasticity**:
   - Baseline VLSFO ($620/t): $C_{\text{fuel}} = \$15,500.00$ on 25.0 t.
   - Scenario A ($600/t): $C_{\text{fuel}} = \$15,000.00$.
   - Scenario B ($900/t): $C_{\text{fuel}} = \$22,500.00$.
   - Result: Linear scaling verified ($\Delta C / \Delta P = m_{\text{fuel}}$).
2. **Carbon Price Sensitivity**:
   - $P_{\text{carbon}} = \$50.00/t$: $C_{\text{carbon}} = \$3,942.75$.
   - $P_{\text{carbon}} = \$120.00/t$: $C_{\text{carbon}} = \$9,462.60$.
   - Result: Linear scaling verified without impact on auxiliary or demurrage terms.
3. **Shore Power Displacement**:
   - Utilizing OPS during a 5-hour berth with 1000 kW hotel load eliminated 1,050 kg of auxiliary MGO burn ($892.50) while incurring $1,400.00 in electricity and port fees, accurately reflecting port environmental compliance costs.

---

## 5. Conclusion
The operational cost objective is fully executable, mathematically rigorous, strictly configuration-driven, and seamlessly integrated into the multi-objective optimization suite.
