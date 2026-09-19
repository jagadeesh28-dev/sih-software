# PHASE 6 — STEP 7: CANDIDATE QI-C2 (MPS TENSOR NETWORK) DESIGN
## SIH26138 — Egreen Quanta
### Direct Quantum-Inspired Matrix Product State Residual Regressor

**Candidate Designation:** QI-C2-MPS  
**Formal Scientific Nomenclature:** Quantum-Inspired Tensor-Network Residual Regressor  
**Compliance Level:** Level 2 (Strong Compliance)  
**Scientific Definition:** Unlike QI-C1 (which uses classical ML optimized by QI search), QI-C2 embeds the quantum-inspired mechanism directly into the model hypothesis representation through a factorized tensor-train decomposition of mapped feature states.  

---

## 1. Architectural Representation

The Matrix Product State (MPS) architecture replaces the non-parametric decision tree of LightGBM with a low-rank multilinear tensor contraction:

```
[Normalized Telemetry x_1, ..., x_d]
                 │
                 ▼
     [Quantum Trigonometric Feature Map]
       phi(x_i) = [cos(pi*x_i/2), sin(pi*x_i/2)]^T
                 │
                 ▼
     [Product State Feature Tensor]
       Phi(x) = phi(x_1) ⊗ phi(x_2) ⊗ ... ⊗ phi(x_d)
                 │
                 ▼
     [Matrix Product State (MPS) Contraction]
       <W, Phi(x)> = A^(1)[s_1] * A^(2)[s_2] * ... * A^(d)[s_d]
                 │
                 ▼
          r_hat_MPS(x)  (Predicted Residual)
                 │
                 ▼
        y_hat = max(0, F_physics(x) + r_hat_MPS(x))
```

---

## 2. Mathematical Equations

### 2.1 Trigonometric Quantum Feature Map
Each continuous telemetry feature $x_i \in [0, 1]$ (normalized on training data) is mapped to a 2-dimensional classical state vector:
$$\phi(x_i) = \begin{bmatrix} \cos\left( \frac{\pi x_i}{2} \right) \\ \sin\left( \frac{\pi x_i}{2} \right) \end{bmatrix}$$
**Key Mathematical Property:**
$$\|\phi(x_i)\|^2 = \cos^2\left( \frac{\pi x_i}{2} \right) + \sin^2\left( \frac{\pi x_i}{2} \right) = 1.0 \quad \forall x_i \in [0, 1]$$
Every feature is identically mapped to the surface of a classical 1-qubit Bloch sphere equator. 

### 2.2 Global Product State Representation
The complete observation is embedded in a $2^d$-dimensional Hilbert space:
$$\Phi(x) = \phi(x_1) \otimes \phi(x_2) \otimes \dots \otimes \phi(x_d)$$
Directly storing the weight tensor $W \in \mathbb{R}^{2 \times 2 \dots \times 2}$ would require $2^d$ parameters (exponential curse of dimensionality).

### 2.3 Matrix Product State / Tensor Train Decomposition
To achieve linear scaling, the weight tensor $W$ is factorized into a chain of 3-way core tensors:
$$W_{s_1 s_2 \dots s_d} \approx \sum_{\alpha_1=1}^{\chi} \sum_{\alpha_2=1}^{\chi} \dots \sum_{\alpha_{d-1}=1}^{\chi} A_{\alpha_0, s_1, \alpha_1}^{(1)} A_{\alpha_1, s_2, \alpha_2}^{(2)} \dots A_{\alpha_{d-1}, s_d, \alpha_d}^{(d)}$$
where $\chi$ is the virtual bond dimension (rank), and boundary indices $\alpha_0 = \alpha_d = 1$.

### 2.4 Model Evaluation via Sequential Contraction
Evaluating the scalar residual prediction for a given ship telemetry vector requires contracting each core with the corresponding feature vector:
$$M_k(x) = \sum_{s_k=1}^2 \phi_{s_k}(x_k) A^{(k)}[:, s_k, :] \in \mathbb{R}^{\chi \times \chi}$$
The full prediction is the matrix product:
$$\hat{r}(x) = \left( \prod_{k=1}^d M_k(x) \right) + b$$
Computational complexity of inference scales as $\mathcal{O}(d \cdot \chi^2)$, which is linear in feature dimension $d$.

---

## 3. Training & Optimization Mechanics

- **Core Tensor Initialization:** Core tensors are initialized with zero-mean Gaussian entries scaled by $0.1 / \sqrt{\chi}$ to prevent exponential vanishing/exploding norm during sequential contraction.
- **Loss Formulation:** Mean Absolute Error (MAE) with $L_2$ Tikhonov weight regularization:
  $$\mathcal{L}(A, b) = \frac{1}{B} \sum_{i=1}^B |r_i - (\hat{r}(x_i) + b)| + \frac{\lambda}{2} \sum_{k=1}^d \|A^{(k)}\|_F^2$$
- **Optimization Method:** Mini-batch stochastic gradient descent with analytical backpropagation through the tensor train contraction.

---

## 4. Parameter Count and Complexity Analysis

For $d = 6$ core features (`stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `wind_speed_ms`, `wave_height_m`) and bond dimension $\chi = 4$:
- Core 1: $(1 \times 2 \times 4) = 8$ weights
- Core 2: $(4 \times 2 \times 4) = 32$ weights
- Core 3: $(4 \times 2 \times 4) = 32$ weights
- Core 4: $(4 \times 2 \times 4) = 32$ weights
- Core 5: $(4 \times 2 \times 4) = 32$ weights
- Core 6: $(4 \times 2 \times 1) = 8$ weights
- Scalar Bias: $1$ weight
- **Total Trainable Parameters:** **145 parameters**.

### Comparison Against LightGBM:
- **LightGBM (P2 Baseline):** 4,650 parameters (32x larger parameter footprint).
- **QI-C2-MPS:** 145 parameters.
- **Scientific Significance:** If QI-C2 can deliver competitive accuracy with only 145 parameters, it provides a dramatic compactness advantage over decision tree ensembles.
