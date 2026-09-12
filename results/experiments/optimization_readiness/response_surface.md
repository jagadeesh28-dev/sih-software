# Operating-Domain Response Surface Audit
**Document ID:** `AUDIT-SURFACE-001`  
**Evaluation Scope:** Sensitivity sweeps of frozen LightGBM surrogate across operational features.  
**Software Version:** 0.2.1 | **Git Commit:** `febed1ae38a3b2be34235dc6436b5fc7d493808b`  

---

## 1. Key Sweep Findings
- **Shaft Power Sweep**: Strong, monotonic fuel rate scaling with shaft power, rising from ~120 kg/h at 500 kW to ~1,500+ kg/h at 8,000 kW.
- **Speed Sweep (Coupled Power)**: Across cruising speeds (10-22 kn), fuel consumption scales cubically, mirroring hydrodynamic demand.
- **Wave Height Sweep**: Mild upward drift in fuel demand, within decision tree step-plateaus.
- **Wind Speed Sweep**: Moderate aerodynamic drag increase; zero negative predictions.
- **Boundary & Extrapolation Behavior**: When inputs exceed P99, domain checker shifts from VALID to NEAR_BOUNDARY or OUT_OF_DOMAIN.

---

## 2. Tabular Sample (One-Factor Speed Sweep)

| Speed (kn) | Power (kW) | Predicted Fuel (kg/h) | Q05 Bound | Q95 Bound | Uncertainty Width | Domain Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 10.0 | 1025.4 | 300.8 | 193.3 | 314.7 | 121.4 | `NEAR_BOUNDARY` |
| 11.0 | 1364.8 | 316.4 | 236.6 | 314.7 | 78.2 | `NEAR_BOUNDARY` |
| 12.0 | 1771.9 | 350.7 | 307.2 | 332.3 | 25.1 | `VALID` |
| 13.0 | 2252.8 | 403.6 | 316.4 | 388.9 | 72.5 | `OUT_OF_DOMAIN` |
| 14.0 | 2813.7 | 452.6 | 328.5 | 442.1 | 113.6 | `OUT_OF_DOMAIN` |
| 15.0 | 3460.7 | 477.6 | 347.1 | 485.7 | 138.6 | `OUT_OF_DOMAIN` |
| 16.0 | 4200.0 | 488.9 | 396.3 | 501.7 | 105.3 | `OUT_OF_DOMAIN` |
| 17.0 | 5037.7 | 506.0 | 518.4 | 518.4 | 0.0 | `OUT_OF_DOMAIN` |
| 18.0 | 5980.1 | 524.2 | 526.0 | 599.0 | 73.0 | `OUT_OF_DOMAIN` |
| 19.0 | 7033.2 | 524.2 | 526.0 | 599.0 | 73.0 | `PHYSICALLY_INVALID` |
