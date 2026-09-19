# Encoding & Solution Representation Benchmark
**Representations Evaluated:**
- R1: Direct Integer Encoding
- R2: Continuous Random-Key Encoding (RK)
- R3: Probability-Vector / Estimation of Distribution (EDA)
- R4: Binary Q-Bit Bloch Angles ($\theta \in [0, \pi/2]$)
- R5: Multi-State Q-Bit / Qudit ($|\psi\rangle = \sum \alpha_i |i\rangle$)
- R6: d-QPSO Latent Representation

## 1. Representation Comparative Ledger

| Code | Representation | Unique Solutions / Budget | Shannon Entropy ($) | Diversity Metric ($) | Feasibility Rate | Mean Hypervolume (^6$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | Direct Integer | 1,420 / 2,500 | 2.14 bits | 84.12 | 86.7% | 142.10 |
| **R2** | Continuous Random-Key | 2,410 / 2,500 | 3.85 bits | 290.22 | 100.0% | 198.45 |
| **R3** | Categorical EDA / Dirichlet | 1,980 / 2,500 | 3.42 bits | 165.30 | 96.7% | 185.20 |
| **R4** | Binary Q-Bit Pairs | 1,890 / 2,500 | 3.21 bits | 145.60 | 93.3% | 178.40 |
| **R5** | Multi-State Q-Bit (A4/A5) | 2,150 / 2,500 | **3.91 bits** | **189.54** | **100.0%** | **247.11** |
| **R6** | d-QPSO Latent Angle | 1,650 / 2,500 | 2.85 bits | 168.49 | 86.7% | 155.80 |

## 2. Entropy vs. Solution Quality Correlation Analysis
- **Diversity vs. Feasibility:**  = 0.42$ ( = 0.02$). Diversity helps avoid premature stagnation, but without Deb's rule, high diversity simply generates infeasible solutions faster.
- **Diversity vs. Hypervolume:**  = 0.68$ ( < 0.001$). High Shannon entropy in R5 enables broad boundary coverage of non-dominated fronts, directly explaining the high hypervolume (.11 \times 10^6$).
- **Critical Caveat:** Diversity is NOT scalar fuel optimization. For single-objective fuel minimization, R2 (continuous random-key + DE) achieves the lowest physical fuel (.70$ vs .45$ for A5, with DE having lower variance).
