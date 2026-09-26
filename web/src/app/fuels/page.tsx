"use client";

import { FlaskConical } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { HBarChart } from "@/components/hmi/charts";
import { DataState, Field, PageHeader, Panel, ProvenanceTag, StateBadge, ToneChip } from "@/components/hmi/primitives";
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
  const fuels = useApi(() => api.fuels({ vessel_id: activeVessel, speed_kn: q.speed, distance_nm: q.distance, port_hours: q.port }), [activeVessel, q]);

  return (
    <>
      <PageHeader title="Alternative Fuels" description="Configured fuel pathways evaluated on an equal-energy basis from the model-predicted VLSFO rate at the chosen speed. Factors and prices come from configs/fuels.yaml." />
      <div role="alert" className="mb-3 flex items-center gap-3 rounded-md border-2 border-st-demo bg-[repeating-linear-gradient(45deg,transparent_0_8px,oklch(0.72_0.15_300/0.12)_8px_16px)] px-4 py-3">
        <FlaskConical className="size-6 text-st-demo" aria-hidden />
        <div>
          <div className="text-base font-bold tracking-wide text-st-demo">SCENARIO ESTIMATE — NOT MEASURED GREEN-FUEL TELEMETRY</div>
          <div className="text-xs text-muted-foreground">No vessel in the dataset burned these fuels. Rows marked SCENARIO ESTIMATE are energy-equivalent conversions, not observations.</div>
        </div>
      </div>
      <Panel title="Operating point" className="mb-3">
        <form className="flex flex-wrap items-end gap-3" onSubmit={(e) => { e.preventDefault(); setQ({ speed: Number(draft.speed), distance: Number(draft.distance), port: Number(draft.port) }); }}>
          <div className="grid gap-1">
            <Label htmlFor="fv" className="text-xs">Vessel</Label>
            <select id="fv" value={activeVessel} onChange={(e) => setActiveVessel(e.target.value)} className="h-8 rounded-md border bg-input/30 px-2 text-sm">
              {vessels.map((v) => <option key={v}>{v}</option>)}
            </select>
          </div>
          {([["speed", `Speed (${UNITS.speed})`], ["distance", `Distance (${UNITS.distance})`], ["port", `Berth (${UNITS.hours})`]] as const).map(([k, l]) => (
            <div key={k} className="grid gap-1">
              <Label htmlFor={`f-${k}`} className="text-xs">{l}</Label>
              <Input id={`f-${k}`} inputMode="decimal" className="num h-8 w-28" value={draft[k]} onChange={(e) => { const v = e.target.value; setDraft((cur) => ({ ...cur, [k]: v })); }} />
            </div>
          ))}
          <Button type="submit">Evaluate</Button>
        </form>
      </Panel>
      <DataState state={fuels}>
        {(f) => (
          <div className="grid gap-3">
            <div className="grid gap-3 lg:grid-cols-[320px_minmax(0,1fr)]">
              <Panel title="VLSFO basis" subtitle={<>Production predictor <ProvenanceTag kind="MODEL" /></>} actions={<StateBadge state={f.prediction.trust.state} />}>
                <PredictionReadout prediction={f.prediction} />
                {f.prediction.trust.fallback && <ToneChip tone="fallback" className="mt-2">{f.prediction.trust.fallback_label}</ToneChip>}
                {f.rows.length === 0 && <p className="mt-2 text-sm text-st-ood">No fuel comparison: the predictor produced no VLSFO rate.</p>}
              </Panel>
              {f.rows.length > 0 && (
                <Panel title="Lifecycle WtW GHG per voyage" subtitle={`${UNITS.ghg} · hatched bars are scenario estimates`}>
                  <HBarChart label="Well-to-wake GHG by fuel pathway" unit={UNITS.ghg} digits={2}
                    rows={f.rows.map((r) => ({ name: r.label, value: r.result.ghg.wtw_tco2e, scenario: r.basis === "SCENARIO ESTIMATE" }))} />
                </Panel>
              )}
            </div>
            {f.rows.length > 0 && (
              <Panel title="Fuel pathway comparison" subtitle={`${f.vessel_id} · ${fmt(f.speed_kn, 1)} ${UNITS.speed} · ${fmt(f.distance_nm, 0)} ${UNITS.distance} · berth ${fmt(f.port_hours, 0)} ${UNITS.hours}`}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Pathway</TableHead><TableHead>Basis</TableHead>
                      <TableHead className="text-right">Rate ({UNITS.fuelRate})</TableHead>
                      <TableHead className="text-right">Energy ({UNITS.energy})</TableHead>
                      <TableHead className="text-right">Fuel ({UNITS.mass})</TableHead>
                      <TableHead className="text-right">Cost ({UNITS.currency})</TableHead>
                      <TableHead className="text-right">WtW ({UNITS.ghg})</TableHead>
                      <TableHead>Berth supply</TableHead>
                      <TableHead className="text-right">TtW</TableHead><TableHead className="text-right">WtT</TableHead>
                      <TableHead className="text-right">LHV MJ/kg</TableHead><TableHead className="text-right">Price USD/t</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {f.rows.map((r) => {
                      const scen = r.basis === "SCENARIO ESTIMATE";
                      return (
                        <TableRow key={r.key} className={cn(scen && "bg-st-demo/5")}>
                          <TableCell className="font-medium">{r.label}</TableCell>
                          <TableCell>{scen ? <ToneChip tone="demo">SCENARIO ESTIMATE</ToneChip> : <ToneChip tone="info">MODEL PREDICTION</ToneChip>}</TableCell>
                          <TableCell className="num text-right">{fmt(r.result.fuel_rate_kg_h, 0)}</TableCell>
                          <TableCell className="num text-right">{fmt(r.result.energy_mj_h, 0)}</TableCell>
                          <TableCell className="num text-right">{fmt(r.result.fuel_t, 2)}</TableCell>
                          <TableCell className="num text-right">{fmtUsd(r.result.cost.total_usd)}</TableCell>
                          <TableCell className="num text-right font-semibold">{fmt(r.result.ghg.wtw_tco2e, 2)}</TableCell>
                          <TableCell className="text-xs">{humanize(r.result.berth.source)} · {fmt(r.result.berth.ghg_tco2e, 2)} {UNITS.ghg}</TableCell>
                          <TableCell className="num text-right">{fmt(r.result.ghg.ttw_tco2e, 2)}</TableCell>
                          <TableCell className="num text-right">{fmt(r.result.ghg.wtt_tco2e, 2)}</TableCell>
                          <TableCell className="num text-right">{fmt(r.assumptions.lhv_mj_kg, 1)}</TableCell>
                          <TableCell className="num text-right">{fmt(r.assumptions.price_usd_per_tonne, 0)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
                <p className="mt-2 text-xs text-muted-foreground">Rate and energy are the sea passage only; they are identical across pathways by construction (the engine holds shaft energy constant and converts fuel mass by LHV). Fuel, cost and WtW include the berth phase.</p>
              </Panel>
            )}
            {f.shore_comparison.length > 0 && (
              <Panel title="Shore power at berth vs onboard generation"
                subtitle={<><ProvenanceTag kind="ESTIMATE" /> {fmt(f.port_hours, 0)} {UNITS.hours} berth · hotel load {fmt(f.config.hotel_load_kw, 0)} kW · onboard SFOC {fmt(f.config.berth_sfoc_kg_per_kwh, 3)} kg/kWh <ProvenanceTag kind="ASSUMED" /></>}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Pathway</TableHead>
                      <TableHead className="text-right">Onboard berth fuel ({UNITS.mass})</TableHead>
                      <TableHead className="text-right">Onboard berth WtW</TableHead>
                      <TableHead className="text-right">Shore grid WtW</TableHead>
                      <TableHead className="text-right">Δ cost (shore − onboard)</TableHead>
                      <TableHead className="text-right">Δ WtW (shore − onboard)</TableHead>
                      <TableHead>Model result</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {f.shore_comparison.map((c) => (
                      <TableRow key={c.fuel}>
                        <TableCell className="font-medium">{c.label}</TableCell>
                        <TableCell className="num text-right">{fmt(c.onboard_berth.fuel_t, 3)}</TableCell>
                        <TableCell className="num text-right">{fmt(c.onboard_berth.ghg_tco2e, 2)}</TableCell>
                        <TableCell className="num text-right">{fmt(c.shore_berth.ghg_tco2e, 2)}</TableCell>
                        <TableCell className="num text-right">{fmtUsd(c.delta_cost_usd)}</TableCell>
                        <TableCell className="num text-right">{fmt(c.delta_wtw_tco2e, 2)}</TableCell>
                        <TableCell className="text-xs">
                          <ToneChip tone={c.ghg_effect === "INCREASES GHG" ? "warning" : "normal"}>{c.ghg_effect}</ToneChip>{" "}
                          <span className="text-muted-foreground">{humanize(c.cost_effect)}</span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <p className="mt-2 text-xs text-muted-foreground">Mutually exclusive berth cases: shore power pays the tariff, connection fee and grid emissions; onboard generation burns the selected pathway fuel (costed and emitted like voyage fuel). Signs are model output, not a fixed expectation.</p>
              </Panel>
            )}
            <div className="grid gap-3 lg:grid-cols-2">
              <Panel title="Configuration source" subtitle={<>{f.config.fuels_config} · sha256 {f.config.fuels_config_sha256.slice(0, 16)}…</>}>
                <dl>
                  <Field label="Carbon price" value={fmtUsd(f.config.carbon_price_usd_per_tco2)} unit="/tCO2" />
                  <Field label="Shore-power tariff" value={fmt(f.config.shore_power_tariff_usd_per_kwh, 2)} unit="USD/kWh" />
                  <Field label="Grid emission factor" value={fmt(f.config.shore_power_grid_factor_g_co2e_per_kwh, 0)} unit="gCO2e/kWh" />
                  <Field label="Onboard generator SFOC" value={fmt(f.config.berth_sfoc_kg_per_kwh, 3)} unit="kg/kWh (VLSFO-eq)" tag={<ProvenanceTag kind="ASSUMED" />} />
                  <Field label="Hotel load at berth" value={fmt(f.config.hotel_load_kw, 0)} unit="kW" tag={<ProvenanceTag kind="ASSUMED" />} />
                </dl>
              </Panel>
              <Panel title="Factor sources per pathway">
                <dl>
                  {f.rows.filter((r) => !r.shore_power).map((r) => (
                    <Field key={r.key} label={r.assumptions.name} value={<span className="text-xs">{r.assumptions.source ?? "—"} ({r.assumptions.confidence ?? "n/a"})</span>} />
                  ))}
                </dl>
              </Panel>
            </div>
          </div>
        )}
      </DataState>
    </>
  );
}
