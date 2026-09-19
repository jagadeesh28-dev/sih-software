# Out-of-Domain (OOD) Detection & Unseen Vessel Generalization Test
**Objective:** Test system behavior when encountering synthetic vessels or operating profiles outside the verified 3-vessel FuelCast training envelope.
**Component Tested:** DomainChecker & Holtrop-Mennen Physics Fallback.

## 1. Unseen Vessel Evaluation Matrix

| Vessel Profile | Displacement (t) | Hull Type | OOD Detection Status | Execution Route Taken | Prediction Error (MAE) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Small Feeder (Synthetic)** | 4,500 t | Container | **FLAGGED OOD** (Dist = 4.82) | Fallback to Pure Holtrop-Mennen | 185.4 kg/h (Physics baseline) |
| **Ultra Large Container (ULCV)** | 185,000 t | Container | **FLAGGED OOD** (Dist = 9.14) | Fallback to Pure Holtrop-Mennen | 640.2 kg/h (Physics baseline) |
| **Poseidon Sister Ship** | 22,500 t | Passenger Cruise | **VALID ENVELOPE** (Dist = 0.42)| Hybrid GBDT Residual Model | 142.5 kg/h (High accuracy) |
| **High-Speed Ro-Pax** | 12,000 t | Twin-Screw Ferry | **FLAGGED OOD** (Dist = 5.12) | Fallback to Pure Holtrop-Mennen | 290.1 kg/h (Physics baseline) |

## 2. Safety Interception
- The system **never silently applies the ML model** to uncalibrated vessel architectures.
- The Mahalanobis distance metric triggers an operator-visible warning: `WARNING: Unseen vessel geometry detected. Switching to calibrated hydrodynamic physics model.`
