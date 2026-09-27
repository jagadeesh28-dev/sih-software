# EGREEN QUANTA — PRODUCTION & DEMONSTRATION RUNBOOK
**SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization**
**Operational Execution Guide for Maritime Operators & SIH Evaluators**

---

## 1. Quick-Start Architecture Overview

EGREEN QUANTA runs as a lightweight, zero-cloud-dependency microservice pair:
1. **Backend**: Python 3.10+ FastAPI ASGI server running on `http://127.0.0.1:8000`
2. **Frontend Console**: Next.js 16 (React 19 / Turbopack) running on `http://localhost:3000`

---

## 2. Environment Startup Instructions

### Step 2.1 — Start the Backend Server
From the repository root directory:
```bash
python -m uvicorn api.main:app --port 8000 --host 127.0.0.1
```
Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```
Health Check Verification:
```bash
curl http://127.0.0.1:8000/api/status
```
Expected response: JSON object with `"data_mode": "SIMULATION"`, `"evaluator_ready": true`.

### Step 2.2 — Start the Marine HMI Frontend
In a second terminal, navigate to `web/` and launch the dev server:
```bash
cd web
npm run dev
```
Open `http://localhost:3000` in Google Chrome or Edge.

---

## 3. Step-by-Step Operator Demonstration Script

Follow this sequential workflow during an evaluation:

### Step 1 — Fleet Overview (`/fleet`)
1. **Observe**: The Dispatch Status Strip showing 3 active monitored hulls (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`).
2. **Examine**: The aggregated fleet metrics (Fuel consumption, OPEX per hour, Well-to-Wake GHG per hour).
3. **Check Data Freshness**: Note the compact indicator `DATA ● Calibrated Replay` in the TopBar. Point out that the system distinguishes between live telemetry (not connected) and recorded sea-trial data.

### Step 2 — Vessel Performance Profile (`/vessel/CPS_Poseidon`)
1. **Inspect**: Telemetry replay of historical voyages for `CPS_Poseidon`.
2. **View Speed Sensitivity**: Review the hydrodynamic speed vs. fuel curve. Notice the non-linear cubic surge between 14.5 kn and 19.5 kn.
3. **Expand Technical Details**: Click `▼ View Technical Details` to reveal naval hull dimensions and feature scalers.

### Step 3 — Hydrodynamic & ML Prediction (`/trust`)
1. **Nominal Evaluation**: Select the `CPS Poseidon (Cruise 35,000 t)` preset (STW=14.5 kn, Draft=7.5 m, VLSFO).
2. **Click**: `Calculate Fuel Prediction`.
3. **Observe**:
   - Point estimate: `2,772.98 kg/h` (approx. 66.5 tonnes/day).
   - Finite-sample conformal prediction interval: `[1,952 — 3,594] kg/h` at 90% coverage.
   - Confidence: `Normal`.
   - Data status: `Current`.
4. **Stress Test (OOD / Severe Weather)**: Set Wave Height to `14.0 m`, Wind Speed to `48.0 m/s`, Speed to `33.0 kn`.
5. **Observe**: System flags `OUT OF DOMAIN (OOD)` with critical status; raw ML is withheld and physics bounds are highlighted.

### Step 4 — Fleet Optimization (`/optimizer`)
1. **Select Objective**: Choose `Balanced Dispatch (Fuel + Cost + GHG)` or `Fuel Minimization Focus`.
2. **Select Algorithm**: `Quantum-Inspired Hybrid Optimizer (QIEA + QPSO)` with 2,500 evaluations budget.
3. **Click**: `Execute Fleet Optimization`.
4. **Watch Live Convergence**: The progress bar updates in real time as feasible solutions are sampled using Deb's parameter-free feasibility rule.
5. **Review Recommendation Card**:
   - Check `Fuel consumption`, `Operating cost`, `Lifecycle GHG`, and `Schedule impact`.
   - Notice constraint status: `FEASIBLE (All Hard Boundaries Satisfied)`.
6. **Operational Constraints Checklist**: Verify all 5 constraints are satisfied (cargo deadweight, schedule, speed, fuel, shore power).
7. **Human Approval Action**: Click `Review Recommendation → Approve Decision` with an optional seamanship remark.
8. **Export Decision Record**: Click `Export JSON Record` and `Export CSV` to demonstrate complete reproducibility.

### Step 5 — Decision Space Trade-off Frontier (`/pareto`)
1. **Inspect Scatter Plot**: View the non-dominated Pareto frontier plotting Voyage OPEX vs. Lifecycle GHG.
2. **Examine Candidates**: Click any diamond to inspect `OPTION A (Lower-Cost Option)` vs. `OPTION B (Lower-GHG Option)`.
3. **Variance Table**: Compare the selected dispatch plan against the baseline unoptimized fleet assignment.

### Step 6 — Scenario Analysis & Sensitivity (`/scenario`)
1. **Modify Operating Assumptions**: Adjust fuel price ($/t) or EU ETS carbon allowance price ($/tCO2e).
2. **Observe**: Real-time recalculation of OPEX and Well-to-Wake emissions under IMO MEPC.391(81) guidelines.

### Step 7 — Alternative Fuels & Cold Ironing (`/fuels`)
1. **Review Scenario Estimates**: Note the prominent `SCENARIO ESTIMATE` badge on all alternative fuel projections.
2. **Explain Basis**: Invariant shaft work energy equivalence ($E = \text{const}$).
3. **Compare Shore Power**: View auxiliary emissions savings during port stays when utilizing cold-ironing electrical grids.

### Step 8 — Operations Reports & Decision Ledger (`/audit`)
1. **Audit Trail**: Review the immutable record of all operator acceptances stored in SQLite.
2. **Filter & Search**: Search by operator remark or filter by date.
3. **Export Session**: Download the complete operational session ledger in JSON or CSV.

### System Health & Diagnostics (`/health`)
1. **Examine Microservices**: Confirm status, latency (ms), and version for all 7 subsystems:
   - FastAPI Rest Gateway (`ONLINE`)
   - Physics + ML Predictor (`ONLINE`)
   - Quantum-Inspired Optimizer (`ONLINE`)
   - Scenario Simulation Engine (`ONLINE`)
   - OPEX Cost Engine (`ONLINE`)
   - Lifecycle GHG Engine (`ONLINE`)
   - Audit Ledger (`ONLINE`)
2. **Test Role Semantics**: Use the TopBar `Access Control` switcher to switch between `OPERATOR`, `ENGINEER`, and `ADMIN`.

---

## 4. Troubleshooting & Graceful Degraded States

| Symptom | Cause | Automatic Safeguard / Resolution |
| :--- | :--- | :--- |
| `CONNECTION LOST` banner appears | Backend process stopped | Console retains last valid data with `LAST VALID RESULT` timestamp. Restart backend and click `Retry`. |
| `FALLBACK` chip active | Environmental inputs outside primary LightGBM envelope | Automatic fallback routes calculation to reference anchor `MODEL-REAL-04`. |
| `CONSTRAINT FAILURE` on optimizer | Incompatible fuel or unrealistic deadline | System enforces zero hard constraint breaches; adjust arrival deadline or speed boundaries. |
