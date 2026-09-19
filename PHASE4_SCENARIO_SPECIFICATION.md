# PHASE 4 SCENARIO SPECIFICATION
## Egreen Quanta / SIH26138: Heterogeneous Fleet, Uncertainty-Aware & Scientifically Defensible Optimization

**Provenance**: `REAL_TELEMETRY_CALIBRATED` / `SYNTHETIC_OPERATIONAL_SCENARIO`  
**Repository**: `sih26138_platform`  
**Date**: September 2026  

---

## 1. Fleet Vessel Profiles (`REAL_TELEMETRY_CALIBRATED`)

All three fleet vessels are anchored in physical real-world telemetry from the FuelCast industrial dataset. Naval architectural characteristics, capacity limits, and authorized fuel pathways are defined below:

| Vessel Identifier | Vessel Name | Class Family | Gross Tonnage (GT) | Deadweight (DWT, t) | Design Draft (m) | Full Displacement (t) | Operating Speed Envelope (kn) | Hotel Load (kW) | Authorized Fuel Pathways | Deck Cargo Capable | Pax Cap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`CPS_Poseidon`** | Crown Princess Poseidon | `passenger_cruise` | 70,000 | 8,500 | 7.5 | 42,000 | 8.0 – 22.0 | 6,500 | VLSFO, Fossil LNG, Bio-methanol | No | 3,800 |
| **`CPS_Triton`** | Coastal Princess Triton | `passenger_cruise_small` | 11,000 | 1,800 | 5.0 | 8,500 | 6.0 – 18.0 | 1,800 | VLSFO, Bio-methanol | No | 1,400 |
| **`OSS_Ceto`** | Ocean Supply Ship Ceto | `offshore_supply` | 24,000 | 5,200 | 6.0 | 6,000 | 4.0 – 15.0 | 800 | VLSFO, MGO, Bio-methanol, Green Ammonia | Yes | 0 |

### Fuel Pathway Compatibility Matrix:
- **`CPS_Poseidon`**: Authorized for VLSFO, Fossil LNG, and Bio-methanol. Green Ammonia and Liquid Hydrogen are **strictly prohibited** due to passenger cruise safety regulations (toxic gas dispersion hazard).
- **`CPS_Triton`**: Authorized for VLSFO and Bio-methanol. Cryogenic LNG and Ammonia storage are **prohibited** due to small hull volumetric constraints.
- **`OSS_Ceto`**: Authorized for VLSFO, MGO, Bio-methanol, and Green Ammonia. Cryogenic LH2 is **prohibited**.

---

## 2. Operational Cargo Demands (`SYNTHETIC_OPERATIONAL_SCENARIO`)

Three distinct maritime commercial demands must be fulfilled by the fleet. All three demands must be scheduled with zero unserved demand:

| Demand ID | Service Name | Origin | Destination | Distance (nm) | Cargo Mass (t) | Passengers (pax) | Transit Deadline (hours) | Min Required Speed (kn) | Required Vessel Family | Commercial Cargo Type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`DEMAND-A`** | Mainline Luxury Cruise | Southampton | Bergen | 550.0 | 1,200 | 3,200 | 32.0 | 17.19 | `passenger_cruise` | Luxury cruise passengers |
| **`DEMAND-B`** | Fjord Eco-Expedition | Stavanger | Tromso | 680.0 | 450 | 1,100 | 48.0 | 14.17 | `passenger_cruise_small` | Coastal cruise passengers |
| **`DEMAND-C`** | Offshore Energy Deck Equipment | Aberdeen | Ekofisk Complex | 180.0 | 3,200 | 0 | 18.0 | 10.00 | `offshore_supply` | Heavy deck equipment |

### Assignment Feasibility Logic:
1. `DEMAND-A` (3,200 pax) can only be served by `CPS_Poseidon` (3,800 pax capacity).
2. `DEMAND-B` (1,100 pax) can be served by `CPS_Triton` (1,400 pax capacity) or `CPS_Poseidon`.
3. `DEMAND-C` (3,200 t deck cargo) can only be served by `OSS_Ceto` (5,200 DWT and deck-cargo certified).
4. Assigning `DEMAND-C` to cruise ships or `DEMAND-A` to `OSS_Ceto` results in hard constraint violation penalties ($P = 100,000$).

---

## 3. Weather Scenarios & Probabilities (`SYNTHETIC_OPERATIONAL_SCENARIO`)

Environmental conditions represent realistic North Sea / Norwegian Sea operations. All environmental parameters are strictly bounded to remain within the empirical domain envelope ($H_s \le 3.5\text{ m}$):

| Scenario ID | Descriptive Name | Significant Wave Height $H_s$ (m) | Peak Wave Period $T_p$ (s) | Wind Speed $V_w$ (m/s) | Wind Dir (deg) | Current Speed $V_c$ (m/s) | Current Dir (deg) | Water Depth $d_w$ (m) | Scenario Probability $p_s$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SCEN-W1`** | Calm Sea / Gentle Breeze | 1.0 | 5.5 | 4.0 | 45.0 | 0.2 | 30.0 | 120.0 | 0.35 |
| **`SCEN-W2`** | Moderate Sea / Fresh Breeze | 1.8 | 7.0 | 8.5 | 90.0 | 0.5 | 60.0 | 120.0 | 0.35 |
| **`SCEN-W3`** | Rough Sea / Strong Breeze | 2.6 | 8.2 | 12.0 | 180.0 | 0.7 | 120.0 | 120.0 | 0.20 |
| **`SCEN-W4`** | Severe Sea / Near Gale | 3.4 | 9.5 | 14.5 | 225.0 | 0.9 | 180.0 | 120.0 | 0.10 |

---

## 4. Operational Modes & Cold-Ironing Rules

- **Transit Mode (`transit`)**: Normal open-water cruising with full auxiliary and propulsion power.
- **Maneuvering Mode (`maneuvering`)**: Port approach and departure navigation ($v \le 8\text{ kn}$).
- **Dynamic Positioning Mode (`dp`)**: Active station keeping for offshore supply operations.
- **Port Idle (`port`)**: Moored alongside. If Shore Power Cold-Ironing (`shore_power=1`) is active, auxiliary diesel generators are shut down, eliminating auxiliary fuel and port emissions, incurring grid electricity tariff ($0.22/kWh).
