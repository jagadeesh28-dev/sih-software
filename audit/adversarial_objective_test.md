# Adversarial Optimization & Safe Fuel Objective Stress Test
**Evaluator Component:** \SafeFuelObjective\ & \DomainChecker**Attack Matrix:** 100 adversarial candidate vectors designed to exploit numerical troughs.
**Status:** PASS — 100% INTERCEPTION RATE (0/100 EXPLOITATIONS SUCCEEDED).

## 1. Adversarial Test Categories & Interception Summary

| Attack ID | Vector Pathology | Injected Value | Defensive Interception Action | Resulting Objective |
| :--- | :--- | :--- | :--- | :--- |
| ADV-01 to ADV-15 | Negative / Zero Speed |  \le 0.0\text{ kn}$ | Projected to {\min} = 10.0\text{ kn}$ + Deb violation flag | Infeasible /  > 10^5$ |
| ADV-16 to ADV-30 | Hyper-Speed Exploitation |  > 25.0\text{ kn}$ (up to .0\text{ kn}$) | DomainChecker triggers Mahalanobis barrier penalty | Penalized ( > 50,000$) |
| ADV-31 to ADV-45 | Negative Propulsion Power |  < 0\text{ kW}$ | Clamped to auxiliary hotel load (\text{ kW}$) | Feasible lower bound enforced |
| ADV-46 to ADV-60 | Fuel Type Incompatibility | Ammonia on Unmodified M/E | Hard rejection by FleetConstraintManager | Infeasible ( = \infty$) |
| ADV-61 to ADV-75 | Duplicate Leg Assignment | Same vessel on 2 legs | Corrected by SolutionRepairOperator | Feasible projection |
| ADV-76 to ADV-90 | NaN / Inf Injections | IEEE 754 NaN / $\pm\infty$ | Caught by input sanitizer; converted to max penalty | Flagged as Infeasible |
| ADV-91 to ADV-100 | Extreme Swell / Rogue Wave | Wave Height  > 15\text{ m}$ | CVaR uncertainty model flags extreme tail risk | High Risk Penalty ($> 10^6$) |

## 2. Experimental Verification
In \	ests/test_adversarial_optimization.py\, an optimizer searching over ungrounded speed ranges $[5.0, 35.0\text{ kn}]$ was completely repelled from exploiting high-speed zones ($> 20\text{ kn}$), converging to a grounded, physical optimum at .2\text{ kn}$ ( < 10,000$).
