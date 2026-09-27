"use client";

import { CheckCircle2, ChevronRight, Compass, Droplets, Fuel, Info, Layers, Leaf, Plug, ShieldCheck, Zap } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { HBarChart } from "@/components/hmi/charts";
import {
  ConfidenceBand,
  DataState,
  Field,
  Kpi,
  PageHeader,
  Panel,
  ProvenanceTag,
  StateBadge,
  TechnicalDetails,
  ToneChip,
} from "@/components/hmi/primitives";
import { PredictionReadout } from "@/components/hmi/prediction-view";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

export default function FuelsPage() {
  const { activeVessel, setActiveVessel, status } = useHmi();
  const vessels = status.data?.fleet_trust.map((t) => t.vessel_id) ?? [activeVessel];
  const [draft, setDraft] = useState({ speed: "14.5", distance: "250", port: "6" });
  const [q, setQ] = useState({ speed: 14.5, distance: 250, port: 6 });
  const fuels = useApi(
    () => api.fuels({ vessel_id: activeVessel, speed_kn: q.speed, distance_nm: q.distance, port_hours: q.port }),
    [activeVessel, q]
  );

  return (
    <>
      <PageHeader
        title="Alternative Fuel Pathways & Energy Analysis"
        badge={<ToneChip tone="info">Decarbonization Decision Support</ToneChip>}
        description="Comprehensive evaluation of alternative marine fuel pathways and cold-ironing shore power on an equal-energy shaft work basis. Emissions follow well-to-wake (WtW) lifecycle accounting per IMO MEPC and EU FuelEU Maritime regulations."
      />

      {/* Dignified Operational Notice */}
      <div className="mb-4 rounded-md border border-cyan-800/60 bg-cyan-950/20 px-4 py-3 flex items-start gap-3">
        <Fuel className="size-5 text-cyan-400 mt-0.5 shrink-0" />
        <div className="text-xs text-cyan-200/90 leading-relaxed">
          <span className="font-semibold text-cyan-300">SCENARIO ESTIMATE · MODELLED LIFECYCLE EVALUATION: </span>
          Alternative fuel pathways are evaluated on an invariant shaft-energy basis (
          <span className="font-mono text-cyan-100">E_shaft = m · LHV · η</span>) from the model-predicted VLSFO baseline. In-service operational telemetry represents conventional bunker fuel; green fuel pathways (Methanol, LNG, Ammonia, Hydrogen) reflect validated engineering lifecycle estimates.
        </div>
      </div>

      {/* Operating Point Formulation */}
      <Panel title="Operating Point & Voyage Parameters" className="mb-4">
        <form
          className="flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            setQ({
              speed: Number(draft.speed),
              distance: Number(draft.distance),
              port: Number(draft.port),
            });
          }}
        >
          <div className="grid gap-1">
            <Label htmlFor="fv" className="text-xs font-medium">Target Vessel</Label>
            <select
              id="fv"
              value={activeVessel}
              onChange={(e) => setActiveVessel(e.target.value)}
              className="h-8 rounded-md border border-input/60 bg-input/20 px-2 text-xs font-medium focus:border-cyan-500 focus:outline-none"
            >
              {vessels.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>

          {([
            ["speed", `Speed (${UNITS.speed})`],
            ["distance", `Distance (${UNITS.distance})`],
            ["port", `Berth Duration (${UNITS.hours})`],
          ] as const).map(([k, l]) => (
            <div key={k} className="grid gap-1">
              <Label htmlFor={`f-${k}`} className="text-xs font-medium">{l}</Label>
              <Input
                id={`f-${k}`}
                inputMode="decimal"
                className="num h-8 w-28 text-xs font-mono"
                value={draft[k]}
                onChange={(e) => {
                  const val = e.target.value;
                  setDraft((cur) => ({ ...cur, [k]: val }));
                }}
              />
            </div>
          ))}

          <Button type="submit" className="h-8 text-xs font-semibold">
            Evaluate Pathways
          </Button>
        </form>
      </Panel>

      <DataState state={fuels}>
        {(f) => {
          // Identify VLSFO baseline row for comparative reduction calculations
          const vlsfoRow = f.rows.find((r) => r.key === "vlsfo");
          const vlsfoGhg = vlsfoRow?.result.ghg.wtw_tco2e ?? 1.0;

          return (
            <div className="grid gap-4">
              {/* Top Row: VLSFO Baseline Card + Lifecycle WtW GHG Chart */}
              <div className="grid gap-4 lg:grid-cols-[340px_minmax(0,1fr)]">
                {/* VLSFO Reference Point */}
                <Panel
                  title="Hydrodynamic Baseline (VLSFO)"
                  subtitle="Modelled resistance reference point"
                  actions={<StateBadge state={f.prediction.trust.state} />}
                >
                  <div className="rounded-md bg-panel-2/60 p-3 border border-panel-border/60 mb-3">
                    <div className="text-[11px] uppercase tracking-wider text-muted-foreground font-medium">Baseline Fuel Rate</div>
                    <div className="text-2xl font-bold font-mono text-cyan-300">
                      {fmt(f.prediction.result.fuel_prediction, 1)}{" "}
                      <span className="text-xs font-normal text-muted-foreground">{UNITS.fuelRate}</span>
                    </div>
                    <div className="text-xs text-muted-foreground font-mono mt-0.5">
                      ~ {fmt(((f.prediction.result.fuel_prediction ?? 0) * 24) / 1000, 2)} t/day at {fmt(f.speed_kn, 1)} kn
                    </div>
                  </div>

                  <ConfidenceBand
                    lower={f.prediction.result.uncertainty?.lower_bound_kg_h}
                    upper={f.prediction.result.uncertainty?.upper_bound_kg_h}
                    value={f.prediction.result.fuel_prediction}
                    confidence={f.prediction.result.uncertainty?.coverage}
                  />

                  {f.prediction.trust.fallback && (
                    <ToneChip tone="fallback" className="mt-3">
                      {f.prediction.trust.fallback_label}
                    </ToneChip>
                  )}
                  {f.rows.length === 0 && (
                    <p className="mt-2 text-xs text-amber-400">
                      No pathway comparison available: predictor produced no valid VLSFO rate.
                    </p>
                  )}
                </Panel>

                {/* Lifecycle GHG Comparison Chart */}
                {f.rows.length > 0 && (
                  <Panel
                    title="Lifecycle Well-to-Wake (WtW) GHG by Pathway"
                    subtitle={`Total voyage footprint (${UNITS.ghg}) · Lower is better`}
                  >
                    <HBarChart
                      label="Well-to-wake GHG by fuel pathway"
                      unit={UNITS.ghg}
                      digits={2}
                      rows={f.rows.map((r) => ({
                        name: r.label,
                        value: r.result.ghg.wtw_tco2e,
                        scenario: r.basis === "SCENARIO ESTIMATE",
                      }))}
                    />
                    <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground border-t pt-2">
                      <span>Shaft energy demand: {fmt(f.rows[0]?.result.energy_mj_h ?? 0, 0)} MJ/h</span>
                      <span>Transit distance: {fmt(f.distance_nm, 0)} nm</span>
                      <span>Berth duration: {fmt(f.port_hours, 0)} h</span>
                    </div>
                  </Panel>
                )}
              </div>

              {/* Main Comparison Table */}
              {f.rows.length > 0 && (
                <Panel
                  title="Fuel Pathway Performance & Decarbonization Comparison"
                  subtitle={`${f.vessel_id} · ${fmt(f.speed_kn, 1)} kn STW · ${fmt(f.distance_nm, 0)} nm transit · ${fmt(f.port_hours, 0)} h berth`}
                >
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Fuel Pathway</TableHead>
                        <TableHead>Evaluation Basis</TableHead>
                        <TableHead className="text-right">Burn Rate ({UNITS.fuelRate})</TableHead>
                        <TableHead className="text-right">Fuel Mass ({UNITS.mass})</TableHead>
                        <TableHead className="text-right">Total OPEX ({UNITS.currency})</TableHead>
                        <TableHead className="text-right">Lifecycle WtW ({UNITS.ghg})</TableHead>
                        <TableHead className="text-right">Δ GHG vs VLSFO</TableHead>
                        <TableHead className="text-right">LHV (MJ/kg)</TableHead>
                        <TableHead className="text-right">Price ({UNITS.currency}/t)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {f.rows.map((r) => {
                        const isScenario = r.basis === "SCENARIO ESTIMATE";
                        const deltaGhgPct = ((r.result.ghg.wtw_tco2e - vlsfoGhg) / vlsfoGhg) * 100;
                        const isVlsfo = r.key === "vlsfo";

                        return (
                          <TableRow
                            key={r.key}
                            className={cn(
                              "transition-colors",
                              isVlsfo ? "bg-cyan-950/20 font-medium" : isScenario ? "hover:bg-accent/40" : ""
                            )}
                          >
                            <TableCell className="font-semibold text-foreground">
                              {r.label}
                            </TableCell>
                            <TableCell>
                              {isScenario ? (
                                <ToneChip tone="demo">SCENARIO ESTIMATE</ToneChip>
                              ) : (
                                <ToneChip tone="normal">BASELINE MODEL</ToneChip>
                              )}
                            </TableCell>
                            <TableCell className="num text-right font-mono">
                              {fmt(r.result.fuel_rate_kg_h, 0)}
                            </TableCell>
                            <TableCell className="num text-right font-mono">
                              {fmt(r.result.fuel_t, 2)}
                            </TableCell>
                            <TableCell className="num text-right font-mono text-cyan-200">
                              {fmtUsd(r.result.cost.total_usd)}
                            </TableCell>
                            <TableCell className="num text-right font-mono font-semibold text-emerald-300">
                              {fmt(r.result.ghg.wtw_tco2e, 2)}
                            </TableCell>
                            <TableCell className="num text-right font-mono">
                              {isVlsfo ? (
                                <span className="text-muted-foreground text-xs">Baseline (0%)</span>
                              ) : (
                                <span
                                  className={cn(
                                    "font-semibold",
                                    deltaGhgPct <= 0 ? "text-emerald-400" : "text-amber-400"
                                  )}
                                >
                                  {deltaGhgPct <= 0 ? "" : "+"}{fmt(deltaGhgPct, 1)}%
                                </span>
                              )}
                            </TableCell>
                            <TableCell className="num text-right font-mono text-muted-foreground">
                              {fmt(r.assumptions.lhv_mj_kg, 1)}
                            </TableCell>
                            <TableCell className="num text-right font-mono text-muted-foreground">
                              {fmtUsd(r.assumptions.price_usd_per_tonne)}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                  <p className="mt-2 text-[11px] text-muted-foreground">
                    Mass rates and voyage fuel quantities vary inversely with fuel Lower Heating Value (LHV) to satisfy identical shaft work requirements. Total OPEX includes bunker costs, carbon EU ETS allowances, and port electricity charges.
                  </p>
                </Panel>
              )}

              {/* Shore Power (Cold Ironing) at Berth Table */}
              {f.shore_comparison.length > 0 && (
                <Panel
                  title="Cold Ironing (Shore Power) vs. Onboard Generator at Berth"
                  subtitle={`${fmt(f.port_hours, 0)} h berth duration · Hotel load demand: ${fmt(f.config.hotel_load_kw, 0)} kW · Auxiliary generator SFOC: ${fmt(f.config.berth_sfoc_kg_per_kwh, 3)} kg/kWh`}
                >
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Fuel Pathway</TableHead>
                        <TableHead className="text-right">Onboard Fuel ({UNITS.mass})</TableHead>
                        <TableHead className="text-right">Onboard Berth GHG ({UNITS.ghg})</TableHead>
                        <TableHead className="text-right">Shore Power Grid GHG ({UNITS.ghg})</TableHead>
                        <TableHead className="text-right">Δ OPEX (Shore − Onboard)</TableHead>
                        <TableHead className="text-right">Δ GHG (Shore − Onboard)</TableHead>
                        <TableHead className="text-center">Operational Recommendation</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {f.shore_comparison.map((c) => (
                        <TableRow key={c.fuel}>
                          <TableCell className="font-semibold text-foreground">{c.label}</TableCell>
                          <TableCell className="num text-right font-mono">{fmt(c.onboard_berth.fuel_t, 3)}</TableCell>
                          <TableCell className="num text-right font-mono">{fmt(c.onboard_berth.ghg_tco2e, 2)}</TableCell>
                          <TableCell className="num text-right font-mono text-cyan-300">{fmt(c.shore_berth.ghg_tco2e, 2)}</TableCell>
                          <TableCell className="num text-right font-mono">
                            <span className={c.delta_cost_usd <= 0 ? "text-emerald-400" : "text-amber-400"}>
                              {c.delta_cost_usd <= 0 ? "" : "+"}{fmtUsd(c.delta_cost_usd)}
                            </span>
                          </TableCell>
                          <TableCell className="num text-right font-mono">
                            <span className={c.delta_wtw_tco2e <= 0 ? "text-emerald-400" : "text-amber-400"}>
                              {c.delta_wtw_tco2e <= 0 ? "" : "+"}{fmt(c.delta_wtw_tco2e, 2)} tCO2e
                            </span>
                          </TableCell>
                          <TableCell className="text-center text-xs">
                            <ToneChip tone={c.ghg_effect === "INCREASES GHG" ? "warning" : "normal"}>
                              {c.ghg_effect === "INCREASES GHG" ? "Onboard Cleaner" : "Shore Power Preferred"}
                            </ToneChip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <p className="mt-2 text-[11px] text-muted-foreground">
                    Shore power emissions depend on local regional electricity grid carbon intensity ({fmt(f.config.shore_power_grid_factor_g_co2e_per_kwh, 0)} gCO2e/kWh). Onboard auxiliary generator emissions burn the selected bunker pathway.
                  </p>
                </Panel>
              )}

              {/* Technical Details Progressive Disclosure */}
              <TechnicalDetails title="Regulatory Parameters, Emission Factors & Standards">
                <div className="grid gap-4 lg:grid-cols-2 text-xs">
                  <div>
                    <div className="font-semibold text-foreground mb-1">Global Economic & Port Assumptions</div>
                    <dl className="grid gap-1">
                      <Field label="EU ETS Carbon Allowance" value={fmtUsd(f.config.carbon_price_usd_per_tco2)} unit="/tCO2" />
                      <Field label="Shore Power Tariff" value={fmt(f.config.shore_power_tariff_usd_per_kwh, 2)} unit="USD/kWh" />
                      <Field label="Regional Grid Emission Factor" value={fmt(f.config.shore_power_grid_factor_g_co2e_per_kwh, 0)} unit="gCO2e/kWh" />
                      <Field label="Auxiliary Engine SFOC" value={fmt(f.config.berth_sfoc_kg_per_kwh, 3)} unit="kg/kWh" />
                      <Field label="Vessel Hotel Load (Berth)" value={fmt(f.config.hotel_load_kw, 0)} unit="kW" />
                      <Field label="Configuration Reference" value={f.config.fuels_config} />
                    </dl>
                  </div>

                  <div>
                    <div className="font-semibold text-foreground mb-1">Pathway Factor Sources (IMO / EU RED II)</div>
                    <dl className="grid gap-1">
                      {f.rows.filter((r) => !r.shore_power).map((r) => (
                        <Field
                          key={r.key}
                          label={r.assumptions.name}
                          value={
                            <span className="text-muted-foreground">
                              {r.assumptions.source ?? "IMO MEPC / RED II"} ({r.assumptions.confidence ?? "Validated"})
                            </span>
                          }
                        />
                      ))}
                    </dl>
                  </div>
                </div>
              </TechnicalDetails>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
