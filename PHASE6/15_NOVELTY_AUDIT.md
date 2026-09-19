# PHASE 6 — STEP 15: PRIOR-ART & NOVELTY AUDIT
## SIH26138 — Egreen Quanta
### Systematic Literature Search, Prior-Art Mapping, and Claim Boundary Verification

**Date:** September 19, 2026  
**Auditor:** Prior-Art / Novelty Claim Auditor, Hostile SIH Jury Reviewer  
**Search Scope:** IEEE Xplore, ScienceDirect, SpringerLink, arXiv, Ocean Engineering, Applied Ocean Research, IEEE Transactions on Evolutionary Computation (2000–2026).  

---

## 1. Literature Taxonomy & Prior-Art Mapping

To prevent inflated or fraudulent novelty claims, every technical concept utilized in Phase 6 was cross-referenced against existing scientific literature:

| Technology / Method | Canonical Prior Art Reference | Prior Art Findings & Scope | What is NOT Novel in Egreen Quanta | Defensible Novelty Claim |
| :--- | :--- | :--- | :--- | :--- |
| **QIEA Feature Selection** | Han & Kim (2002); Zhang (2011) | Q-bit representation with rotation gates has been extensively applied to knapsack, image processing, and generic tabular classification. | The QIEA algorithm, Q-bit concept, and rotation lookup table are **NOT novel**. | We found no directly comparable study applying QIEA to multi-vessel hydrodynamic residual feature selection under IMO resistance constraints. |
| **QPSO Hyperparameter Tuning** | Sun, Feng & Xu (2004); Fang et al. (2010) | QPSO delta-potential well dynamics have been widely used for continuous function optimization and SVM/ANN hyperparameter tuning. | The QPSO equations, mean best attractor ($mbest$), and contraction coefficient are **NOT novel**. | Application to naval architecture physics-guided residual regressor tuning. |
| **MPS Tensor Network Regression** | Stoudenmire & Schwab (2016); Novikov et al. (2015) | Supervised learning with Matrix Product States / Tensor Trains on MNIST and synthetic data. | The MPS structure, trigonometric feature map $\phi(x) = [\cos, \sin]^T$, and tensor train contraction are **NOT novel**. | Empirical stress-testing of MPS on continuous maritime sensor telemetry (resulting in an honest negative finding). |
| **Physics + ML Residual Hybrid** | Petersen et al. (2012); Coraddu et al. (2019) | Gray-box modeling combining Holtrop-Mennen or towing tank resistance curves with neural/tree residuals. | The hybrid residual concept $y = F_{phys} + r_{ML}$ is **well-established in maritime engineering**. | Integration with domain-checking Mahalanobis guardians and conformal prediction intervals. |
| **Maritime Fleet Telemetry** | Dalheim & Steen (2020); DTU FuelCast (2023) | High-frequency sensor logging from Coriolis flow meters, Doppler logs, and GPS on commercial vessels. | The dataset itself is open research telemetry from the DTU FuelCast project. | Multi-vessel operational benchmarking with rigorous LOVO cross-vessel generalization auditing. |

---

## 2. Rigorous Claim Discipline: What Must NOT Be Claimed

In accordance with strict SIH scientific ethics, the following claims are **CATEGORICALLY PROHIBITED**:

1. **PROHIBITED:** Claiming that Egreen Quanta invented QIEA, QPSO, or Matrix Product State regression. (These are established classical algorithms dating from 2002–2016).
2. **PROHIBITED:** Claiming "quantum advantage", "quantum speedup", or "quantum computing". (The entire prediction stack executes on classical x86_64 silicon).
3. **PROHIBITED:** Claiming that Tensor Network / MPS models outperformed classical machine learning on real shipping telemetry. (Experimental evidence conclusively proved that MPS suffered optimization instability and underperformed LightGBM).
4. **PROHIBITED:** Claiming that the predictive models generalize zero-shot to unseen vessel classes. (LOVO validation showed a $3.4\times\text{--}5.2\times$ error increase across different vessels).
5. **PROHIBITED:** Claiming that alternative fuel predictions (LNG, green methanol, ammonia, hydrogen) are experimentally validated. (Real telemetry is conventional oil; alternative fuels are strictly physics-based thermodynamic scenarios).

---

## 3. Defensible Novelty Statement

The defensible novelty of Phase 6 is strictly limited to an **empirical system integration and scientific benchmarking contribution**:

> **Defensible Claim:**  
> *"To the best of our knowledge and within the searched literature, this study represents the first rigorous, open benchmark evaluating both Level 1 (QIEA/QPSO optimized residual learners) and Level 2 (Matrix Product State tensor networks) quantum-inspired prediction architectures against a verified physics + ML baseline on 173,974 records of real multi-vessel commercial telemetry. Furthermore, it establishes the empirical boundaries of cross-vessel generalization (LOVO), conformal predictive uncertainty, and downstream fleet optimization integration."*
