# Maritime Dataset Quality Audit Report

## 1. Executive Summary
- **Total Records Audited**: 1,203
- **Vessel Count**: 3 (VESSEL_FE_01, VESSEL_FE_02, VESSEL_HM_03)
- **Temporal Span**: 2026-03-01T00:00:00+00:00 to 2026-03-02T09:15:00+00:00
- **Nominal Sampling Interval**: 300.0 s

## 2. Epistemic Quality Classification
Every observation has been classified without destructive discarding:

| Classification | Record Count | Percentage | Definition |
| :--- | :--- | :--- | :--- |
| **VALID** | 1,178 | 97.92% | Physically sound, non-duplicate, within allowable ranges |
| **SUSPICIOUS** | 1 | 0.08% | Plausible but extreme or preceded by timestamp gap |
| **INVALID** | 9 | 0.75% | Physically impossible (e.g. negative fuel/power, bad coordinates) |
| **MISSING** | 15 | 1.25% | Missing one or more required sensor channels |

## 3. Diagnostic Breakdown
- **Duplicate Observations**: 3 (0.25%)
- **Range Violations Detected**: 4
- **Temporal Gaps Detected (>3x nominal interval)**: 1
- **Missing Schema Columns**: None (All canonical columns present)

## 4. Policy for Machine Learning Ingestion
- Only **VALID** records are permitted into model training and validation sets.
- **INVALID** records are isolated and logged in `range_violations.csv` and `duplicates.csv`.
- **SUSPICIOUS** records require explicit experimenter flagging before inclusion.
