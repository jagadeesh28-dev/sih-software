# Conditional Value-at-Risk (CVaR) Uncertainty & Risk Stress Test
**Mathematical Formulation:** CVaR_alpha(Z) = E[Z | Z >= VaR_alpha(Z)] where Z is the voyage cost/delay distribution across weather draws.
**Risk Parameters Tested:** alpha in {0.80, 0.90, 0.95}, lambda_robust in [0.0, 1.0].

## 1. Impact of Risk Aversion (lambda_robust) on Fleet Decisions

| Lambda (lambda) | Mean Speed (knots) | Mean Fuel (tonnes) | Tail Delay (P95) | Operational Behavior |
| :--- | :--- | :--- | :--- | :--- |
| lambda = 0.0 (Risk-Neutral) | 15.8 kn | 28.4 t | 6.8 hours | Optimizes strictly for calm water average; severe storm delay. |
| lambda = 0.25 (Mild) | 15.2 kn | 29.1 t | 4.2 hours | Minor speed reduction; adds 10% sea margin buffer. |
| lambda = 0.50 (Balanced) | **14.5 kn** | **30.2 t** | **2.1 hours** | **Recommended operational setting: trades +6% fuel for -69% tail delay.** |
| lambda = 0.75 (Conservative) | 13.8 kn | 31.8 t | 1.1 hours | Heavy routing diversion around storm zones. |
| lambda = 1.00 (Minimax) | 12.5 kn | 34.5 t | 0.4 hours | Extreme risk aversion; delays virtually eliminated at high bunker cost. |

## 2. Critical Safety Audit
- **Scientific Truth:** CVaR **does NOT guarantee safety** in a physical sense (e.g. vessel stability or hull structural integrity).
- **Correct Formulation:** CVaR **penalizes expected tail loss** in severe environmental realizations.
- **Physical Feasibility Separated:** Hard physical feasibility (P_B <= 0.90 * MCR) is enforced by physical resistance constraints, completely independent of CVaR.
