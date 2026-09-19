# Slide 4: Real Vessel Telemetry & Data Provenance

## Commercial Vessel Fleet Dataset

| Vessel Identifier | Vessel Type | Raw Ingested | Cleaned Validated | Data Hash (SHA256) |
|:------------------|:------------|:-------------|:------------------|:-------------------|
| **CPS_Poseidon** | Large Passenger Cruise | 105,426 | **105,422** | `da85f2e21b6e8724...` |
| **CPS_Triton** | Small Passenger Cruise | 25,351 | **25,347** | `fa8cc7f9f6a92d33...` |
| **OSS_Ceto** | Offshore Platform Supply | 43,209 | **43,205** | `ac3f8d5e865f11cd...` |
| **Fleet Totals** | **3 Vessels** | **173,986** | **173,974** | **100% Cryptographic Match** |

---

## Data Cleaning & Integrity Protocol
- **Removal of 12 Trailing Rows**: Exactly 4 rows at the end of each vessel's logging file contained null timestamps and dead sensor channels caused by data logger shutdown.
- **Zero Interior Interpolation**: No artificial synthetic imputation was performed on interior operational records.
- **Speed Decoupling**: Speed Through Water (STW) and Speed Over Ground (SOG) are strictly decoupled to preserve ocean current effects.

---

## Leakage-Free Temporal Split Protocol
- **Chronological Forward Splitting**:
  - **Train Set (60%)**: $104,384$ records (earliest historical segment).
  - **Validation Set (20%)**: $34,794$ records (used strictly for hyperparameter tuning & conformal calibration).
  - **Test Set (20%)**: $34,796$ records (strictly held-out future operational window).
- **Temporal Monotonicity**: Zero future data contamination into training sets; confirmed by deterministic test assertion.
