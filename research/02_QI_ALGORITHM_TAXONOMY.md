# 02 — QUANTUM-INSPIRED ALGORITHM TAXONOMY
## A Rigorous Classification of Quantum-Inspired Optimization Algorithms

---

## 1. Taxonomy Overview

```
Quantum-Inspired Optimization Algorithms
├── Swarm-Based
│   ├── QPSO (Quantum-Behaved PSO)
│   ├── Discrete QPSO
│   ├── Binary QPSO
│   ├── Adaptive QPSO
│   ├── QPSO + Local Search
│   └── Multi-Objective QPSO (MO-QPSO)
├── Evolutionary / Genetic
│   ├── QIEA (Quantum-Inspired Evolutionary Algorithm)
│   ├── QGA (Quantum Genetic Algorithm)
│   ├── QIDE (Quantum-Inspired Differential Evolution)
│   └── Multi-Objective QIEA
├── Probabilistic Population Algorithms
│   ├── Q-bit Estimation of Distribution Algorithms (QEDAs)
│   └── Quantum-Inspired Compact Genetic Algorithm (QI-cGA)
├── Annealing-Inspired
│   ├── Simulated Quantum Annealing (classical)
│   └── QUBO-based Ising Solvers
└── Hybrid Architectures
    ├── QPSO-DE hybrids
    ├── QIEA + local search
    └── QI + surrogate models
```

---

## 2. ALGORITHM PROFILES

---

### 2.1 Quantum-Behaved Particle Swarm Optimization (QPSO)

**Origin:** Sun, Xu, Fang & Feng (2004), Proceedings of CEC  
**Core Paper:** "A global search strategy of quantum-behaved particle swarm optimization," *CEC 2004*

**Representation:**  
Each particle occupies a position $\mathbf{x} \in \mathbb{R}^D$, no explicit velocity vector.

**Quantum Mechanism:**  
Position update via delta-potential quantum well:
$$x_{i,d}^{(t+1)} = p_{i,d} \pm \beta(t) \cdot |mbest_d - x_{i,d}^{(t)}| \cdot \ln(1/u), \quad u \sim U(0,1)$$

where:
- $p_{i,d} = \phi \cdot pbest_{i,d} + (1-\phi) \cdot gbest_d$, $\phi \sim U(0,1)$
- $mbest_d = \frac{1}{M}\sum_{i=1}^{M} pbest_{i,d}$ (mean best position)
- $\beta(t) \in [0.5, 1.0]$ contraction-expansion schedule

**State/Probability Model:** Implicit — positions are stochastic but not probability distributions

**Exploration:** Heavy-tailed Laplacian perturbations allow global search  
**Exploitation:** Attracts toward $p_{i,d}$ (local attractor) and $mbest$ (global centroid)

**Discrete Variable Handling:**  
⚠️ **POOR**: Designed for $\mathbb{R}^D$ only. Integer values require external rounding. No mechanism for non-ordinal categorical transitions.

**Continuous Variable Handling:** ✅ Excellent  
**Binary Variable Handling:** ⚠️ Requires threshold mapping  
**Categorical Variable Handling:** ❌ Not supported natively  
**Constraint Handling:** External penalty only  
**Multi-Objective:** Requires Pareto-archive extension  
**Complexity:** $O(M \cdot D \cdot T)$

**Strengths:**
- No velocity vector reduces parameters
- Good continuous global search
- Well-studied convergence properties
- Simplicity and reproducibility

**Weaknesses:**
- Continuous space only
- Flat gradient in categorical assignment landscapes causes attractor freezing
- Penalty-only constraint handling leads to Penalty Inversion if $P_{hard} < J_{soft}$
- No diversity mechanism for premature convergence

**Literature Support on Mixed-Variable Limitation:**  
Sun & Xu (2004) explicitly scope QPSO to continuous spaces. Subsequent work on discrete QPSO (multiple authors, 2009–2022) required substantial modification including custom rounding, position clamping, and categorical mutation operators. Research confirms that naive application to categorical spaces produces frequent attractor trapping. [Evidence Class A]

---

### 2.2 QIEA / Quantum-Inspired Evolutionary Algorithm

**Origin:** Han & Kim (2002), "Quantum-Inspired Evolutionary Algorithm for a Class of Combinatorial Optimization," *IEEE Transactions on Evolutionary Computation*, Vol. 6, No. 6, pp. 580-593. DOI: 10.1109/TEVC.2002.804320

**Representation:**  
Q-bit chromosome:
$$Q_i = \begin{bmatrix} \alpha_1 & \alpha_2 & \cdots & \alpha_m \\ \beta_1 & \beta_2 & \cdots & \beta_m \end{bmatrix}$$
where $|\alpha_j|^2 + |\beta_j|^2 = 1$ for each Q-bit $j$.

$|\alpha_j|^2$ = probability of observing state 0  
$|\beta_j|^2$ = probability of observing state 1

**Observation Mechanism:**  
Collapse Q-bit $j$ to binary state by sampling: $b_j = 1$ if $r < |\beta_j|^2$, else $b_j = 0$

**Quantum Rotation Gate Update:**  
$$\begin{bmatrix} \alpha_j' \\ \beta_j' \end{bmatrix} = R(\Delta\theta_j) \cdot \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \quad R(\Delta\theta) = \begin{bmatrix} \cos\Delta\theta & -\sin\Delta\theta \\ \sin\Delta\theta & \cos\Delta\theta \end{bmatrix}$$

Rotation angle $\Delta\theta_j$ is a function of the current Q-bit state relative to the best known solution. This is the primary "learning from elite" mechanism.

**Binary Variable Handling:** ✅ **Native and Excellent** — direct binary observation  
**Categorical Variable Handling:** ✅ With extension to categorical probability vector $P_k = |\alpha_k|^2$ for $K$ categories  
**Continuous Variable Handling:** ⚠️ Requires encoding (e.g., Gray code, amplitude rotation)  
**Constraint Handling:** Feasibility can be integrated via conditional observation  
**Multi-Objective:** MOQIEA variants exist (Qian et al., 2013; Zhang et al., 2018)  
**Diversity Preservation:** Interference and catastrophic mutation operators

**Strengths:**
- ✅ Naturally suited to binary decisions (shore power on/off)
- ✅ Can represent categorical probability distributions for fuel/mode/assignment
- ✅ Rich exploration via superposition of states
- ✅ Convergence guaranteed under mild conditions (Han & Kim 2002)
- ✅ 23+ years of academic validation

**Weaknesses:**
- Continuous variables require extra encoding overhead
- Rotation gate tuning is problem-dependent
- Direct optimization of real-valued parameters (e.g., vessel speed) is less natural

**Complexity:** $O(P \cdot m \cdot G)$ where $P$ = population, $m$ = chromosome length, $G$ = generations

---

### 2.3 QGA — Quantum Genetic Algorithm

**Origin:** Narayanan & Moore (1996); formalized by multiple groups 1996–2002  
**Key Reference:** Han et al. (2023), "Green maritime: An improved quantum genetic algorithm-based ship speed optimization method," *Journal of Cleaner Production*, Vol. 385, 2023, DOI: 10.1016/j.jclepro.2022.135814. [Evidence Class A — VERIFIED]

**Relationship to QIEA:** QGA uses genetic operations (crossover, mutation) over Q-bit chromosomes rather than pure rotation-gate updates. It is QIEA with GA-style evolution.

**Application to Maritime (Verified):**  
Han et al. (2023) applied QGA to ship speed optimization under CII and EU ETS regulations. Key features:
- Speed as continuous variable; regulatory constraint as fitness modifier
- Quantum operators maintain diversity across emission regulation scenarios
- Compared against standard GA

**Assessment for Our Problem:**
- ✅ Directly relevant domain (maritime, emission regulation)
- ✅ Q-bit representation → categorical fuel/mode decisions
- ⚠️ Han et al. optimize speed only; do not address heterogeneous fleet composition or multi-fuel assignment
- ✅ Combinatorial demand assignment is within QGA's natural scope

---

### 2.4 Quantum-Inspired Differential Evolution (QIDE)

**Origin:** Multiple independent groups (2009–2024)  
**Key References:**
- Ali et al. (2020), "A quantum-inspired differential evolution algorithm for solving the generalized symmetric TSP" — applies quantum rotation for solution update
- Various MDPI/arXiv papers 2022–2024 on QIDE for combinatorial and mixed-integer problems

**What Makes QIDE "Quantum-Inspired":**  
Replaces DE's real-valued mutation ($v = x_{r1} + F(x_{r2} - x_{r3})$) with:
1. Q-bit representation of population members
2. Quantum rotation gate for parameter update instead of arithmetic difference

**Actual Search Behavior vs. Standard DE:**  
- QIDE's Q-bit encoding inherits QIEA's diversity-preserving properties
- For real-valued optimization, QIDE frequently reduces to DE with quantum-noise augmentation
- For discrete variables, the Q-bit observation mechanism provides cleaner categorical sampling

**Key Finding:**  
The "quantum" in QIDE is substantive for discrete/binary variables (replaces rounding with probabilistic observation). For continuous variables, QIDE and DE are often statistically indistinguishable when matched for evaluation budget. [Evidence Class B based on 2022–2024 comparative surveys]

**Assessment for Our Problem:**  
Since DE already achieves 100% feasibility on our benchmark, QIDE provides marginal algorithmic benefit in the continuous-speed dimension. Its main value is in providing a principled binary/categorical search for assignment, fuel, and shore decisions — identical to QIEA.

---

### 2.5 Adaptive QPSO Variants

**Adaptive Beta QPSO:**  
Tunes $\beta(t)$ dynamically based on fitness landscape analysis. Addresses premature convergence but not categorical handling.

**Elite-Guided QPSO:**  
Uses elite population subset instead of full $mbest$ computation. Reduces swarm collapse but does not address mixed-variable problem.

**Chaos QPSO (CQPSO):**  
Applies chaotic maps to $\beta$ scheduling. Verified to improve exploration in hybrid discrete-continuous mechanical design problems (Semanticscholar sources, 2022). **Relevant** for our speed/cargo dimensions.

**Diversity-Controlled QPSO:**  
Injects random restarts when diversity metric falls below threshold. Partially addresses swarm attractor trapping. Does not address penalty inversion.

**Hybrid QPSO-DE:**  
Uses DE mutation within QPSO update when particle stagnates. This is the closest existing hybrid to what we might design. However, no published variant applies this to maritime fleet assignment.

---

### 2.6 Multi-Objective QPSO (MO-QPSO)

Multiple authors (2010–2023) extended QPSO to multi-objective optimization using:
- Non-dominated sorting (Pareto front)
- External archive for elite preservation
- Crowding distance for diversity

**Status:** Well-established. Our Pareto analysis can use standard MO-QPSO architecture.

---

### 2.7 Q-bit Estimation of Distribution Algorithms (QEDAs)

**Mechanism:** Builds a probability model over Q-bit amplitudes; samples candidates from this model.

**Strength:** Naturally represents probability distributions over categorical variables.  
**Weakness:** Learning the probability model is computationally expensive.

**Assessment:** Academic interest; not necessary for our fleet problem given QIEA provides equivalent capability with simpler mechanism.

---

## 3. Summary Comparison Table

| Algorithm | Binary | Categorical | Continuous | Constraint | MO | Maturity | Maritime Relevance |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **QPSO** | ⚠️ | ❌ | ✅ | Penalty | Via archive | High | Speed/cargo only |
| **QIEA** | ✅ | ✅ | ⚠️ | Feasibility | MOQIEA | High | Assignment/fuel/shore |
| **QGA** | ✅ | ✅ | ⚠️ | GA-style | Yes | High | Maritime speed (Han 2023) |
| **QIDE** | ✅ | ✅ | ⚠️ | Penalty | Yes | Medium | Limited maritime |
| **Adaptive QPSO** | ⚠️ | ❌ | ✅ | Penalty | Via archive | Medium | Speed/cargo |
| **Chaos QPSO** | ⚠️ | ❌ | ✅ | Penalty | No | Low | Speed |
| **Hybrid QPSO-DE** | ⚠️ | ❌ | ✅ | Penalty | Via archive | Low | Speed only |
| **MO-QPSO** | ⚠️ | ❌ | ✅ | Penalty | ✅ | Medium | Speed/cargo Pareto |
| **Hybrid QIEA-QPSO** | ✅ | ✅ | ✅ | Feasibility-first | ✅ | **None published** | **Our target** |
