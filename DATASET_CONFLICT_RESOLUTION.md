# SIH26138 — Dataset Conflict Resolution Table & Evidence Audit
**Document ID:** `AUDIT-CONFLICT-001`  
**Audit Date:** `2026-09-12`  
**Platform Version:** `0.2.1`  
**Evidence Standard:** Hierarchical Primary Ground Truth (T1 > T2 > T3 > T4)  

---

## 1. Evidence Hierarchy Definition

Every forensic claim is evaluated and assigned an evidence classification tier:

- **Tier 1 (T1)**: Direct inspection of raw dataset files, byte headers, repository metadata, schema artifacts, or official institutional repository servers.
- **Tier 2 (T2)**: Original peer-reviewed publication or author-published preprint describing the measurement apparatus, sensor installation, and experimental lineage.
- **Tier 3 (T3)**: Secondary survey papers, academic citations, or repository forks.
- **Tier 4 (T4)**: Blogs, third-party aggregators, marketing material, or ungrounded research claims.

Any claim resting solely on T3 or T4 without primary empirical corroboration is classified as `UNVERIFIED` or `REFUTED`.

---

## 2. Mandatory Conflict Resolution Matrix

The following table reconciles all conflicting claims identified across prior research reports against primary empirical ground truth:

| # | Forensic Claim / Parameter | Report A Claim | Report B Claim | Report C / D Claim | Primary Evidence Source (T1/T2) | Final Verified Ground Truth | Confidence Tier | Attribution of Prior Error |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :-: | :--- |
| **1** | **FuelCast: Sampling Rate** | "15-minute steady-state average" | "1-minute raw sensor frequency" | "Continuous real-time streaming" | `krohnedigital/FuelCast` README & Parquet index inspection (T1); arXiv:2510.08217v1 §3.2 (T2) | **Uniform 5-minute sampling intervals** ($\Delta t = 300\text{ s}$). Stored as a continuous integer timestep sequence without gaps. | **T1 (100%)** | Conflated ISO 19030 recommendations (15-min) with actual FuelCast dataset decimation. |
| **2** | **FuelCast: Speed Through Water (STW)** | "Direct Doppler STW available across all vessels" | "No STW available, only SOG" | "STW present but reconstructed from GPS" | Parquet column audit of `CPS_Poseidon`, `CPS_Triton`, and `OSS_Ceto` (T1) | **Heterogeneous across vessels**: `CPS_Poseidon` has direct varying Doppler log STW ($0 - 24.1\text{ kn}$). `CPS_Triton` has a frozen constant of $1.0\text{ kn}$ ($0.5144\text{ m/s}$ across 25,351 rows). `OSS_Ceto` has no STW column. High-fidelity vector derivation is possible for Triton ($r=0.998$). | **T1 (100%)** | Generalized findings from one vessel file (`CPS_Poseidon`) to the entire multi-vessel fleet without inspecting individual parquets. |
| **3** | **FuelCast: Shaft Power & Propulsion** | "No engine or propulsion power data provided" | "Shaft power present for main engines only" | "Synthetic power computed from Holtrop" | Parquet schema audit: 9 power columns in Poseidon, 8 in Triton, 3 in Ceto (T1) | **Shaft power, torque, and RPM exist as real observed telemetry**: Poseidon has generator shaft powers + port/starboard propeller shaft power ($W$) and torque ($\text{N}\cdot\text{m}$). Triton has main engine & propeller shaft powers and torques. | **T1 (100%)** | Report assumed FuelCast was strictly a kinematic/weather table and overlooked engine/propeller sensor columns. |
| **4** | **FuelCast: Dataset License** | "Public domain CC0 / Open Source" | "Permissive MIT License" | "Strictly proprietary / unreleased" | Hugging Face YAML metadata: `license: cc-by-nc-nd-4.0` (T1); arXiv preprint metadata (T2) | **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (`CC BY-NC-ND 4.0`)**. Non-commercial academic research permitted; commercial use and public redistribution of adapted derivatives prohibited. | **T1 (100%)** | Assumed that public availability on Hugging Face equates to permissive open source (MIT/Apache). |
| **5** | **FuelCast: Vessel Count & Types** | "Single commercial container ship" | "Three identical sister cargo vessels" | "Unknown synthetic vessels" | Hugging Face parquets + arXiv:2510.08217v1 Table 1 (T1/T2) | **Exactly 3 distinct real vessels**: Two Cruise Passenger Ships (`CPS_Triton`, 11,000 GT; `CPS_Poseidon`, 70,000 GT) and one Offshore Supply Ship (`OSS_Ceto`, 24,000 GT). Total rows: 173,986. | **T1 (100%)** | Ignored vessel typology prefixes (`CPS` vs `OSS`) and failed to verify individual parquet filenames. |
| **6** | **FuelCast: Fuel Target Lineage** | "Derived from empirical Holtrop SFC curves" | "Daily noon report bunker sounding interpolated" | "Coriolis mass flow meter measurement" | arXiv:2510.08217v1 §3.2 (T2); KROHNE EcoMATE™ specifications (T1) | **Real Observed Coriolis Mass Flow**: Measured directly using calibrated KROHNE Coriolis mass-flow meters on each engine, calculating instantaneous consumption as differential inlet minus outlet ($\dot{m}_{\text{in}} - \dot{m}_{\text{out}}$). | **T1 / T2 (100%)** | Conflated synthetic benchmark generation methods with KROHNE Digital's industrial telemetry collection. |
| **7** | **PONTOS-Hub: Telemetry Data Availability** | "Fully open public dataset with 1-second telemetry" | "Free REST API with open access to Swedish fleet" | "Platform blueprint only; no real data" | GitHub `MO-RISE/pontos-hub` (T1); live API test against `pontos.ri.se/api/vessel_ids` (T1) | **Data is GATED / BLOCKED (`HTTP 401 Unauthorized`)**: While the microservice software platform is open source (Apache 2.0), live and historical telemetry queries require a restricted JWT bearer token (`PONTOS_TOKEN`). | **T1 (100%)** | Confused open-source datahub software infrastructure with open public operational data access. |
| **8** | **PONTOS-Hub: Fuel Flow Availability** | "Direct mass flow in kg/h" | "No fuel flow measurements exist" | "Only volumetric liters per hour" | `MO-RISE/pontos-data-format/tags.md` (T1); `pontos_cli` source code (T1) | **Defined tag is volumetric (`enginemain_fuelcons_lph`), not mass flow**. On test vessel `SD 401 Fredrika`, fuel flow is not publicly accessible without authentication. | **T1 (100%)** | Relied on verbal project summaries rather than inspecting the schema specification and client implementations. |
| **9** | **M/S Smyril: Repository & Download Status** | "Dataset is dead / link permanently broken" | "Privately archived at DTU; not downloadable" | "Available on academic request only" | Live HTTP GET check against `http://cogsys.imm.dtu.dk/propulsionmodelling/raw_data.tar.gz` (T1) | **Fully Live and Downloadable (`HTTP 200 OK`)**: 282.19 MB archive (`295,900,645` bytes) actively hosted at DTU. Streaming verification confirms ~1 Hz sensor CSVs. | **T1 (100%)** | Encountered broken intermediate mirror links without testing the primary DTU Cognitive Systems institutional domain. |
| **10** | **Shifts 2.0: Target Variable Definition** | "Direct ship fuel consumption in kg/h" | "Instantaneous fuel rate and power" | "Shaft power estimation benchmark" | GitHub `Shifts-Project/shifts/vpower/README.md` (T1); arXiv:2206.15407v2 §4 & App. D (T2) | **Propeller Shaft Power (`power` in kW) ONLY**. NO fuel consumption target exists in the dataset. Measured via onboard optical/strain gauge torsionmeter. | **T1 / T2 (100%)** | Conflated the maritime energy domain with fuel mass flow; assumed maritime energy consumption always means bunker fuel. |
| **11** | **Shifts 2.0: Speed Through Water (STW)** | "SOG only from GPS" | "Derived STW from weather reanalysis" | "Direct STW from Doppler speed log" | `Shifts-Project/shifts/vpower/README.md` feature table (T1) | **Direct Speed Through Water (`stw` in knots)** measured by onboard speed log. Also includes SOG acceleration (`diff_speed_overground`). | **T1 (100%)** | Report failed to read the published tabular feature schema in the official repository. |
| **12** | **UTAS-WMU: Target Resolution & Task Fit** | "High-frequency operational sensor dataset" | "Voyage-level aggregate fuel consumption" | "Suitable for real-time instantaneous prediction" | Elsevier *Comm. Transp. Res.* (2022) Part I/II/III text (T2) | **Voyage-level / 24-hour noon report aggregates** ($X_{\text{voyage}} \to F_{\text{voyage}}$). Entirely unsuitable for synchronous instantaneous state estimation ($X(t) \to F(t)$). | **T2 (100%)** | Equated voyage-level maritime fuel efficiency modeling with high-frequency operational IoT prediction. |

---

## 3. Systematic Breakdown of Critical Discrepancies

### 3.1 FuelCast: The "Direct STW" Conflict
Prior reports presented contradictory claims: Report B stated STW was absent, while Report A stated STW was universally present.
- **Forensic Investigation**: Direct inspection of the three Parquet files reveals that both reports made sweeping generalizations from partial evidence:
  - `CPS_Poseidon.parquet`: Column `Ship_SpeedThroughWater` exists and contains 103,148 valid non-null measurements ranging from $0.00$ to $12.40\text{ m/s}$ ($0.0 - 24.1\text{ kn}$).
  - `CPS_Triton.parquet`: Column `Ship_SpeedThroughWater` exists, but its value is frozen at exactly $0.5144\text{ m/s}$ ($1.00\text{ kn}$) across all 25,351 rows. This represents a known marine logging failure where an uncalibrated or disconnected acoustic Doppler speed log defaulted to a fixed constant.
  - `OSS_Ceto.parquet`: Column `Ship_SpeedThroughWater` is completely absent.
- **Resolution**: Direct STW is valid **only on Poseidon**. On Triton, STW must be reconstructed using the hydrodynamic vector triangle ($V_{\text{water}} = V_{\text{ground}} - V_{\text{current}}$). On Poseidon, this vector derivation exhibits $r = 0.998$ correlation with the Doppler log, confirming mathematical viability.

### 3.2 FuelCast: Shaft Power & Propulsion Variables
Prior reports claimed that FuelCast lacked propulsion telemetry and could not be used to validate engine physics.
- **Forensic Investigation**: Direct schema inspection revealed:
  - `CPS_Poseidon`: 9 shaft power columns, 7 RPM columns, 2 torque columns (`Propeller_Port_ShaftTorque`, `Propeller_Starboard_ShaftTorque`).
  - `CPS_Triton`: Main engine shaft power (Port/Starboard), propeller shaft power (Port/Starboard), RPM, and torque.
  - `OSS_Ceto`: Engine room shaft powers and RPM.
- **Resolution**: Propulsion variables **are present**. Because fuel consumption is physically and mechanically coupled to shaft power through engine brake specific fuel consumption (BSFC), shaft power must be quarantined into `CONFIG-REAL-B` (upstream propulsion inclusion) and excluded from `CONFIG-REAL-A` (kinematic/environmental pure estimation) to prevent label leakage.

### 3.3 Shifts 2.0: The False "Fuel Consumption" Target
Several summaries erroneously cataloged Shifts 2.0 as a competitor for ship fuel prediction.
- **Forensic Investigation**: Appendix D.2 of arXiv:2206.15407v2 and `vpower/README.md` explicitly state:
  > *"Target feature: `power` (kW) — Propeller shaft power. For real data is measured by an onboard torquemeter."*
- **Resolution**: Shifts 2.0 is an operational **shaft power** dataset, not a fuel mass flow dataset. It cannot evaluate $X(t) \to F(t)$. It can, however, serve as an auxiliary benchmark for hydrodynamic resistance and shaft power modeling ($X(t) \to P(t)$).
