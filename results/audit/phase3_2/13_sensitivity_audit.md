# Phase 3.2 Sensitivity Re-Benchmark Audit

## Parameter Response Verification
Controlled sweeps were executed across 5 independent operational parameters holding all other variables constant:
1. **Fuel Price ($400 - 1000\text{ USD/t}$)**: Higher fuel prices incentivize marginal speed reduction (slow steaming) to conserve fuel energy.
2. **Carbon Price ($0 - 250\text{ USD/t}$)**: Increasing carbon cost drives optimal selection toward zero-carbon and low-carbon pathways.
3. **Weather ($1.0 - 5.0\text{ m}$ wave height)**: Added wave resistance monotonically increases propulsion power requirement, demanding higher fuel flow for equivalent speed.
4. **Schedule Deadline ($24 - 40\text{ h}$)**: Tight deadlines force higher transit speeds to avoid quadratic schedule delay penalties.
5. **Robust Uncertainty Weight ($\lambda = 0.0 - 1.0$)**: Conservative policies account for quantile prediction dispersion.

All response curves exhibit realistic physical gradients without artificial penalty cliffs.
