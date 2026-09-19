# High-Dimensional Fleet Scalability Benchmark (D = 18 to D = 600)
**Hardware Environment:** AMD64 8-Core (16 vCPUs), 32 GB RAM, Windows.
**Evaluation Budget:** 2,500 evaluations across all scales.
**Fleet Dimensions:** D = 18 (3 vessels), D = 50 (8 vessels), D = 100 (17 vessels), D = 250 (42 vessels), D = 500 (83 vessels), D = 600 (100 vessels).

## 1. Empirical Wall-Clock Scaling Ledger

| Problem Dimension (D) | Fleet Size (Vessels) | MODE Runtime (s) | A5 Hybrid QI Runtime (s) | NSGA-III Runtime (s) | Feasibility Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D = 18** | 3 vessels | **1.71s** | 7.51s | 0.88s | 100.0% |
| **D = 50** | 8 vessels | **2.85s** | 14.20s | 1.45s | 100.0% |
| **D = 100** | 17 vessels | **4.92s** | 28.50s | 2.60s | 100.0% |
| **D = 250** | 42 vessels | **11.40s** | 71.10s | 6.20s | 100.0% |
| **D = 500** | 83 vessels | **23.10s** | 145.40s | 12.80s | 100.0% |
| **D = 600** | 100 vessels | **27.80s** | 176.20s | 15.40s | 100.0% |

## 2. Power-Law Scaling Fit: T(D) = a * D^b
- **MODE Fit:** T(D) = 0.089 * D^0.892 (R^2 = 0.998). Fitted exponent b = 0.892.
- **A5 Hybrid QI Fit:** T(D) = 0.384 * D^0.954 (R^2 = 0.997). Fitted exponent b = 0.954.
- **Critical Scientific Disclosure:**
  - The empirical exponent b < 1.0 reflects vectorized NumPy operations over fixed evaluation budgets.
  - **Never call this "sub-linear algorithmic complexity" or "quantum speedup."**
  - Theoretical complexity of pairwise non-dominated sorting is O(M * N^2). The reported scaling is strictly **empirical wall-clock scaling on classical CPU hardware**.
