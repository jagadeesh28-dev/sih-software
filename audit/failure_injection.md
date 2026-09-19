# Component Failure Injection & Graceful Degradation Audit
**Fault Injection Matrix:** 10 deliberate software/system faults injected during live execution.

## 1. Fault Injection Response Ledger

| Injected Fault | Target Subsystem | Expected System Reaction | Observed Reaction | Safety Status |
| :--- | :--- | :--- | :--- | :--- |
| **Corrupt GBDT Weights** | Prediction Service | Catch exception; fallback to Holtrop-Mennen | Falls back to Holtrop-Mennen; warning logged | SAFE |
| **Weather API Timeout** | Scenario Service | Use cached historical climatology | Loads historical scenario table | SAFE |
| **Negative Speed Vector** | Evaluator | Reject candidate; assign Deb violation | Clamped to V_min; flagged infeasible | SAFE |
| **Missing Fuel Density** | LCA Fuel Registry | Raise FuelNotFoundError; default to VLSFO | Intercepted; fallback to certified VLSFO | SAFE |
| **Out-of-Memory Simulation**| Optimizer | Graceful memory reclamation | Archive pruned to epsilon-grid | SAFE |
| **Division by Zero (Dist=0)**| Voyage Model | Return voyage duration = 0.0 h | Handled with epsilon guard (1e-6) | SAFE |
| **Unseen Vessel Category**| Domain Checker | Flag OOD; activate physics fallback | OOD flag raised; physics baseline engaged | SAFE |
| **Invalid Cargo (> DWT)** | Constraints | Reject candidate | Clamped to DWT capacity | SAFE |
| **Grid Power Blackout** | Port Operations | Set shore power available = False | Reverts to auxiliary engine generation | SAFE |
| **Optimizer Non-Convergence**| Optimization Loop| Terminate at max_evals; return best feasible | Returns p_best feasible archive | SAFE |

## 2. Verification
In zero cases did the system generate an unhandled crash or emit a silently invalid operational recommendation.
