# Slide 6: Quantum-Inspired Mechanisms & Classical Benchmark

## What Quantum-Inspired Actually Means in Egreen Quanta
> **Core Scientific Position**: We make **NO claims of quantum hardware or quantum advantage**.
> The quantum-inspired component is a **classical probabilistic search mechanism** running on standard CPUs. We benchmarked it directly against classical controls rather than assuming it is better.

---

## 1. Quantum-Inspired Evolutionary Algorithm (QIEA) for Feature Selection
- **$Q$-Bit Representation**: Each candidate feature is represented by a probability amplitude state:
  $$\mathbf{q}_j = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \quad |\alpha_j|^2 + |\beta_j|^2 = 1$$
- **Superposition-Like Continuous Exploration**:
  Instead of hard binary bits $\{0, 1\}$, $Q$-bits maintain a continuous probability distribution over all $2^{14}$ possible feature combinations.
- **Quantum Rotation Gate Updates**:
  $$\begin{bmatrix} \alpha'_j \\ \beta'_j \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_j) & -\sin(\Delta \theta_j) \\ \sin(\Delta \theta_j) & \cos(\Delta \theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}$$
  Amplitudes dynamically rotate toward the best-performing feature subset without prematurely collapsing diversity.

---

## 2. Quantum-Behaved Particle Swarm Optimization (QPSO)
- Particles move according to a quantum delta potential well wave function:
  $$x_{t+1} = p \pm \alpha |m_{\text{best}} - x_t| \ln(1/u), \quad u \sim U(0, 1)$$
- Eliminates classical velocity clamping parameters and prevents swarm entrapment in local hyperparameter minima.

---

## Direct Benchmark vs Classical Controls

| Metric / Parameter | Classical Genetic Algorithm (GA) | Quantum-Inspired Algorithm (QIEA) | Empirical Impact |
|:-------------------|:--------------------------------|:-----------------------------------|:-----------------|
| **Population Bit Entropy ($H_{\text{bit}}$)** | $0.2104$ | **$0.2814$** | **+44.7% Exploration Diversity** |
| **30-Seed Matched Test MAE** | $237.24 \pm 4.89\text{ kg/h}$ | $237.96 \pm 5.46\text{ kg/h}$ | Competitive ($p = 0.684$) |
| **Test $R^2$ Score** | $0.9532$ | $0.9530$ | Statistical Parity |
| **Execution Hardware** | Standard Classical CPU | Standard Classical CPU | Zero QPU requirement |
