# AUDIT #3: DATA INTEGRITY & ARTIFACT SANITY VERIFICATION
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §5 & §16 Data Integrity & Raw Log Auditing  
**Auditor:** Scientific Validation Engineer & Reproducibility Auditor  
**Date:** September 15, 2026  

---

## 1. Raw Dataset Integrity & Structure

All raw optimization logs stored in `PHASE5/results/` and `PHASE5/validation/` were scanned for missing values, NaN incursions, unphysical negative fitness values, and formatting defects.

### Raw Results Files Audit Matrix
| File Path | Rows (Header + Data) | Columns | Missing Values (NaN/Null) | Min Fitness | Max Fitness | Feasible Run Count | MD5 Hash | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `PHASE5/results/A0.csv` | 31 (1 + 30) | 24 | 0 | 3.375 | 51,000.00 | 24 / 30 (80.0%) | `6fb65780a4b3d7b876d299446fec36d1` | **PASS** |
| `PHASE5/results/A1.csv` | 31 (1 + 30) | 24 | 0 | 3.373 | 20,003.35 | 30 / 30 (100.0%) | `c5db4591f86aa5930214c718bbf6f586` | **PASS** |
| `PHASE5/results/A2.csv` | 31 (1 + 30) | 24 | 0 | 3.372 | 3.424 | 30 / 30 (100.0%) | `928ddb3df71a340b0baefbfe65324ec9` | **PASS** |
| `PHASE5/results/A3.csv` | 31 (1 + 30) | 24 | 0 | 3.374 | 51,000.00 | 26 / 30 (86.7%) | `8b4383c276a74da4790176fb14878a17` | **PASS** |
| `PHASE5/results/A4.csv` | 31 (1 + 30) | 24 | 0 | 3.385 | 4.869 | 30 / 30 (100.0%) | `0f507b966cf17ae28d9cba704143a411` | **PASS** |
| `PHASE5/results/A5.csv` | 31 (1 + 30) | 24 | 0 | 3.378 | 3.824 | 30 / 30 (100.0%) | `a5f4ebba7d56e01ea313c4c8bf3b867c` | **PASS** |
| `PHASE5/results/DE.csv` | 31 (1 + 30) | 24 | 0 | 3.381 | 20,003.49 | 30 / 30 (100.0%) | `111867c4a16223e71ba2db7ebf7eeea9` | **PASS** |
| `PHASE5/results/PSO.csv` | 31 (1 + 30) | 24 | 0 | 3.378 | 51,000.00 | 15 / 30 (50.0%) | `49633ff80175b9f71bf46fc108d0e764` | **PASS** |
| `PHASE5/results/GA.csv` | 31 (1 + 30) | 24 | 0 | 3.377 | 51,000.00 | 21 / 30 (70.0%) | `03ffb40076a26732f1ea30c0c69ea400` | **PASS** |
| `PHASE5/results/Random.csv` | 31 (1 + 30) | 24 | 0 | 3.489 | 51,000.00 | 29 / 30 (96.7%) | `d55df27d53b2d18721244d85287e07ca` | **PASS** |
| `PHASE5/results/NSGA3.csv` | 31 (1 + 30) | 24 | 0 | 3.421 | 51,000.00 | 24 / 30 (80.0%) | `8fbc8bcf8df33036e78ba7a5bebb089d` | **PASS** |

---

## 2. Validation & Benchmark Summary Files
- `PHASE5/results/A5_ABLATION_TABLE.csv`: Exactly matches arithmetic means and medians computed from the raw CSVs.
- `PHASE5/results/A5_COMPONENT_CONTRIBUTION.csv`: Correctly reflects pairwise differences between consecutive ablation stages.
- `PHASE5/validation/failure_taxonomy.csv`: Exactly reflects failure counts across all algorithms (total failed runs = 6 for A0, 0 for A1, 0 for A2, 4 for A3, 0 for A4, 0 for A5, 0 for DE, 15 for PSO, 9 for GA, 1 for Random, 6 for NSGA-III).
- `PHASE5/validation/scalability.csv`: Contains 8 rows covering $D \in \{30, 120, 300, 600\}$ across A5 and DE.

---

## 3. Seed Alignment Verification
Every raw CSV was checked for seed sequencing:
$$\text{seeds} = [1001, 1002, 1003, \dots, 1030]$$
The seed ordering is strictly monotonic, identical across all 11 algorithms, and pairs perfectly for paired statistical tests.

---

## 4. Audit Verdict: PASS
All raw CSV artifacts have complete structural integrity, zero missing data, zero corrupted fields, and exact mathematical alignment with all published tables.
