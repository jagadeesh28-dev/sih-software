# PHASE 6 — STEP 10: FORENSIC MODEL FAILURE ANALYSIS
## SIH26138 — Egreen Quanta
### Failure Taxonomy, Root Cause Decomposition, and Mitigations

**Date:** September 19, 2026  
**Auditor:** Scientific Code Auditor, Hostile SIH Jury Reviewer  
**Scope:** Complete Failure Analysis across Classical Baselines, QI-C1 (QIEA/QPSO), and QI-C2 (MPS)  

---

## 1. Taxonomy of Predictive Failure Modes

Every predictive failure observed during the Phase 6 benchmark was isolated, categorized, and traced to its governing mathematical or physical root cause:

```
                          [Predictive Failure Matrix]
                                      │
         ┌────────────┬───────────────┼───────────────┬────────────┐
         ▼            ▼               ▼               ▼            ▼
       [F1]         [F2]            [F3]            [F4]         [F5-F7]
    Telemetry   Distribution       Physics      Optimization   Uncertainty
     Quality       Shift          Capacity        Instability  Calibration
    (Sensors)     (LOVO)          (Biases)           (MPS)     (Extremes)
```

---

## 2. Failure Mode Ledger

| Failure Code | Failure Mode Name | Affected Architecture | Frequency (%) | Governing Mechanism & Root Cause | Observed Symptom | Engineering Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F1** | **Doppler Log Velocity Dropout** | All Models | $0.003\%$ | Acoustic bubble aeration under vessel hull causing temporary loss of bottom-track STW. | Sudden zero-reading in `stw_kn` during high-speed transit. | Strict rejection by `DomainChecker`; fallback to kinematic ocean current vector reconstruction. |
| **F2** | **Cross-Vessel Generalization Collapse** | All Models (LOVO) | $100.0\%$ | Unmodeled differences in hull form, block coefficient ($C_B$), engine tuning, and hotel loads. | MAE increases $3.4\times\text{--}5.2\times$ when evaluated on unseen sister vessel. | Require vessel-specific fine-tuning (minimum 2 weeks telemetry) prior to operational dispatch. |
| **F3** | **Unmodeled Physical Drag Bias** | P0 (Physics Only) | $98.4\%$ | Holtrop-Mennen calm water formulation ignores hull biofouling, rough sea margin, and hotel loads. | Large negative structural bias ($-1,883.19\text{ kg/h}$), under-predicting real consumption. | Hybrid residual coupling: $\hat{F} = \max(0, F_{phys} + \alpha \cdot \hat{r})$ restores $R^2$ from $-0.55$ to $0.95$. |
| **F4** | **Tensor Network Gradient Divergence** | P6 (QI-C2-MPS) | $66.7\%$ | Unconstrained SGD across deep tensor-train chain ($d=6$) causes exponential gradient vanishing/explosion. | Prediction residual explodes to $>10^{11}\text{ kg/h}$ across 20 out of 30 random seeds. | Impose gauge-fixing orthogonalization (SVD/QR canonicalization) or reject MPS in favor of tree ensembles. |
| **F5** | **Berth/Anchorage Zero Consumption** | P0 (Physics Only) | $2.4\%$ | Speed Through Water $V_{STW} = 0$ implies $R_{total} = 0 \implies P_B = 0 \implies \text{Fuel} = 0$. | Predicting 0 kg/h while auxiliary boilers/generators consume $300\text{--}600\text{ kg/h}$ at berth. | Enforce minimum physical auxiliary floor model ($P_{aux} = 250\text{ kW}$) in `propulsion.py`. |
| **F6** | **Superposition Saturation** | QIEA (Theoretical) | $0.0\%$ | Repeated rotations driving $|\alpha|^2$ or $|\beta|^2$ to exact $0.0$ or $1.0$, destroying quantum superposition. | Premature convergence to a suboptimal feature subset without further exploration. | Enforce probability amplitude clipping bounds: $|\alpha|^2, |\beta|^2 \in [0.001, 0.999]$. |
| **F7** | **Heavy Sea Interval Under-Coverage** | Quantile ML | $4.8\%$ | Non-Gaussian, fat-tailed error bursts during extreme storm maneuvering ($H_s > 4.5\text{ m}$). | Ground truth exceeds nominal 90% prediction interval during severe sea slamming. | Conformal non-conformity score calibration with adaptive variance scaling conditioned on $H_s$. |

---

## 3. Deep Dive into Failure Mode F4 (MPS Gradient Collapse)

The failure of Candidate QI-C2-MPS represents an important negative scientific result. 
During forward sequential contraction:
$$\hat{r}(x) = M_1(x) M_2(x) \dots M_d(x)$$
The gradient with respect to core tensor $A^{(k)}$ involves the product of all other $d-1$ core tensors:
$$\frac{\partial \hat{r}}{\partial A^{(k)}} = \left( \prod_{j=1}^{k-1} M_j(x) \right) \otimes \phi(x_k) \otimes \left( \prod_{j=k+1}^d M_j(x) \right)$$
If the spectral radius of the core matrices $\rho(M_j) > 1.0$, the gradient scales as $\mathcal{O}(\rho^{d-1})$, causing exponential gradient explosion. 
Conversely, if $\rho(M_j) < 1.0$, the gradient vanishes exponentially. 

In quantum physics (DMRG/TEBD), this is controlled via **left- and right-canonicalization** (enforcing isometric constraints $A^{(k)\dagger} A^{(k)} = I$ via singular value decomposition after every sweep). 
Standard mini-batch SGD without canonicalization cannot maintain this isometry on continuous tabular features, causing the MPS regressor to diverge.
