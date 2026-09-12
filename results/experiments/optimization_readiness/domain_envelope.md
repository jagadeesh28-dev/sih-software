# Operating Domain Envelope & Feature Distribution Profiling
**Document ID:** `AUDIT-ENVELOPE-001`  
**Dataset:** `DS-SYNTH-2026-01` (`SYNTHETIC_TEST_DATA`, N_train=833)  
**Software Version:** 0.2.1 | **Git Commit:** `febed1ae38a3b2be34235dc6436b5fc7d493808b`  

---

## 1. Feature Bounding & Percentile Envelope

| Feature | Train Min | P01 | Median (P50) | P99 | Train Max | Mean | Std | IQR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stw_kn` | 8.00 | 11.22 | 14.44 | 17.59 | 18.69 | 14.41 | 1.41 | 1.95 |
| `sog_kn` | 9.38 | 10.87 | 14.44 | 18.17 | 22.00 | 14.43 | 1.58 | 2.07 |
| `draft_m` | 7.85 | 7.90 | 8.10 | 11.59 | 11.61 | 9.21 | 1.63 | 3.44 |
| `displacement_t` | 15200.00 | 15200.00 | 15300.00 | 58000.00 | 58000.00 | 29620.17 | 20206.36 | 42800.00 |
| `rpm` | 0.00 | 108.38 | 119.98 | 131.33 | 135.28 | 119.76 | 6.52 | 7.02 |
| `shaft_power_kw` | 0.00 | 960.92 | 1771.02 | 3025.81 | 3573.87 | 1821.70 | 468.06 | 636.39 |
| `shaft_torque_nm` | 60475.56 | 84051.04 | 141004.65 | 223647.78 | 252271.96 | 144143.19 | 31214.86 | 43508.77 |
| `engine_load_pct` | 8.00 | 8.00 | 13.85 | 29.93 | 35.33 | 14.74 | 4.88 | 6.12 |
| `wind_speed_ms` | 1.00 | 1.78 | 7.26 | 13.52 | 15.29 | 7.38 | 2.46 | 3.20 |
| `wind_direction_deg` | 0.11 | 3.06 | 183.26 | 356.79 | 359.90 | 181.80 | 102.04 | 173.61 |
| `wave_height_m` | -2.50 | 0.24 | 1.51 | 2.60 | 3.01 | 1.50 | 0.52 | 0.67 |
| `wave_period_s` | 3.00 | 4.36 | 7.02 | 10.10 | 10.75 | 7.05 | 1.21 | 1.55 |
| `wave_direction_deg` | 0.25 | 6.95 | 185.01 | 358.03 | 359.89 | 181.27 | 101.96 | 175.43 |
| `current_speed_ms` | 0.00 | 0.04 | 0.50 | 0.96 | 9.50 | 0.50 | 0.37 | 0.28 |
| `current_direction_deg` | 0.23 | 5.89 | 183.61 | 354.82 | 359.68 | 182.65 | 102.49 | 169.16 |
| `water_depth_m` | 40.81 | 47.82 | 404.86 | 794.57 | 799.44 | 411.67 | 217.79 | 370.75 |

---

## 2. Operating Domain Classification Rules
1. **IN_DOMAIN (`VALID`)**: All features fall within empirical [P01, P99] intervals.
2. **NEAR_BOUNDARY (`CAUTION`)**: Features lie between [min, P01) or (P99, max].
3. **OUT_OF_DOMAIN (`REJECTED`)**: Any feature exceeds empirical [min, max] boundaries.
4. **PHYSICALLY_INVALID (`REJECTED`)**: State violates physical constraints (negative power, impossible speeds).
