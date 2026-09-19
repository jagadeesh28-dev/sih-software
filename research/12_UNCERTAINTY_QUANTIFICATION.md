# 12 — UNCERTAINTY QUANTIFICATION IN QI OPTIMIZATION
## RQ17: How Should Uncertainty Be Modeled and Propagated?

---

## 1. Sources of Uncertainty in SIH26138

| Source | Type | Magnitude | Impact |
|:---|:---|:---:|:---|
| Weather (wave, wind, current) | Aleatory | High | ±15–25% fuel consumption |
| Fuel price (LNG, Methanol) | Aleatory | High | ±20–35% cost |
| Surrogate model error (telemetry) | Epistemic | Low-Medium | ±5–10% fuel |
| Port congestion / delay | Aleatory | Medium | ±10–20% schedule |
| Demand uncertainty | Aleatory | Low | ±0–5% in planning horizon |
| CII reference value (annual) | Epistemic | Low | Regulatory parameter |

---

## 2. Uncertainty Representation

### 2.1 Scenario-Based Uncertainty (Current Approach)

Current Phase 4 uses $S = 4$ weather scenarios with equal probability:
$$J(\mathbf{x}) = \frac{1}{S} \sum_{s=1}^{S} J(\mathbf{x}, \omega_s)$$

This is the **expected value** objective. It is simple, interpretable, and implementable but:
- Under-weights tail risk (extreme weather events)
- With $S=4$ scenarios, Monte Carlo variance is high
- Does not distinguish risk-averse from risk-neutral operators

### 2.2 CVaR (Conditional Value-at-Risk)

**Definition:** $\text{CVaR}_\alpha(J) = \mathbb{E}[J \mid J \geq \text{VaR}_\alpha(J)]$

For our problem, $\alpha = 0.95$: CVaR₀.₉₅ is the expected cost in the worst 5% of weather scenarios.

**Objective:** $J_{robust}(\mathbf{x}) = (1-\lambda) \cdot \mathbb{E}[J] + \lambda \cdot \text{CVaR}_{0.95}[J]$

where $\lambda \in [0, 1]$ is risk aversion weight ($\lambda = 0$: risk-neutral; $\lambda = 1$: worst-case focus).

**CVaR computation:**
$$\text{CVaR}_\alpha(J) \approx \frac{1}{S(1-\alpha)} \sum_{s: J_s > q_\alpha} J_s$$

where $q_\alpha$ is the $\alpha$-quantile of $\{J_s\}_{s=1}^S$.

**Required scenarios:** $S \geq 50$ for reliable CVaR₀.₉₅ estimation (otherwise quantile estimation is noisy). Recommend $S = 50$ for Phase 5.

### 2.3 Surrogate Model Uncertainty

The telemetry-calibrated surrogate $\hat{J}(v, s_v, f_v)$ has prediction uncertainty $\sigma_{surrogate}(v, s_v)$ from the regression.

**Propagation:** Use Monte Carlo uncertainty propagation:
$$J_{with\_uncertainty} = \hat{J} + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2_{surrogate})$$

Over 5 Monte Carlo samples per surrogate call, this adds negligible computational cost.

---

## 3. Interaction Between Uncertainty and QI Optimization

### 3.1 QPSO Under Uncertainty

QPSO's attractor update uses a single fitness value per particle position. Under uncertainty, the fitness evaluation is stochastic. This means:
- The personal best $pbest$ may record a "lucky" low-cost evaluation that is not reproducible
- The global best $gbest$ can become an artifact of the weather scenario sample, not a true optimum

**Mitigation:** Use the mean of 5 fitness evaluations per position update (computational cost: 5× evaluations). This stabilizes the attractor.

### 3.2 QIEA Under Uncertainty

The Q-bit rotation gate update:
$$\Delta\theta_j = f(x_j^{(current)}, x_j^{(best)})$$

requires that $x^{(best)}$ is reliably better than $x^{(current)}$. Under noisy fitness, the comparison may be reversed for adjacent solutions.

**Mitigation:** Use bootstrapped ranking: for each pair of solutions, evaluate $n_{boot}$ times and rank by median. Accept the rotation update only if the probability of the best being better exceeds 0.8.

### 3.3 Hybrid QI-HFO Under Uncertainty

The hybrid inherits both issues. Additional mitigation:
- **QIEA component:** use $n_{eval} = 3$ evaluations per observation to stabilize Q-bit updates
- **QPSO component:** use $n_{eval} = 5$ evaluations per position to stabilize attractor
- **Shared fitness cache:** avoid re-evaluating identical configurations

---

## 4. Uncertainty-Aware Benchmark Protocol

For scientifically defensible uncertainty quantification:

```yaml
uncertainty_protocol:
  weather_scenarios: 50          # Monte Carlo weather samples
  fuel_price_scenarios: 10       # Fuel price uncertainty
  surrogate_mc_samples: 5        # Surrogate uncertainty propagation
  cvar_alpha: 0.95               # CVaR confidence level
  risk_aversion_lambda: 0.3      # Moderate risk aversion
  fitness_evaluations_per_position: 3  # Stability
  total_effective_budget: 10000  # Keep evaluation budget constant
```

**Note:** Increasing scenario count while keeping total budget constant reduces per-position fitness evaluations. With $n_{weather}=50$ scenarios and 10,000 total evaluations, we can afford $10000 / (50 \times n_{pop}) = 5$ generations for $n_{pop}=40$. This is insufficient for convergence.

**Recommendation:** Run Phase 5 with $n_{weather} = 10$ scenarios (balanced accuracy vs. convergence) and a separate uncertainty study with $n_{weather} = 50$ for validation.

---

## 5. Reporting Uncertainty in Results

Per scientific best practices, all reported results must include:

| Metric | Report As |
|:---|:---|
| Best objective value | Mean ± 1SD over 30 seeds |
| Feasibility rate | % with 95% Clopper-Pearson CI |
| CVaR (0.95) | Point estimate + bootstrap CI |
| Surrogate prediction error | RMSE on held-out telemetry |
| Algorithm comparison | Wilcoxon p-value + Hodges-Lehmann Δ + BCa 95% CI |
| Convergence speed | First generation achieving 95% of final quality |
