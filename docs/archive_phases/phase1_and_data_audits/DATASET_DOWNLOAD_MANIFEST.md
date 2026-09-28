# SIH26138 — Maritime Dataset Forensic Download Manifest
**Document ID:** `MANIFEST-REAL-DATA-001`  
**Audit Date:** `2026-09-12`  
**Platform Version:** `0.2.1`  
**Auditor Role:** Forensic Scientific Data Auditor (SIH26138 Egreen Quanta)  

---

## 1. Primary Downloaded Dataset: FuelCast (KROHNE Digital)

- **Official Repository**: `https://huggingface.co/datasets/krohnedigital/FuelCast`
- **Preprint DOI / Reference**: `arXiv:2510.08217v1` [cs.LG] (2025-10-09)
- **Peer-Reviewed Reference**: Springer Nature Link (*Advanced Analytics and Learning on Temporal Data*, pp. 54–69, 2026, ISBN: 978-3-032-15535-1, DOI: `10.1007/978-3-032-15535-1_4`)
- **Repository Commit Hash**: `eb6a6ec011c1c9a2cbce21459e22be4c77ef84dd`
- **License**: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (`CC BY-NC-ND 4.0`)
- **Local Storage Path**: `data/external/fuelcast/`
- **Access Protocol**: HTTPS direct binary pull via Hugging Face REST LFS endpoints.

### Verified File Checksums & Metadata:

| Relative File Path | Format | Size (Bytes) | Size (MB) | Verified SHA-256 Checksum | Number of Records | Columns |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| `data/external/fuelcast/CPS_Poseidon.parquet` | Apache Parquet | `10,860,847` | 10.36 MB | `fcc4fff3e86de3d02b034376429e4cd98c794befb4e8f610187643d52552571b` | 105,422 | 65 |
| `data/external/fuelcast/CPS_Triton.parquet` | Apache Parquet | `3,154,132` | 3.01 MB | `327581b0d35c756db207e6992a1d78f6f7e4f68dcfd299c77188912fdbd6aab8` | 25,351 | 62 |
| `data/external/fuelcast/OSS_Ceto.parquet` | Apache Parquet | `3,479,421` | 3.32 MB | `a81eefff2bb6bedbb85455e4fb408906a1de5356f0633fda450d7e794410b7ef` | 43,213 | 46 |
| **Total Verified** | — | **`17,494,400`** | **16.68 MB** | — | **173,986** | — |

---

## 2. Primary Remote-Verified Dataset: M/S Smyril (Petersen / DTU)

- **Official Repository**: Technical University of Denmark (DTU) Cognitive Systems
- **Repository Landing URL**: `http://cogsys.imm.dtu.dk/propulsionmodelling/data.html`
- **Direct Archive URL**: `http://cogsys.imm.dtu.dk/propulsionmodelling/raw_data.tar.gz`
- **Peer-Reviewed Publications**:
  - COMPIT'11 (Berlin, May 2011, pp. 305–316): *"A machine-learning approach to predict main energy consumption under realistic operational conditions"*
  - *Journal of Marine Science and Technology* (Springer, 2012, 17:30–39, DOI: `10.1007/s00773-011-0151-0`): *"Statistical modelling for ship propulsion efficiency"*
- **HTTP Server Response**: `HTTP/1.1 200 OK`
- **Content-Length**: `295,900,645` bytes (282.19 MB)
- **Archive Format**: Gzipped POSIX Tar Archive (`application/x-gzip`)
- **Sampling Frequency**: ~1.0 Hz (.NET DateTime 100-nanosecond ticks, start timestamp `2010-02-16 10:50:11.922539 UTC`)
- **Archive Contents Verified via In-Memory Stream**:
  - `rawdata/fuelDensity.csv` (`47,012,195` bytes)
  - `rawdata/fuelTemp.csv`
  - `rawdata/fuelVolumeFlowRate.csv` (`47,011,898` bytes)
  - `rawdata/inclinometer-raw.csv`
  - `rawdata/latitude.csv`
  - `rawdata/longitude.csv`
  - `rawdata/level1median.csv`
  - `rawdata/level2median.csv`
  - `rawdata/longitudinalWaterSpeed.csv`
  - `rawdata/portPitch.csv`, `rawdata/starboardPitch.csv`
  - `rawdata/portRudder.csv`, `rawdata/starboardRudder.csv`
  - `rawdata/speedKmh.csv`, `rawdata/speedKnots.csv`
  - `rawdata/trackDegreeMagnetic.csv`, `rawdata/trackDegreeTrue.csv`
  - `rawdata/trueHeading.csv`
  - `rawdata/windAngle.csv`, `rawdata/windSpeed.csv`
- **Download Classification**: `VERIFIED_REMOTE_ACCESSIBLE` (Download validated via streaming inspection; full extraction optional due to 282 MB size).

---

## 3. Auxiliary Remote-Verified Dataset: Shifts 2.0 Vessel Power (DeepSea / Shifts Project)

- **Official Repository**: `https://github.com/Shifts-Project/shifts` (`vpower/` directory)
- **Paper Reference**: `arXiv:2206.15407v2` [cs.LG] (2022-09-15)
- **Direct AWS S3 URL**: `https://deepsea-tmp.s3.eu-central-1.amazonaws.com/baselines.zip`
- **Zenodo Deposit Records**: `https://zenodo.org/record/7051658`, `https://zenodo.org/record/7051692`, `https://zenodo.org/record/7057666`
- **License**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0`)
- **Target Variable**: Propeller Shaft Power (`power` in kW) from onboard shaft torsionmeter.
- **Fuel Flow Target**: **ABSENT** (Confirmed via `Shifts-Project/shifts/vpower/README.md` and paper Appendix D).
- **Download Classification**: `VERIFIED_AUXILIARY_REMOTE` (Shaft power estimation benchmark only).

---

## 4. Blocked / Gated Candidate: PONTOS-Hub (RISE Sweden)

- **Project Web Portal**: `https://pontos.ri.se`
- **Platform Architecture Repository**: `https://github.com/MO-RISE/pontos-hub`
- **CLI Utility Repository**: `https://github.com/arvidsorfeldt/pontos_cli`
- **Data Format Specification**: `https://github.com/MO-RISE/pontos-data-format`
- **API Endpoint**: `https://pontos.ri.se/api/vessel_ids`
- **API Diagnostic Check**:
  ```http
  GET /api/vessel_ids HTTP/1.1
  Host: pontos.ri.se
  Status: 401 Unauthorized
  Body: {"code":"42501","details":null,"hint":null,"message":"permission denied for view vessel_ids"}
  ```
- **License Status**: Code is Apache-2.0; Telemetry data is restricted behind partner JWT authentication tokens (`PONTOS_TOKEN`).
- **Forensic Status**: `DOWNLOAD_BLOCKED` (Open platform architecture, proprietary/gated operational data).

---

## 5. Blocked / Unsuitable Candidate: UTAS-WMU

- **Publication References**: Elsevier *Communications in Transportation Research* (2022):
  - Part I (DOI: `10.1016/j.commtr.2022.100074`)
  - Part II (DOI: `10.1016/j.commtr.2022.100073`)
  - Part III (DOI: `10.1016/j.commtr.2022.100072`)
- **Target Resolution**: 24-hour noon report aggregates and voyage-leg aggregates.
- **Repository Availability**: No public Zenodo, Mendeley Data, or GitHub repository published with the articles.
- **Forensic Status**: `DOWNLOAD_BLOCKED` & `TASK_INCOMPATIBLE` (Voyage-level aggregate, mathematically incapable of operational $X(t) \to F(t)$ instantaneous fuel flow estimation).
