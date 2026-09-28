# SIH26138 — Dataset Legal & Licensing Forensic Audit
**Document ID:** `LEGAL-AUDIT-001`  
**Audit Date:** `2026-09-12`  
**Platform Version:** `0.2.1`  
**Auditor Role:** Forensic Scientific Data Auditor  

---

## 1. Executive Summary & Legal Boundary Classification

This audit establishes the definitive legal and intellectual property status of all candidate real maritime operational datasets. Prior research reports frequently conflated "publicly downloadable on the web" with "openly reusable for commercial purposes."

Under forensic scrutiny:
- **No candidate dataset is licensed under an unencumbered permissive open-source license (such as MIT, Apache 2.0, or CC0) for commercial operational use.**
- **FuelCast** is governed by **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (`CC BY-NC-ND 4.0`)**.
- **Shifts 2.0** is governed by **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0`)**.
- **M/S Smyril (DTU)** is released under an academic research distribution without explicit commercial grant.
- **PONTOS-Hub** code is Apache 2.0, but operational data is proprietary and gated behind authorization credentials.

---

## 2. Comprehensive License Verification Matrix

| Dataset Name | Primary Legal Source | Declared License | Version | Commercial Use? | Public Redistribution? | Derivative Works Distributed? | Mandatory Attribution | Legal Status for SIH Hackathon Evaluation | Commercial Production Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **FuelCast** | Hugging Face Dataset Card YAML Frontmatter | `CC BY-NC-ND` | 4.0 | **PROHIBITED** | Permitted (Unadapted only) | **PROHIBITED** | Required (Viga et al., Springer 2026) | **PERMITTED** (Non-commercial academic evaluation) | **LICENSE_REVIEW_REQUIRED** (Requires commercial bilateral license from KROHNE) |
| **M/S Smyril** | DTU Cognitive Systems Data Portal (`cogsys.imm.dtu.dk`) | Academic Research Access | N/A (2011) | **UNAUTHORIZED** | Permitted with citation | Internal modification permitted; commercial redistribution prohibited | Required (Petersen et al., COMPIT'11 & JMST 2012) | **PERMITTED** (Academic benchmarking) | **LICENSE_REVIEW_REQUIRED** (Requires clearance from DTU / Decision3) |
| **Shifts 2.0** | GitHub `Shifts-Project/shifts/vpower/README.md` | `CC BY-NC-SA` | 4.0 | **PROHIBITED** | Permitted (under same license) | Permitted (Must share alike) | Required (Malinin et al., NeurIPS/arXiv 2022) | **PERMITTED** (Non-commercial academic research) | **PROHIBITED** (Non-commercial clause prevents closed commercial SaaS) |
| **PONTOS-Hub** | GitHub `MO-RISE/pontos-hub/LICENSE` & API auth | Code: Apache 2.0; Data: Proprietary / Gated | Code: 2.0 | Code: YES; Data: GATED | Code: YES; Data: NO | Code: Permitted; Data: Restricted | Required (RISE Research Institutes of Sweden) | **DATA INACCESSIBLE** (`HTTP 401`) | **PROHIBITED** (Unless formal partnership agreement is established with RISE) |
| **UTAS-WMU** | Elsevier *Comm. Transp. Res.* (2022) | Proprietary Shipping Line Data | N/A | **PROHIBITED** | **PROHIBITED** | **PROHIBITED** | Required (Li et al., 2022) | **DATA INACCESSIBLE** (Unreleased) | **PROHIBITED** |

---

## 3. Forensic Deep Dive: FuelCast (`krohnedigital/FuelCast`)

### 3.1 Primary Legal Artifacts
- **Hugging Face YAML Metadata**:
  ```yaml
  license: cc-by-nc-nd-4.0
  ```
- **ArXiv Paper Text License**:
  ```
  License: CC BY-SA 4.0 (Preprint text only)
  ```
- **Springer Publisher Notice**:
  Copyright © 2026 Springer Nature Switzerland. Book chapter published in *Advanced Analytics and Learning on Temporal Data*.

### 3.2 Terms of Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (`CC BY-NC-ND 4.0`)
Under the formal legal code of `CC BY-NC-ND 4.0`:
1. **NonCommercial (NC)**:
   - *"NonCommercial means not primarily intended for or directed towards commercial advantage or monetary compensation."*
   - Participating in the Smart India Hackathon (SIH26138) as an academic/student research project and validating an open-source research engine is strictly non-commercial and legally permissible.
   - However, packaging this data into a commercial maritime SaaS fleet routing service or enterprise SaaS offering sold to ship operators would breach the NC clause unless KROHNE Messtechnik GmbH issues an explicit commercial license.
2. **NoDerivatives (ND)**:
   - *"If you remix, transform, or build upon the material, you may not distribute the modified material."*
   - In-memory transformations, feature normalization, and feeding the data into a machine learning model for evaluation do not constitute distributing modified data.
   - However, the project **must not publish or redistribute modified versions of the parquet files** (e.g. resampled or augmented datasets) to public third-party repositories. The raw files must be referenced or downloaded directly from the upstream Hugging Face endpoint.
3. **Attribution (BY)**:
   - Any report, slide deck, paper, or dashboard citing FuelCast must provide explicit attribution to Justus Viga, Penelope Mueck, Alexander Löser, Torben Weis, KROHNE Digital, and Springer Nature.

### 3.3 Classification for SIH Prototype
- **Academic Research & Hackathon Evaluation**: `LEGALLY_PERMITTED`
- **Commercial Deployment / Enterprise Fleet Optimization**: `LICENSE_REVIEW_REQUIRED` (Must be documented in the final report as requiring commercial licensing from KROHNE Messtechnik).

---

## 4. Forensic Deep Dive: M/S Smyril (`DTU Cognitive Systems`)

### 4.1 Primary Legal Artifacts
- Hosted on the public institutional server of DTU: `http://cogsys.imm.dtu.dk/propulsionmodelling/data.html`.
- Webpage declaration:
  > *"We present a novel and publicly available data set of high quality sensory data collected from a ferry over a period of 2 months... Download the raw dataset here."*
- Paper copyright: COMPIT'11 proceedings (May 2011) and Springer (*Journal of Marine Science and Technology*, 2012).
- Authors: J. P. Petersen, D. J. Jacobsen (Decision3 / Strandfaraskip Landsins) and Ole Winther (DTU Informatics).

### 4.2 Reusability Analysis
- The dataset has been cited and utilized across more than 50 academic maritime engineering publications (e.g. Bassam et al., *Ocean Engineering*, 2022; Ma et al., *JMSE*, 2023).
- DTU provided the data as an open academic benchmark for propulsion modeling.
- No commercial exploitation rights were granted. Use in SIH26138 is legitimate under fair academic benchmarking.

---

## 5. Forensic Deep Dive: Shifts 2.0 (`vpower`)

### 5.1 Primary Legal Artifacts
- GitHub Repository `vpower/README.md`:
  > *"The data are released under CC BY-NC-SA 4.0 license."*
- Code Repository `vpower/LICENCE`:
  > *"Apache License Version 2.0, January 2004 — Copyright 2022 Deepsea Technologies."*

### 5.2 Legal Implications
- Software scripts, baseline neural network architectures, and evaluation metrics are Apache 2.0 (permissive commercial reuse).
- The telemetry data itself is `CC BY-NC-SA 4.0`. While derivatives are allowed, any derivative work must be shared under the identical non-commercial license.
- This dataset is restricted to auxiliary scientific testing.

---

## 6. Synthesis: Legal Usability Verdict

1. **For Smart India Hackathon (SIH26138) Scientific Benchmark**:
   - Both **FuelCast** and **M/S Smyril** are 100% legally usable for offline model validation, comparative benchmarking, and academic report submission.
2. **For Commercial Platform Commercialization**:
   - The platform must be architected so that client vessel owners supply their own operational telemetry (e.g. NMEA-0183/2000, Modbus, or EcoMATE streams).
   - FuelCast cannot be bundled as a commercial training asset without a corporate agreement with KROHNE Digital.
   - Classification: **`LICENSE_REVIEW_REQUIRED`** for enterprise deployment.
