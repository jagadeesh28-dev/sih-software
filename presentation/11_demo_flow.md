# Slide 11: Live Demonstration Flow (7 Production Scenes)

## Interactive Demonstration Runner
Executed in terminal via single command:
```bash
python scripts/demo_scenarios.py
```

---

## The Seven Demonstration Scenes

### Scene 1: Normal Vessel Operation (*CPS_Poseidon*)
- **Input**: $\text{STW} = 14.5\text{ kn}$, $\text{Draft} = 7.5\text{ m}$, $\text{Wind} = 5.0\text{ m/s}$, $\text{Wave} = 1.0\text{ m}$.
- **Jury Card**:
  ```text
  Prediction:  2740.86 kg/h
  Model:       QI-C1
  Confidence:  MEDIUM
  OOD:         IN-DOMAIN
  Uncertainty: [1958.39, 3523.33] kg/h
  ```

### Scene 2: High Operating Demand (Schedule Catch-Up)
- **Input**: Speed increased to $19.5\text{ kn}$ ($+5.0\text{ kn}$).
- **Output**: Fuel surges by $+87.3\%$ to $5,133.94\text{ kg/h}$, capturing hydrodynamic cubic power scaling.

### Scene 3: Slow-Steaming Scenario
- **Input**: Speed reduction from $18.0\text{ kn}$ to $15.0\text{ kn}$.
- **Output**: $35.54\%$ simulated fuel reduction under stated operating assumptions.

### Scene 4: Alternative Fuel Scenarios (Invariant Shaft Work)
- **Input**: Same shaft energy demand ($56,176.7\text{ MJ/h}$).
- **Output**: Compares VLSFO, MGO, Bio-Methanol, Green Ammonia, and Liquid $\text{H}_2$ with clear **Scenario Estimate** labels.

### Scene 5: Injected Out-of-Distribution Condition (Storm State)
- **Input**: Extreme hurricane state ($\text{STW} = 33.0\text{ kn}$, $\text{Wind} = 48.0\text{ m/s}$, $\text{Wave} = 14.0\text{ m}$).
- **Output**: Envelope distance $1.366$ triggers WARNING and reroutes to reference model.

### Scene 6: Injected Model Failure & Automatic Safety Routing
- **Input**: Injected runtime C++ memory exception into QI-C1 booster.
- **Output**: Caught in $<2\text{ ms}$; automatically routed to fallback MODEL-REAL-04.

### Scene 7: Heterogeneous Fleet Multi-Objective Optimization
- **Input**: 3 vessels, multi-leg cargo itineraries, strict port arrival windows.
- **Output**: Optimal speed profile $[13.8, 14.2, 12.5]\text{ kn}$ with zero deadline penalties.
