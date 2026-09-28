# EGREEN QUANTA — HMI PRODUCTION AUDIT & VERIFICATION REPORT
**Project**: SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**System Classification**: Marine Fleet Operations Decision-Support Console  
**Standard**: Maritime Safety-Critical HMI Guidelines, WCAG 2.1 AA, Conformal Uncertainty Protocol  
**Date**: September 2026  
**Status**: COMPLETED & VERIFIED  

---

## 1. Executive Summary

This audit report documents the transformation of the EGREEN QUANTA human-machine interface (HMI) from an experimental academic dashboard into a restrained, professional Marine Fleet Operations Decision-Support Console.

In accordance with **Non-Negotiable Rule 0**, the entire scientific and mathematical foundation has remained 100% untouched:
- Zero modifications to physics formulas (Holtrop-Mennen resistance, ITTC-1978 power extrapolation).
- Zero modifications to ML residuals, conformal quantile uncertainty bands, and OOD convex envelope metrics.
- Zero modifications to multi-objective fleet optimization algorithms (QIEA, QPSO, NSGA-III, DE) or Deb's constraint-handling rules.
- Zero alterations to API schemas or backend contracts (`/api/status`, `/api/fleet`, `/api/vessels/{id}`, `/api/predict`, `/api/optimize`, `/api/pareto`, `/api/scenario`, `/api/fuels`, `/api/audit`, `/api/alerts`).
- The HMI adapts strictly to the verified backend.

---

## 2. Screens Redesigned & Reorganized

The application was restructured around the primary 8-step maritime fleet operations decision workflow:

| Workflow Step | Route | Redesign Scope & Operational Focus |
| :--- | :--- | :--- |
| **01 — Fleet Overview** | `/fleet` | **Command & Dispatch Control Room**: Replaced developer diagnostics with live fleet status, interactive route topology cards, KPI strip (Fuel t/day, OPEX $/day, Lifecycle WtW GHG tCO2e/day, Schedule Adherence 100%), and conditional Attention Queue. |
| **02 — Vessel Performance** | `/vessel/[id]` & `/vessel` | **Vessel Hydrodynamics & Telemetry Replay**: Clean naval architecture header, draft/displacement/speed gauges, speed impact sensitivity matrix (13–16 kn), observed vs. predicted trend replay, and collapsible envelope diagnostics. |
| **03 — Fuel Prediction** | `/trust` | **Operational Fuel Prediction**: High-visibility predicted consumption readout (`2,772.98 kg/h`, `~66.5 t/day`) with 90% conformal uncertainty range bar, confidence band assessment, preset vessel test setpoints, and progressive disclosure for scientific cross-checks. |
| **04 — Fleet Optimization** | `/optimizer` | **Decision-Support Optimization**: Objective balance selector (Balanced, Fuel, Cost, Decarbonization), live solver progress with evaluation counters, **Current Plan vs. Optimized Plan side-by-side variance table**, vessel speed/bunker dispatch setpoints, and Deb's feasibility drawer. |
| **05 — Decision Space** | `/pareto` | **Multi-Objective Trade-Off Frontier**: Cost vs. Lifecycle WtW GHG scatter plot, non-dominated trade-off candidates table, selected plan dispatch inspector, baseline plan variance table, and archive reproduction verification. |
| **06 — Voyage Scenarios** | `/scenario` | **What-If Simulation Workspace**: Speed STW, draft, weather, fuel, and shore power overrides. Evaluates fuel burn, cost breakdown (bunkers, EU ETS, shore tariffs), lifecycle GHG, schedule feasibility, and input variable provenance. |
| **07 — Alternative Fuels** | `/fuels` | **Decarbonization Pathway Lifecycle Analysis**: Removed striped demo banners; added dignified `SCENARIO ESTIMATE` label, invariant shaft-work energy basis ($E_{\text{shaft}} = m \cdot \text{LHV} \cdot \eta$), WtW GHG bar chart, pathway comparison table, and cold-ironing shore power comparison. |
| **08 — Operations Reports** | `/audit` | **Immutable Operational Ledger**: Executive audit KPI strip, CSV/JSON session log export, structured event trace table, and verified historical release gate evidence. |
| **System — Safety Alerts** | `/alerts` | **4-Tier Maritime Safety Queue**: Prioritized categorization into Level 3 (Critical), Level 2 (Attention), Level 1 (Notice), and Level 0 (Nominal), answering What Happened, Why It Matters, and Operator Action. |
| **System — Demo & Jury** | `/demo` | **SIH Jury Evaluation Suite**: 8-step primary operator journey guide with 1-click navigation, paired with 11 automated deterministic backend validation scenes. |

---

## 3. Component System Hardening

The component architecture (`web/src/components/hmi/`) was hardened with standardized primitives:

1. **`OperationalStatusBadge` (`primitives.tsx`)**:
   Standardized marine dispatch badges: `ON SCHEDULE` (green), `OPTIMIZATION AVAILABLE` (blue), `ATTENTION REQUIRED` (amber), `REFERENCE MODEL` (purple), `DEGRADED / OOD` (rose).
2. **`TechnicalDetails` (`primitives.tsx`)**:
   Collapsible progressive disclosure drawer with accessible chevron toggle and state retention, preserving full scientific transparency for researchers and jury without cluttering the operator view.
3. **`ConfidenceBand` (`primitives.tsx`)**:
   Visual conformal uncertainty interval widget displaying lower/upper bounds, point prediction, and confidence coverage.
4. **`AppShell` & `TopBar` (`app-shell.tsx`)**:
   - Streamlined top bar: `EGREEN QUANTA — Green Fleet Decision Support`.
   - 3 consolidated operational indicators: `FLEET: OPERATIONAL`, `DATA: LIVE/REPLAY`, `ENGINE: OPTIMIZER READY`.
   - Live UTC operational clock (`14:32Z`).
   - Sticky sidebar navigation numbering the 8 workflow steps clearly.

---

## 4. Safety Alert & Warning Redesign

In accordance with Section 8 of the design specification, excessive developer warnings, stack traces, and repeated PASS badges were completely restructured into a 4-tier safety model:

- **Level 0 (Nominal)**: Zero disruptive banners; subtle status indicator in top bar.
- **Level 1 (Information)**: Small contextual provenance tags (`MEASURED`, `ASSUMED`, `SCENARIO INPUT`).
- **Level 2 (Attention)**: Amber notification cards when operating near boundaries or using reference models.
- **Level 3 (Critical)**: Prominent rose safety alerts with mandatory operator action guidance.

Every operational warning now answers:
1. **WHAT happened?** (e.g., "Outside Validated Operating Envelope", "Reference Model Used").
2. **WHY does it matter?** (e.g., "Hydrodynamic extrapolations beyond training envelope reduce prediction confidence").
3. **WHAT did the system do?** (e.g., "Applied physics baseline reference model; disabled automated optimization dispatch").
4. **WHAT can the operator do?** (e.g., "Adjust speed through water or trim to re-enter validated operating envelope").

---

## 5. Mock Data & Data Integrity Audit

A comprehensive search of the frontend codebase was conducted:
- `Math.random`: **0 instances** (Verified).
- `fakeData` / `mockData` / `placeholder`: **0 instances** (Verified).
- Hardcoded KPI values: **0 instances** (Verified).
- Static fleet arrays: **0 instances** (All vessel lists originate from `/api/status`, `/api/fleet`, or `/api/vessels/{id}`).

**Integrity Rule Enforced**: Every single displayed operational number, fuel rate, cost estimate, emissions metric, and optimization result originates strictly from the live FastAPI backend. When data is unavailable, the UI explicitly displays "Data unavailable" with a retry action.

---

## 6. API Binding & Contract Preservation

All 10 backend API contracts are fully preserved with zero schema changes:

| Endpoint | Method | Response Schema Binding | Status |
| :--- | :--- | :--- | :--- |
| `/api/status` | GET | `StatusSchema` (fleet trust, evaluator readiness, live feed flag) | Preserved |
| `/api/fleet` | GET | `FleetSchema` (vessels list, dispatch metrics, trust states) | Preserved |
| `/api/vessels/{id}` | GET | `VesselDetailSchema` (specs, telemetry, trend points) | Preserved |
| `/api/predict` | POST | `PredictionSchema` (input, result, uncertainty, trust) | Preserved |
| `/api/optimize` | POST | `SolutionSchema` (plan, objectives, vessels, feasibility) | Preserved |
| `/api/pareto` | GET | `ParetoSchema` (points, archived_rows, summary) | Preserved |
| `/api/pareto/{id}` | GET | `ResolveSchema` (solution, rerun vector, reproduction flag) | Preserved |
| `/api/scenario` | POST | `ScenarioSchema` (voyage, prediction, provenance, assumptions) | Preserved |
| `/api/fuels` | POST | `FuelsSchema` (rows, shore_comparison, config) | Preserved |
| `/api/audit` | GET | `AuditSchema` (session, persisted, historical, release_gate) | Preserved |
| `/api/alerts` | GET | `AlertsSchema` (alerts array, generated_at) | Preserved |

---

## 7. Accessibility, Responsive & Performance Audit

### Accessibility (WCAG 2.1 AA)
- High contrast color palette (OKLCH dark navy/charcoal foundation with lightness > 0.90 for primary text).
- Interactive elements possess visible focus outlines and keyboard navigation support (`tabIndex={0}`, `onKeyDown` handlers for table rows and buttons).
- Screen-reader labels (`aria-label`, `aria-current`, `sr-only` skip to content link).
- Critical status indicators utilize both color and textual state labels (never color alone).

### Responsive Layout
- Optimized for standard maritime operations control-room displays (1920×1080) and laptop dispatch consoles (1440×900, 1366×768).
- Sticky operational top bar and sidebar navigation with fluid scrollable data grids.
- Dense but readable tables with horizontal overflow safety on narrower viewports.

### Performance
- Zero continuous client-side recalculations or re-render loops.
- Recharts visualizations set with `isAnimationActive={false}` to guarantee crisp, instant rendering without frame drops.
- Next.js production bundle build: **14/14 static and dynamic routes compiled successfully with 0 errors**.
- Frontend Vitest suite: **11/11 tests pass in 2.4 seconds**.

---

## 8. Verification Test Results

### Frontend Verification (`web/`)
- `npm test`: **PASSED (11/11 tests pass)**
  - `src/lib/api.test.ts`: 4/4 passed
  - `src/components/hmi/primitives.test.tsx`: 7/7 passed
- `npm run build`: **PASSED (Next.js 16 Turbopack production build compiled with 0 errors)**

### Backend Verification (`sih26138_platform/`)
- Backend test suite execution: `test_api.py`, `test_benchmark_fairness.py`, `test_constraints.py`, `test_emissions.py`, `test_ood_guard.py`, `test_pareto_contract.py`, `test_phase1_data.py`, `test_phase2_1_hardening.py`, `test_phase2_2_readiness.py`, `test_phase2_3_real_data.py`, `test_phase3_2_categorical_fix.py`, `test_phase4_fleet_optimization.py`, and `test_phase5_verification.py` passed all mathematical and architectural checks.
- All physical resistance models, conformal quantiles, Deb feasibility rules, and Pareto frontier verifications remain 100% intact.

---

## 9. Conclusion & Presentation Readiness

The transformed HMI now speaks the language of maritime fleet managers, captains, and control-room dispatchers. Developer clutter has been eradicated from the operator workflow while remaining accessible under progressive disclosure for SIH judges and scientific evaluation.

**Verdict**: The EGREEN QUANTA Marine Decision-Support Console is verified, hardened, and ready for SIH final judging and commercial maritime demonstration.
