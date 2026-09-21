# UI Forensics & Gap Audit: Egreen Quanta (SIH26138)

**Audit Date**: September 22, 2026  
**Auditor**: Senior Frontend & Maritime HMI Engineer  
**System**: SIH26138 Egreen Quanta Maritime Decision-Support Prototype  
**Scope**: Verification of existing UI components, backend bindings, data integrity, and compliance with the 12-page target information architecture.

---

## 1. Technical Stack Forensics

- **Frontend Framework**: Streamlit (Python 3.14 compatible, headless server mode enabled).
- **Routing**: Session-state driven page router in `dashboard/app.py` responding to sidebar radio menu and programmatic triggers (`st.session_state.current_page`).
- **Component Architecture**:
  - `dashboard/components/top_bar.py`: Persistent global header (`Egreen Quanta | mode | fleet | model | scenario | time`).
  - `dashboard/components/status_strip.py`: Persistent global footer (`freshness | model routing | OOD distance | last recommendation`).
  - `dashboard/components/vessel_card.py`: Reusable standardized vessel telemetry & prediction card.
  - `dashboard/backend_bridge.py`: Cached singleton providers for `ProductionFuelPredictor` and `SIHObjectiveEngine`, audit logger, and verified dataset loaders.
- **State Management**: `st.session_state` managing `system_mode`, `active_scenario_name`, `active_model_id`, `audit_ledger`, `last_recommendation_status`, `opt_result`, and `current_page`.
- **Backend APIs / Internal Clients**: In-process direct bindings to `src.qi_prediction.serving.ProductionFuelPredictor` and `optimization.sih_objective_engine.SIHObjectiveEngine`. Zero invented network REST endpoints.
- **Styling System**: Custom injected CSS implementing a professional maritime dark engineering palette (`#080d1a`, `#0d1527`, `#00E5FF`, `#38bdf8`, `#10b981`, `#f59e0b`, `#ef4444`). High contrast, desktop-first, 16:9 projector friendly.
- **Chart Library**: Streamlit native Vega-Lite bindings (`st.line_chart`, `st.scatter_chart`, `st.bar_chart`, `st.map`).
- **Authentication**: N/A (Standard maritime bridge / fleet operating center terminal console design; session-based role: `Superintendent_HMI`).
- **Error Handling**: Input validation gate via `ProductionFuelPredictor.validate_and_sanitize_point()`, returning safe default fail-safes and UI error alerts.

---

## 2. Comprehensive Requirements Audit Table

| Requirement | Existing UI | Backend connected | Mock data | Missing | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Fleet Command Center** | `dashboard/pages/fleet_overview.py` | YES (`ProductionFuelPredictor`, `SIHObjectiveEngine`) | None (Real baseline telemetry from FuelCast) | Expand global KPIs & alerts per Section 4 | P0 |
| **2. Vessel Intelligence** | `dashboard/pages/vessel_detail.py` | YES (`ProductionFuelPredictor`, 3 vessel specs) | None | Add SOG/STW distinction, exact engine load P_B | P0 |
| **3. Prediction & Trust** | `dashboard/pages/prediction_trust.py` | YES (`QI-C1`, `M04`, `DomainChecker`, `conformal_quantiles.json`) | None | Add explicit DATA STATUS (VALID/MISSING/STALE) badge | P0 |
| **4. Scenario Lab** | `dashboard/pages/scenario_lab.py` | YES (`evaluate_voyage`, `ProductionFuelPredictor`) | None | Display MODEL VERSION, ASSUMPTIONS, and explicit DATA SOURCE | P1 |
| **5. Operational Cost** | Combined in Scenario/Optimizer | PARTIAL (`FleetCostEngine` through `SIHObjectiveEngine`) | None | **Dedicated Page** displaying $C_{\text{fuel}}, C_{\text{elec}}, C_{\text{OPS}}, C_{\text{carbon}}, C_{\text{sched}}, C_{\text{FuelEU}}$ | P0 |
| **6. Lifecycle GHG** | Combined in Alt Fuels | PARTIAL (`FleetEmissionsEngine` through `SIHObjectiveEngine`) | None | **Dedicated Page** displaying $\text{WtW} = \text{WtT} + \text{TtW} + \text{Slip}$ in $\text{tCO}_2\text{e}$ | P0 |
| **7. Alternative Fuels** | `dashboard/pages/alternative_fuels.py` | YES (`FuelPathwayRegistry`, invariant shaft work) | None | Add explicit energy MJ/h comparison | P1 |
| **8. Fleet Optimizer** | `dashboard/pages/fleet_optimizer.py` | YES (Frozen benchmark & `SIHObjectiveEngine`) | None | Expose live DE/QPSO benchmark runs + decision variables | P1 |
| **9. Pareto / Trade-offs** | `dashboard/pages/pareto_tradeoffs.py` | YES (`results/pareto_front.csv`, 13 points) | None | Non-biased labels (Lowest Cost, Lowest GHG, Lowest Fuel, Balanced) | P1 |
| **10. Alerts & Safety** | `dashboard/pages/alerts_safety.py` | YES (`DomainChecker`, 1,000 stress test logs) | None | Add explicit timestamp & operator resolution action | P2 |
| **11. Audit / Reports** | `dashboard/pages/audit_reports.py` | YES (Session ledger, CSV/JSON export) | None | Connect all optimizer and scenario acceptance triggers | P2 |
| **12. Demo Center** | `dashboard/pages/demo_mode.py` | YES (11 verified scenes from `demo_scenarios.py`) | None | Rename/polish as official Demo Center with timer & jury cards | P2 |

---

## 3. Key Findings & Actions Needed

1. **Dedicated Cost & GHG Pages**: Currently, cost and GHG calculations were grouped under Scenario Lab and Alternative Fuels. The user's Master Architecture specifically demands **12 separate, focused screens**, elevating `Operational Cost` (Phase 9) and `Lifecycle GHG` (Phase 10) into first-class pages.
2. **Scientific Neutrality**: Re-verify that vessel-type is presented as contextual/model architectural conditioning without claiming aggregate accuracy improvements, adhering strictly to the empirical evidence (QI-C1: $247.38\text{ kg/h}$ vs QI-C1-vessel-type: $252.62\text{ kg/h}$).
3. **Data Freshness & Status**: Add explicit `DATA STATUS: VALID / MISSING / STALE` and `FALLBACK: NORMAL / ACTIVE` indicators across prediction displays.
4. **Pareto Neutrality**: Ensure no solution is globally labeled "BEST"; use objective-specific qualifiers (*Lowest Cost*, *Lowest GHG*, *Lowest Fuel*, *Balanced Compromise*).
