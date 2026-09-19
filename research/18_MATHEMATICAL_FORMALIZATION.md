# 18 — MATHEMATICAL FORMALIZATION
## Precise Problem Definition and Algorithm Specification

---

## 1. Problem Formulation

### 1.1 Sets and Indices

| Symbol | Definition |
|:---|:---|
| $\mathcal{V}$ | Fleet of $V$ heterogeneous vessels, $|\mathcal{V}| = V = 6$ |
| $\mathcal{D}$ | Set of demand units, $|\mathcal{D}| = D = 8$ |
| $\mathcal{F}$ | Set of fuel modes, $|\mathcal{F}| = K = 4$ |
| $\mathcal{S}$ | Set of weather scenarios, $|\mathcal{S}| = S$ |
| $\mathcal{P}$ | Set of ports on routes |

### 1.2 Decision Variables

| Variable | Type | Domain | Description |
|:---|:---|:---|:---|
| $s_v$ | Continuous | $[s^{min}_v, s^{max}_v]$ | Speed of vessel $v$ (knots) |
| $f_v$ | Categorical | $\{1, \ldots, K\}$ | Fuel mode of vessel $v$ |
| $d_{v,k}$ | Binary | $\{0, 1\}$ | 1 if demand unit $k$ assigned to vessel $v$ |
| $p_v$ | Binary | $\{0, 1\}$ | 1 if vessel $v$ uses shore power at port |

**Complete solution vector:** $\mathbf{x} = (\mathbf{s}, \mathbf{f}, \mathbf{d}, \mathbf{p})$

### 1.3 Objective Function

$$\underset{\mathbf{x}}{\min} \; J(\mathbf{x}) = (1-\lambda)\underbrace{\mathbb{E}_{\omega \sim \mathcal{S}}[J_{total}(\mathbf{x}, \omega)]}_{\text{expected cost}} + \lambda \underbrace{\text{CVaR}_{0.95}[J_{total}(\mathbf{x}, \omega)]}_{\text{tail risk}}$$

where:
$$J_{total}(\mathbf{x}, \omega) = \underbrace{\sum_{v} J_{fuel}(v, s_v, f_v, \omega)}_{\text{fuel cost}} + \underbrace{\sum_{v} J_{delay}(v, s_v, \omega)}_{\text{delay penalty}} + \underbrace{\sum_{v,k} J_{cargo}(v, k, d_{v,k})}_{\text{cargo handling}} + \underbrace{\sum_{v} J_{shore}(v, p_v)}_{\text{shore power savings}}$$

### 1.4 Constraints

**C1 — Demand Partition (hard):**
$$\sum_{v \in \mathcal{V}} d_{v,k} = 1 \quad \forall k \in \mathcal{D}$$

**C2 — Capacity (hard):**
$$\sum_{k \in \mathcal{D}} d_{v,k} \cdot w_k \leq C_v \quad \forall v \in \mathcal{V}$$

**C3 — Vessel-Fuel Compatibility (hard):**
$$f_v \in \mathcal{F}_v \quad \forall v \in \mathcal{V}$$

**C4 — Port-Fuel Availability (hard):**
$$f_v \in \bigcap_{p \in \text{route}(v)} \mathcal{F}_p \quad \forall v \in \mathcal{V}$$

**C5 — Shore Power Eligibility (hard):**
$$p_v \leq \text{portcap}_v \quad \forall v \in \mathcal{V}$$

**C6 — CII Compliance (hard):**
$$\text{CII}(v, s_v, f_v) = \frac{\text{CO}_2(v, s_v, f_v) \cdot \text{CF}_{f_v}}{DWT_v \cdot \text{NM}_v} \leq \text{CII}_{ref}(v) \quad \forall v \in \mathcal{V}$$

**C7 — FuelEU Maritime (fleet-wide soft/hard):**
$$\frac{\sum_{v} \text{Energy}(v, s_v) \cdot \text{GHI}(f_v)}{\sum_{v} \text{Energy}(v, s_v)} \leq GFI_{limit}$$

---

## 2. Hybrid QI-HFO Mathematical Specification

### 2.1 QIEA Component State

For a population of $P$ individuals, the QIEA state at generation $t$ is:

$$\mathcal{Q}^{(t)} = \{Q^{(t)}_1, Q^{(t)}_2, \ldots, Q^{(t)}_P\}$$

where each $Q^{(t)}_i$ consists of:
- **Binary Q-matrix for demand:** $\mathbf{B}^{(t)}_i \in [0,1]^{V \times D}$ (probability of assignment 1)
- **Binary Q-vector for shore:** $\mathbf{b}^{(t)}_i \in [0,1]^V$ (probability of shore power 1)
- **Dirichlet Q-matrix for fuel:** $\mathbf{F}^{(t)}_i \in \Delta^{K-1}_{V}$ (categorical probability vectors)

### 2.2 QPSO Component State

$$\mathcal{X}^{(t)} = \{x^{(t)}_1, x^{(t)}_2, \ldots, x^{(t)}_P\} \subset \mathbb{R}^V$$

Speed particles with:
- Personal best: $\tilde{x}^{(t)}_i$ (best speed vector found by particle $i$)
- Global best: $x^*$ (best speed vector over all particles and time)
- Mean best: $m^{(t)} = \frac{1}{P}\sum_i \tilde{x}^{(t)}_i$

### 2.3 Joint Update Equations

**QPSO speed update:**
$$\phi^{(t+1)}_i \sim U^V(0,1), \quad p^{(t)}_i = \phi^{(t+1)}_i \odot \tilde{x}^{(t)}_i + (1-\phi^{(t+1)}_i) \odot x^*$$
$$u^{(t+1)}_i \sim U^V(0,1), \quad \sigma^{(t+1)}_i \sim \text{Rad}^V (P(\sigma=+1)=0.5)$$
$$x^{(t+1)}_i = p^{(t)}_i + \sigma^{(t+1)}_i \odot \beta(t) \odot |m^{(t)} - x^{(t)}_i| \odot \ln\left(\frac{1}{u^{(t+1)}_i}\right)$$

where $\odot$ denotes elementwise product, $\text{Rad}$ is Rademacher distribution, and $\beta(t) = \beta_0 - (\beta_0 - \beta_f) t/T$.

**QIEA demand Q-bit rotation (binary):**

For each demand Q-bit $B_{i,v,k}^{(t)}$ (probability of assigning demand $k$ to vessel $v$):

Let $d^*_{v,k}$ denote the best observed assignment for demand $k$ on vessel $v$.

$$\Delta\theta_{i,v,k} = f(B_{i,v,k}^{(t)}, d_{i,v,k}^{(obs)}, d^*_{v,k})$$

using the standard Han-Kim rotation angle table:

| $B_{i,v,k}^{(t)}$ | $d_{i,v,k}^{obs}$ | $d^*_{v,k}$ | $\Delta\theta$ |
|:---:|:---:|:---:|:---:|
| ↑ | 0 | 1 | $+\delta$ |
| ↓ | 1 | 0 | $-\delta$ |
| × | 0 | 0 | 0 |
| × | 1 | 1 | 0 |

where $\delta = 0.05\pi$ is the rotation step.

**QIEA fuel Dirichlet-Q update:**
$$F^{(t+1)}_{i,v,k} = \frac{F^{(t)}_{i,v,k} + \eta \cdot \mathbb{1}[f^*_v = k]}{1 + \eta - \lambda F^{(t)}_{i,v,k}}$$

then renormalize to sum to 1.

### 2.4 Observation Functions

**Conditional demand observation (exact):**
$$\hat{d}_{v,k} = \mathbf{1}[v = \text{Categorical}(B_{i,v,k}^{(t)} \cdot \text{cap\_mask}_{v,k})]$$

where cap\_mask normalizes capacity-eligible vessels.

**Fuel mode observation:**
$$\hat{f}_v = \text{Categorical}(F^{(t)}_{i,v,1}, \ldots, F^{(t)}_{i,v,K}) \cap \mathcal{F}_v \cap \mathcal{F}_{port}$$

**Shore power observation:**
$$\hat{p}_v = \mathbb{1}[u < b^{(t)}_{i,v}] \cdot \text{portcap}_v, \quad u \sim U(0,1)$$

---

## 3. Complexity Analysis

| Component | Per-Generation Complexity |
|:---|:---|
| QPSO speed update | $O(P \cdot V)$ |
| QIEA demand observation | $O(P \cdot V \cdot D)$ |
| QIEA fuel observation | $O(P \cdot V \cdot K)$ |
| Fitness evaluation | $O(P \cdot S_{weather})$ |
| QIEA Q-bit rotation | $O(P \cdot V \cdot D)$ |
| QIEA Dirichlet update | $O(P \cdot V \cdot K)$ |
| **Total per generation** | $O(P(VD + VK + S_{weather}))$ |
| **Total over T generations** | $O(T \cdot P \cdot (VD + VK + S_{weather}))$ |

For $P=40$, $V=6$, $D=8$, $K=4$, $S=10$, $T=250$:  
Total = $250 \times 40 \times (48 + 24 + 10) = 820{,}000$ primitive operations.

This is computationally trivial on modern hardware (sub-second per run for pure computation; fitness evaluation is the bottleneck via the surrogate model call).
