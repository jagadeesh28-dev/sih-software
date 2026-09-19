# PHASE 5 REPRODUCIBILITY AUDIT & PROTOCOL
**Project:** SIH26138 — Egreen Quanta  
**Benchmark:** Phase 5 Heterogeneous Fleet Ablation (A0–A5) & Classical Baselines  
**Standard:** IEEE Transactions on Evolutionary Computation / ACM Artifact Review Standards  
**Status:** FULLY REPRODUCIBLE (100% Deterministic Seed Verification)

---

## 1. System & Environment Specifications

| Parameter | Value |
| :--- | :--- |
| **Operating System** | Windows 11 Enterprise (Build 26100.3194 / 64-bit) |
| **Host Architecture** | x86_64 / Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz (8 vCPUs) |
| **Installed RAM** | 16.0 GB DDR4 |
| **Python Runtime** | Python 3.14.0 (CPython, 64-bit) |
| **Random Seed Scheme** | 3-Tier Seed Isolation Protocol (Tuning, Validation, Final Benchmark) |
| **Evaluation Accounting** | Strict physical evaluator calls recorded via thread-safe call interceptor |
| **Common Interface** | `BaseFleetOptimizer.optimize(evaluator, bounds, seed, budget)` |

### Primary Python Package Dependencies
```text
numpy==2.2.3
scipy==1.15.2
pandas==2.2.3
pyarrow==19.0.1
matplotlib==3.10.1
seaborn==0.13.2
pytest==8.3.4
pyyaml==6.0.2
```

---

## 2. Seed Protocol & Budget Allocation

To prevent p-hacking and parameter overfitting, three strictly disjoint sets of seeds were used across all experiments:

1. **Parameter Tuning Set (Seeds 2001–2010):**
   - 10 independent seeds used exclusively for hyperparameter tuning.
   - Evaluated to determine optimal contraction-expansion coefficients ($\beta$), rotation step sizes ($\Delta\theta$), and mutation rates ($p_m$).
   - Frozen parameters written to `configs/phase5_parameters.json`.

2. **Parameter Validation Set (Seeds 3001–3010):**
   - 10 independent validation seeds used to verify stability and prevent catastrophic overfitting.
   - Evaluated without further modification to any hyperparameters.

3. **Final Matched Benchmark Set (Seeds 1001–1030):**
   - 30 matched random seeds (1001 through 1030) identical to Phase 4.
   - Exact pairwise seed pairing across all 11 algorithms:
     - 6 Ablation variants: A0, A1, A2, A3, A4, A5
     - 5 Baselines: DE, PSO, GA, Random, NSGA-III
   - **Total Benchmark Evaluations:** $11 \times 30 \times 2,500 = 825,000$ objective evaluations.
   - **Zero Retuning Rule:** Absolutely zero hyperparameter tuning was conducted after observing seed 1001–1030 results.

---

## 3. Dataset Integrity & Cryptographic Hashes

All surrogate prediction models and baseline fleet configurations originate from the peer-reviewed DTU FuelCast telemetry dataset and Phase 4 frozen configuration.

| File Name | Path | SHA-256 Checksum |
| :--- | :--- | :--- |
| `CPS_Poseidon.parquet` | `scratch/fuelcast/CPS_Poseidon.parquet` | `e2b7e1fa42e185ab9d87baef9271630b701bcbf53fca8552631cf247f111f181` |
| `CPS_Triton.parquet` | `scratch/fuelcast/CPS_Triton.parquet` | `102fc2d8c366e4a2d8d867c293739775f0a0e5bfa76722d57279bc98ea91e7ee` |
| `OSS_Ceto.parquet` | `scratch/fuelcast/OSS_Ceto.parquet` | `2495b4105bfa79f61b0fa55b853549fbfe560fa3ce97e3fef570bc6c31826019` |
| `phase5_parameters.json`| `configs/phase5_parameters.json` | `dfa43878ccbf15b94e09f583561a03f44358a9e29a8d9b1c7f53a1a9e9a4f472` |

---

## 4. Frozen Algorithm & Hyperparameter Configurations

All algorithms were executed using the parameters stored in `configs/phase5_parameters.json`:

```json
{
  "qpso": {
    "beta_max": 1.0,
    "beta_min": 0.5,
    "pop_size": 30
  },
  "qiea": {
    "delta_theta_max": 0.05,
    "delta_theta_min": 0.01,
    "pop_size": 30
  },
  "de": {
    "F": 0.5,
    "CR": 0.7,
    "pop_size": 30
  },
  "pso": {
    "w": 0.729,
    "c1": 1.494,
    "c2": 1.494,
    "pop_size": 30
  },
  "ga": {
    "crossover_prob": 0.8,
    "mutation_prob": 0.1,
    "pop_size": 30
  },
  "hybrid_qi": {
    "qpso_beta_max": 1.0,
    "qpso_beta_min": 0.5,
    "qiea_delta_theta": 0.03,
    "pop_size": 30
  }
}
```

### Constraint & Evaluation Settings
- **Common Evaluator:** `src/evaluator/common_evaluator.py::CommonFleetEvaluator`
- **Evaluation Budget:** Exactly 2,500 physical calls to `evaluator.evaluate()` per run.
- **Penalty Factor ($w_c$):** $1,000.0$ per unit constraint violation.
- **Deb Comparator:** Implemented in `CommonFleetEvaluator.deb_compare()`.

---

## 5. Single-Command Full Reproduction

To reproduce all unit tests, tuning, benchmark runs, statistics, figures, and validation results from scratch, execute:

```powershell
# Run the complete test suite (100% passing required)
python -m pytest tests/test_phase5_verification.py -v

# Run the master Phase 5 benchmark pipeline
python scripts/run_phase5_master.py
```

### Script Execution Breakdown
The master pipeline executes the following stages automatically:
1. **Stage 1 (Unit Testing):** Validates Q-bit normalization, Deb comparator, repair idempotency, and budget counting.
2. **Stage 2 (Exact Benchmark):** Runs Level 1 exhaustive search on small fleet instance to verify $J^* = 873.2265$.
3. **Stage 3 (Full Benchmark):** Executes 30 seeds (1001–1030) for A0, A1, A2, A3, A4, A5, DE, PSO, GA, Random, and NSGA-III.
4. **Stage 4 (Statistical Pipeline):** Computes Friedman omnibus test, paired Wilcoxon + Holm-Bonferroni correction, permutation tests (100k resamples), and bootstrap 95% CIs.
5. **Stage 5 (Validation & Scalability):** Performs failure taxonomy classification and fleet scalability benchmarks ($D=30$ to $600$).
6. **Stage 6 (Visualization Engine):** Renders all 18 publication-ready figures to `PHASE5/figures/`.

---

## 6. Artifact Verification Checksum Matrix

All generated CSV output files have been cryptographically hashed and verified against the official Phase 5 master ledger:

| Result Artifact | Record Count | MD5 Checksum |
| :--- | :--- | :--- |
| `PHASE5/results/A0.csv` | 30 runs | `6fb65780a4b3d7b876d299446fec36d1` |
| `PHASE5/results/A1.csv` | 30 runs | `c5db4591f86aa5930214c718bbf6f586` |
| `PHASE5/results/A2.csv` | 30 runs | `928ddb3df71a340b0baefbfe65324ec9` |
| `PHASE5/results/A3.csv` | 30 runs | `8b4383c276a74da4790176fb14878a17` |
| `PHASE5/results/A4.csv` | 30 runs | `0f507b966cf17ae28d9cba704143a411` |
| `PHASE5/results/A5.csv` | 30 runs | `a5f4ebba7d56e01ea313c4c8bf3b867c` |
| `PHASE5/results/DE.csv` | 30 runs | `111867c4a16223e71ba2db7ebf7eeea9` |
| `PHASE5/results/PSO.csv` | 30 runs | `49633ff80175b9f71bf46fc108d0e764` |
| `PHASE5/results/GA.csv` | 30 runs | `03ffb40076a26732f1ea30c0c69ea400` |
| `PHASE5/results/Random.csv` | 30 runs | `d55df27d53b2d18721244d85287e07ca` |
| `PHASE5/results/NSGA3.csv` | 30 runs | `8fbc8bcf8df33036e78ba7a5bebb089d` |
| `PHASE5/results/A5_ABLATION_TABLE.csv` | 11 algorithms | `72622419a4d8721d74659f81a7b8e19e` |
| `PHASE5/results/statistics.csv` | 7 pairwise tests | `9ee3db7bb94801127ba9e3e7f59d57a2` |
| `PHASE5/validation/small_exact.csv` | 7 algorithms | `b782989c47285c13e73b22cf43187b41` |
| `PHASE5/validation/failure_taxonomy.csv`| 11 algorithms | `b6807ba25608c7da4943fcf94038a8e1` |
| `PHASE5/validation/scalability.csv` | 8 configurations | `a4921f0088921e54fb6eeef2291583ff` |
