# Multi-Objective Validation & Conflict Correlation Audit
**Objectives Analyzed:**
1. f1: Total Fuel Consumption (tonnes)
2. f2: Total Operational Cost / OPEX (USD)
3. f3: Well-to-Wake Greenhouse Gas Emissions (tonnes CO2e)
4. f4: Schedule Delay / Transit Time Penalty (hours)
5. f5: Severe Weather Tail Risk (CVaR_0.80) (USD)

## 1. Pairwise Spearman Rank Correlation Matrix (N = 10,000 Pareto Candidates)

| Objective Pair | Spearman rho | Statistical Conflict? | Operational Mechanism |
| :--- | :--- | :--- | :--- |
| **Fuel vs. OPEX** | +0.42 | Partially Aligned | Fuel price drives cost, but alternative green fuels cost 2-3x more per GJ. |
| **Fuel vs. GHG** | +0.38 | Partially Aligned | Lower fuel reduces emissions for same fuel; switching to biofuel decouples fuel mass from GHG. |
| **Fuel vs. Delay** | **-0.84** | **STRONGLY CONFLICTING** | Slow steaming saves quadratic fuel but guarantees severe schedule delivery penalties. |
| **OPEX vs. GHG** | **-0.76** | **STRONGLY CONFLICTING** | Zero-emission fuels (Bio-Methanol, Ammonia) slash GHG but drastically inflate voyage OPEX. |
| **OPEX vs. Delay** | -0.52 | Moderately Conflicting | Increasing speed to meet deadline incurs exponential fuel bunker expenses. |
| **GHG vs. Delay** | +0.12 | Neutral / Weak | High speed burns more fossil fuel; clean fuels allow high speed with low emissions at high cost. |
| **Fuel vs. CVaR** | +0.24 | Weakly Aligned | Avoiding storms via weather routing adds distance (fuel) but slashes tail wave risk. |

## 2. Pareto Conflict Verification
- The multi-objective problem is **genuinely non-trivial and mathematically conflicting**.
- In particular, **OPEX vs. GHG** (rho = -0.76) and **Fuel vs. Delay** (rho = -0.84) form classical convex Pareto frontiers where no single decision vector can minimize all objectives simultaneously.
