# Slide 1: Problem Definition & Maritime Decarbonization Context

## The Global Maritime Challenge
- **Global Shipping Emissions**: Maritime transport accounts for $\approx 3\%$ of global $\text{CO}_2$ emissions ($>1$ billion tonnes annually).
- **Regulatory Pressure**: IMO Carbon Intensity Indicator (CII) mandates annual carbon intensity reductions; poor ratings (D/E) trigger mandatory corrective action plans and chartering bans.
- **Economic Volatility**: Marine fuel constitutes $40\%–60\%$ of ship operational expenses (OPEX). Minor percentage savings translate to millions of dollars.

---

## The Technical Bottlenecks in Existing Tools
1. **Static OEM Testbed Curves**: Fail in real seas. Neglect added wave resistance, wind drag, shallow water effects, and hull fouling ($\pm 25\%$ error).
2. **First-Principles Hydrodynamic Formulations**: Holtrop-Mennen and empirical resistance models yield high prediction error at sea ($\text{MAE} = 1,885.45\text{ kg/h}, R^2 = -0.5471$) without expensive sea-trial tuning.
3. **Unchecked Black-Box ML**: Standard neural networks hallucinate during extreme storms without out-of-distribution detection or statistical confidence intervals.
4. **Disjoint Voyage Planning**: Route speed planning, bunker fuel choice, port schedule arrival windows, and emissions compliance are optimized in silos rather than holistically.

---

## Problem Statement Target: SIH26138
Develop an intelligent, physics-informed, transparent decision-support system to predict maritime fuel consumption accurately under dynamic sea states and optimize fleet operations while meeting contractual deadlines and emissions regulations.
