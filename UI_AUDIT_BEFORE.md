# EGREEN QUANTA — HMI/UX AUDIT BEFORE REDESIGN
**System**: SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Auditor**: Senior Marine HMI/UX Architect & Safety-Critical Dashboard Designer  
**Scope**: Next.js 16 Web Application (`web/src/`)  
**Date**: 2026-09-26  
**Document Status**: Pre-Implementation Forensic Baseline (`UI_AUDIT_BEFORE.md`)  

---

## 1. CURRENT SCREENS INVENTORY

| Route | Page File | Intended Operational Purpose | Current State & Flaws |
| :--- | :--- | :--- | :--- |
| `/` | `web/src/app/page.tsx` | Entry redirect | Blind redirect to `/fleet`. |
| `/fleet` | `web/src/app/fleet/page.tsx` | Fleet operations overview | Cluttered table with ML internals (`OOD band d=0.00`, `Fallback`, `Trust`); missing maritime route topology and operational status categorization (`ON SCHEDULE`, `OPTIMIZATION AVAILABLE`, `ATTENTION`). |
| `/vessel/[id]` | `web/src/app/vessel/[id]/page.tsx` | Vessel performance detail | Exposes raw feature arrays, booster IDs (`QI-C1-vessel-type`), and cross-check delta tables. Missing compact speed-impact curve (`14 kn baseline, 15 kn +X%`) and clean voyage summary. |
| `/trust` | `web/src/app/trust/page.tsx` | Fuel prediction & confidence | Styled like an ML test form with test options (`bulk carrier (unsupported — tests fallback)`), developer text (`Leave optional fields blank to test missing factors`), and raw model IDs. |
| `/optimizer` | `web/src/app/optimizer/page.tsx` | Heterogeneous fleet optimization | Shows raw RNG seed, raw objective weight sliders, and unformatted Python docstring (`Phase4FleetEvaluator docstring`). Lacks a clear side-by-side **Current Plan vs. Optimized Plan** comparison. |
| `/pareto` | `web/src/app/pareto/page.tsx` | Multi-objective trade-off space | Technically functional 2D scatter chart, but uses terminology like `re-evaluated decision vector`, and dense tabular layout without trade-off compromise guidance. |
| `/scenario` | `web/src/app/scenario/page.tsx` | What-if voyage scenario engine | Form inputs feel like developer database overrides (`blank keeps baseline`). KPIs and trust banners dominate over operational decision insight. |
| `/fuels` | `web/src/app/fuels/page.tsx` | Alternative fuels & shore power | Dominated by a giant diagonal-striped purple disclaimer banner (`SCENARIO ESTIMATE — NOT MEASURED GREEN-FUEL TELEMETRY`). Overwhelms the actual engineering comparison. |
| `/alerts` | `web/src/app/alerts/page.tsx` | Safety & out-of-distribution alerts | Displays an 8-state academic reference catalog even when zero alerts are active. Redundant alerts shown for normal states. |
| `/audit` | `web/src/app/audit/page.tsx` | Audit ledger & compliance trace | Raw JSON dumps inside expandable rows. Dense ledger without clear voyage/energy/cost executive summaries. |
| `/demo` | `web/src/app/demo/page.tsx` | SIH scripted scene runner | Mixed into the main operator sidebar with equal visual weight, confusing real operations with test fixtures. |

---

## 2. CURRENT COMPONENTS INVENTORY

### HMI Domain Components (`web/src/components/hmi/`)
- `app-shell.tsx`: Global grid layout, `TopBar`, `SideNav`, `StatusBar`. Houses excessive status cells (8 cells in footer, 5 in header).
- `prediction-view.tsx`: `EnvelopeGauge`, `TrustBanner`, `PredictionReadout`, `PredictionDetails`, `CrossCheck`. Exposes mathematical symbols ($d_{\text{env}}$) and internal model names directly.
- `primitives.tsx`: `StateBadge`, `PlanStatus`, `ToneChip`, `ProvenanceTag`, `Panel`, `Kpi`, `Field`, `Loading`, `ErrorBox`, `Notice`. Highly defensive; repeats status chips and warnings.
- `charts.tsx`: `TrendChart`, `ParetoChart`, `HBarChart` (Recharts wrappers).
- `confirm.tsx`: `ConfirmAction` dialog for operator decision acceptance.

### Generic UI Primitives (`web/src/components/ui/`)
- Radix UI wrappers: `alert`, `alert-dialog`, `badge`, `button`, `card`, `input`, `label`, `select`, `separator`, `skeleton`, `slider`, `switch`, `table`, `tabs`, `tooltip`.

---

## 3. UI PROBLEMS & DEVELOPER CLUTTER IDENTIFIED

### 3.1 Exposure of Machine Learning & Internal Engineering Plumbing
- Primary screens prominently display booster identities (`QI-C1-vessel-type`, `QI-C1`, `MODEL-REAL-04`).
- Mathematical distance metrics ($d_{\text{env}} = 0.000$, $\text{MPIW}$, $q_{0.90}$) appear in standard tables without contextual explanation.
- Raw Python docstrings from `optimization/` are dumped verbatim inside `Panel` components on `/optimizer`.
- Raw JSON dumps are rendered in `/audit` details.

### 3.2 Cluttered Navigation & Disrupted Information Hierarchy
- Navigation lists 10 items in arbitrary technical order rather than following the 7-step maritime operations workflow:
  `Fleet Overview → Vessel Performance → Fuel Prediction → Fleet Optimization → Pareto Trade-offs → Scenario Analysis → Voyage Reports`.
- Demo mode is placed directly in the main operator navigation, making the platform look like a prototype demo instead of an operational fleet console.

### 3.3 Defensive and Redundant Warning Pollution
- Defensive notices appear on nearly every page (e.g. repeated notices: *"Constraint violations appear after a Fleet Optimizer run; this screen evaluates prediction trust only"*).
- The Alternative Fuels view has a giant, garish purple-striped banner that screams *"NOT MEASURED TELEMETRY"* across the entire screen width, distracting from the scientific data.
- The footer status bar displays "worst fleet trust", "OOD: none of 3", "Fallback: none", "optimizer warming", creating visual alarm even during 100% nominal operation.

### 3.4 Inconsistent & Technical Terminology
| Current UI Phrasing | Professional Marine Operations Terminology |
| :--- | :--- |
| "Prediction API" / "serving contract" | **Fuel Consumption Prediction** |
| "OOD band" / "convex envelope distance" | **Operating Envelope Status** / **Within Validated Limits** |
| "MODEL-REAL-04 fallback" | **Reference Hydrodynamic Model Used** |
| "Re-evaluated decision vector" | **Operational Dispatch Plan** |
| "Phase4FleetEvaluator docstring" | **Maritime Regulatory & Vessel Constraints** |
| "RNG seed" / "Objective evaluations" | **Optimization Parameters** / **Search Convergence** |
| "Demo Mode" | **Simulation / Demonstration Suite** |

---

## 4. MOCK, STATIC, AND PROVENANCE DATA AUDIT
- **Operational Metrics**: All active numbers (`fuel_prediction`, `predicted_fuel_kg_h`, `cost_usd_per_h`, `wtw_tco2e_per_h`, Pareto solutions) originate from backend endpoints (`/api/*`).
- **Static Fleet Presets**: Vessel identifiers (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`) and itineraries are realistic customer baseline fixtures loaded from `common/fleet_defaults.py`.
- **Finding**: While calculations are 100% real, the UI repeatedly prefixes every label with *"ASSUMED"* or *"NO LIVE FEED"*, undermining the presentation. Instead, clear, professional provenance indicators (e.g. `FLEET PROFILE`, `CALIBRATED MODEL`, `SCENARIO ESTIMATE`) should be used cleanly without alarmism.

---

## 5. ACCESSIBILITY & RESPONSIVE DESIGN GAPS
- **Viewport Layout**: The fixed 2-column grid (`grid-cols-[208px_1fr]`) with sticky elements causes cramping on 1366×768 laptops and 1440×900 displays.
- **Color Semantics**: Red (`--st-ood`) and amber (`--st-warning`) are used in multiple non-critical contexts (e.g., highlighting normal missing factors or test options).
- **Table Density**: Tables lack sticky headers, horizontal scrolling containers for compact viewports, and clean numeric right-alignment.

---

## 6. REDESIGN TARGETS & STRATEGY

1. **Restrained Marine Operations Aesthetic**: Dark charcoal/navy foundation (`#0c1017`, `#131924`), muted cyan data accents (`#38bdf8`), professional maritime blue, amber only for genuine attention, red strictly for critical safety halts.
2. **7-Stage Standard Operator Workflow**:
   - `01 FLEET`: Central control-room fleet status, route cards, active voyages, and operational attention queue.
   - `02 VESSELS`: Deep-dive vessel performance, speed-impact analysis, and voyage economics.
   - `03 PREDICTION`: Operational fuel rate prediction with confidence range, with ML internals hidden behind an expandable **Technical Details** panel.
   - `04 OPTIMIZATION`: Side-by-side **Current Plan vs. Optimized Plan** with modelled changes and feasibility checks.
   - `05 DECISIONS`: Interactive Pareto trade-off frontier with solution comparison.
   - `06 SCENARIOS`: Alternative fuel pathways & cold-ironing shore power comparison without garish disclaimers.
   - `07 REPORTS`: Comprehensive voyage, cost, emissions, and decision audit logs with clean export.
3. **Progressive Disclosure**:
   - Level 1: Operational Status & Attention
   - Level 2: Current Voyage Metrics
   - Level 3: Predictive & Optimization Recommendations
   - Level 4: Technical & Scientific Details (Physics baseline, ML residual, conformal interval, OOD distance, Deb feasibility).
4. **Engineering / Demo Separation**:
   - Move test harnesses, demo scene triggers, and raw diagnostic inspection into an **Engineering / Demo Suite** tab or secondary drawer, keeping the primary operator workspace clean.
