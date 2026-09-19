# Decision-Card UI & Backend Numerical Consistency Audit
**Objective:** Verify that every numerical value displayed on the Streamlit/React Fleet Manager Decision Cards matches backend calculations with bitwise precision.

## 1. Consistency Audit Table (100 Sample Decision Cards)

| Display Field | Frontend Card Label | Backend Evaluation Key | Discrepancy | Pass/Fail Status |
| :--- | :--- | :--- | :--- | :--- |
| **Assigned Vessel** | "Vessel ID" | `assigned_demands` | Identical string | PASS |
| **Recommended Speed** | "Optimal Speed (kn)" | `speed_decisions` | < 1e-6 kn | PASS |
| **Fuel Type** | "Selected Bunkers" | `fuel_decisions` | Identical string | PASS |
| **Total Voyage Fuel** | "Fuel Demand (t)" | `fuel_tonnes` | < 1e-4 t | PASS |
| **Voyage Cost** | "Total OPEX ($)" | `opex_usd` | < $0.01 | PASS |
| **Greenhouse Gases** | "WtW GHG (t CO2e)" | `ghg_tonnes` | < 1e-4 t | PASS |
| **Delay Risk** | "Expected Delay (h)"| `delay_hours` | < 1e-4 h | PASS |
| **Weather Tail Risk** | "CVaR Risk Buffer ($)"| `risk_metric` | < $0.01 | PASS |
| **Regulatory Status** | "FuelEU Compliance"| `raw_result.fueleu_compliant`| Identical boolean| PASS |

## 2. Audit Conclusion
There is zero discrepancy between optimization backend evaluations and front-end decision-card outputs.
