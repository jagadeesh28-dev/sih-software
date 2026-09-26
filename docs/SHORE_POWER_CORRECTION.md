# Shore-Power (Berth) Model Correction — 2026-09-24

## Defect

Both authoritative engines charged shore power (tariff + connection fee) but never counted the fuel burned by onboard generators when shore power was OFF. The fleet evaluator also added no grid emissions. Shore power could therefore only lose: it was strictly dominated in every optimization, and the HMI showed it as increasing GHG.

## Corrected model (`optimization/berth_model.py`, used by both engines)

For hotel load H [kW] and berth time P [h]:

```
E = H · P                                              [kWh]

ON  (shore power):
  C_berth   = E · tariff + connection_fee              (configs/fuels.yaml: 0.18 USD/kWh, 500 USD)
  GHG_berth = E · grid_factor / 10^6                   (configs/fuels.yaml: 450 g CO2e/kWh)
  m_berth   = 0

OFF (onboard generation, selected pathway fuel):
  m_vlsfo_eq = E · SFOC                                (SFOC = 0.220 kg/kWh, VLSFO-equivalent)
  m_berth    = LHV conversion to the pathway           (FleetEmissionsEngine.convert_fuel_mass_for_pathway)
  C_berth    = m_berth · bunker_price + TtW_CO2 · carbon_price     (FleetCostEngine, as for voyage fuel)
  GHG_berth  = WtW(m_berth, pathway)                   (FleetEmissionsEngine, as for voyage fuel)

Totals: COST = voyage_cost + C_berth ; GHG = voyage_GHG + GHG_berth ; FUEL = voyage_fuel + m_berth
```

The two cases are mutually exclusive, and no berth term is counted twice.

**Assumptions** (ASSUMED, shown on the HMI):
- SFOC 0.220 kg/kWh (the constant the evaluator already used for the hotel-load floor), expressed as VLSFO-equivalent.
- Auxiliary engines burn the selected pathway fuel.
- The fleet scenario uses P = 2 h per demand.
- FuelEU is assessed on the sea passage only.

**Where it is applied:**
- `Phase4FleetEvaluator.evaluate_vector` (per assigned leg, per weather scenario; berth terms are scenario-independent);
- `SIHObjectiveEngine.evaluate_voyage` (new result fields: `berth_source`, `berth_energy_kwh`, `berth_fuel_tonnes`, `berth_cost_usd`, `berth_ghg_tonnes`);
- the legacy Phase 3 `FleetEvaluationEngine`, for consistency.

## Before / after

| Case | Before (asymmetric) | After (symmetric) |
|---|---|---|
| Poseidon VLSFO, 2 h, 13,000 kWh — ON | +$2,840, +0 t | +$2,840, +5.85 t |
| Poseidon VLSFO, 2 h — OFF | $0, 0 t, 0 t fuel | +$2,574.74, +10.60 t, 2.860 t fuel |
| Ceto green NH3, 2 h, 1,600 kWh — ON / OFF | +$788, 0 t / nothing | +$788, 0.72 t / +$836.85, 0.217 t, 0.761 t fuel |
| HMI example (Poseidon, 6 h, 1,800 kW, VLSFO): shore − onboard | +$2,444, **+4.86 t** | +$304.98, **−3.949 t** |
| HMI example, green NH3: shore − onboard | +$2,444, +4.86 t | −$3,204.75, **+3.395 t** (onboard NH3 cleaner than the grid) |

## Pareto impact

| | Before | After |
|---|---|---|
| Stored front (`results/pareto_front.csv`) | 6 | **31** |
| Exhaustive valid-region grid (124,416 plans) | 6 | **31**; identical fuel-mix and shore-power patterns to the NSGA-III front |
| Range (cost / WtW) | $170,689 / 727.85 → $437,974 / 610.22 | $173,942.50 / 742.45 → $442,810.01 / 617.92 |

**Membership changes:**
- The old PS-01, PS-02 and PS-03 patterns (LNG on Poseidon, shore power off) stay non-dominated.
- The old PS-04, PS-05 and PS-06 become dominated. They ran bio-methanol vessels on onboard generation, and for bio-methanol shore power is both cheaper and cleaner.
- The additional plans come from genuine shore-power trade-offs: for VLSFO and LNG, shore power costs more but emits less.
- Fuel and cost are no longer perfectly aligned (min fuel = PS-05, min cost = PS-01).

Every stored plan is feasible, penalty-free, in its speed band, uses compatible fuels, is mutually non-dominated, and re-evaluates identically: 31/31 in `reproduce_release`.

## Gates

- **G7** now also requires ON = voyage + electricity only, and OFF = voyage + onboard berth fuel only (`berth_accounting_symmetric`).
- **G8** now also requires the berth GHG counterfactual: OFF adds onboard berth WtW; ON adds exactly the grid emissions.

The asymmetric model would fail both. Pre-correction evidence is in `results/superseded/2026-09-24_pre_shore_power_correction/`.

## Tests

`tests/test_shore_power.py` (8 tests):
- Poseidon VLSFO exclusivity;
- Poseidon bio-methanol economics;
- Ceto NH3 sign;
- the SIH consistency invariant for every vessel and fuel pair;
- the fleet evaluator ON − OFF difference matching the SIH semantics.

`tests/test_api.py::test_fuels_shore_comparison_is_backend_derived_and_signed_by_model` covers the API side.

## Not changed in this correction

MGO remains declared compatible for OSS_Ceto but not encodable by the fuel gene. This is a separate open issue.
