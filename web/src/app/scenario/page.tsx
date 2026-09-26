"use client";

import { FlaskConical } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { PredictionReadout } from "@/components/hmi/prediction-view";
import {
  ErrorBox, Field, Kpi, Loading, Notice, PageHeader, Panel, ProvenanceTag, StateBadge, ToneChip, provenanceKind,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { api, type Scenario } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";

const OVERRIDES = [
  { key: "stw_kn", label: "Speed (STW)", unit: UNITS.speed },
  { key: "draft_m", label: "Draft", unit: UNITS.length },
  { key: "displacement_t", label: "Displacement / loading", unit: UNITS.displacement },
  { key: "wind_speed_ms", label: "Wind speed", unit: UNITS.windSpeed },
  { key: "wave_height_m", label: "Wave height (Hs)", unit: UNITS.length },
  { key: "water_depth_m", label: "Water depth", unit: UNITS.length },
];

export default function ScenarioPage() {
  const { activeVessel, setActiveVessel, setScenarioId, status } = useHmi();
  const vessels = status.data?.fleet_trust.map((t) => t.vessel_id) ?? [activeVessel];
  const fuelOptions = useApi(() => api.fuels({ vessel_id: "CPS_Poseidon", speed_kn: 14.5, distance_nm: 100, port_hours: 0 }), []);
  const [base, setBase] = useState<"fleet_default" | "dataset_latest">("fleet_default");
  const [ov, setOv] = useState<Record<string, string>>({});
  const [fuel, setFuel] = useState("vlsfo");
  const [shore, setShore] = useState(false);
  const [portH, setPortH] = useState("6");
  const [dist, setDist] = useState("300");
  const [deadline, setDeadline] = useState("24");
  const [res, setRes] = useState<Scenario>();
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true); setError(undefined);
    const overrides = Object.fromEntries(Object.entries(ov).filter(([, v]) => v !== "").map(([k, v]) => [k, Number(v)]));
    try {
      const r = await api.scenario({
        vessel_id: activeVessel, base, overrides, fuel_type: fuel, use_shore_power: shore,
        port_hours: Number(portH), distance_nm: Number(dist), deadline_h: Number(deadline),
      });
      setRes(r); setScenarioId(r.scenario_id);
    } catch (e) { setError((e as Error).message); setRes(undefined); }
    finally { setBusy(false); }
  };

  const fuels = Array.from(new Map((fuelOptions.data?.rows ?? []).filter((r) => !r.shore_power).map((r) => [r.fuel, r.assumptions.name])));
  const v = res?.voyage;

  return (
    <>
      <PageHeader title="Scenario Lab" badge={<ToneChip tone="info">What-if workspace</ToneChip>}
        description="Change operating and voyage parameters, then evaluate fuel, cost, lifecycle GHG and schedule through the production predictor and SIH objective engine. Outputs are SCENARIO ESTIMATES, never measured telemetry." />
      <div className="grid gap-3 xl:grid-cols-[400px_minmax(0,1fr)]">
        <Panel title="Scenario inputs">
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); run(); }}>
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1">
                <Label htmlFor="vessel" className="text-xs">Vessel</Label>
                <select id="vessel" value={activeVessel} onChange={(e) => setActiveVessel(e.target.value)} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                  {vessels.map((id) => <option key={id}>{id}</option>)}
                </select>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="base" className="text-xs">Baseline state</Label>
                <select id="base" value={base} onChange={(e) => setBase(e.target.value as typeof base)} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                  <option value="fleet_default">Fleet default (ASSUMED)</option>
                  <option value="dataset_latest">Latest recorded (MEASURED)</option>
                </select>
              </div>
            </div>
            <fieldset className="grid grid-cols-2 gap-2 rounded-md border p-2">
              <legend className="px-1 text-[11px] uppercase tracking-wider text-muted-foreground">Overrides — blank keeps baseline</legend>
              {OVERRIDES.map((o) => (
                <div key={o.key} className="grid gap-1">
                  <Label htmlFor={o.key} className="text-xs">{o.label} ({o.unit})</Label>
                  <Input id={o.key} inputMode="decimal" className="num h-8" placeholder="baseline" value={ov[o.key] ?? ""}
                    onChange={(e) => { const v = e.target.value; setOv((cur) => ({ ...cur, [o.key]: v })); }} />
                </div>
              ))}
            </fieldset>
            <fieldset className="grid grid-cols-2 gap-2 rounded-md border p-2">
              <legend className="px-1 text-[11px] uppercase tracking-wider text-muted-foreground">Voyage — SCENARIO INPUT</legend>
              <div className="col-span-2 grid gap-1">
                <Label htmlFor="fuel" className="text-xs">Fuel pathway (configs/fuels.yaml)</Label>
                <select id="fuel" value={fuel} onChange={(e) => setFuel(e.target.value)} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                  {fuels.length ? fuels.map(([k, name]) => <option key={k} value={k}>{name}</option>) : <option value="vlsfo">vlsfo</option>}
                </select>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="dist" className="text-xs">Route distance ({UNITS.distance})</Label>
                <Input id="dist" inputMode="decimal" className="num h-8" value={dist} onChange={(e) => setDist(e.target.value)} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="deadline" className="text-xs">Schedule deadline ({UNITS.hours})</Label>
                <Input id="deadline" inputMode="decimal" className="num h-8" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
              </div>
              <div className="flex items-center gap-2">
                <Switch id="shore" checked={shore} onCheckedChange={setShore} />
                <Label htmlFor="shore" className="text-xs">Shore power at berth</Label>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="port" className="text-xs">Berth duration ({UNITS.hours})</Label>
                <Input id="port" inputMode="decimal" className="num h-8" value={portH} onChange={(e) => setPortH(e.target.value)} />
              </div>
              <div className="col-span-2 grid gap-1 opacity-60">
                <Label htmlFor="cargo" className="text-xs">Cargo (t)</Label>
                <Input id="cargo" disabled placeholder="Not supported by the voyage engine — see Fleet Optimizer" className="h-8" />
              </div>
            </fieldset>
            <Button type="submit" disabled={busy}><FlaskConical className="size-4" aria-hidden /> {busy ? "Evaluating…" : "Evaluate scenario"}</Button>
          </form>
        </Panel>

        <div className="grid content-start gap-3">
          {error && <ErrorBox error={error} />}
          {busy && <Loading label="Running predictor and SIH objective engine…" />}
          {!res && !busy && !error && <Notice title="No scenario evaluated yet">Configure inputs and press Evaluate scenario.</Notice>}
          {res && (
            <>
              <Notice tone="warning" title="SCENARIO ESTIMATE — NOT MEASURED TELEMETRY">{res.basis}</Notice>
              <Panel title={`Result ${res.scenario_id}`} actions={<StateBadge state={res.prediction.trust.state} />}>
                <div className="grid gap-4 lg:grid-cols-5">
                  <div className="lg:col-span-2">
                    <div className="mb-1 text-[11px] uppercase tracking-wider text-muted-foreground">VLSFO-basis fuel rate at scenario state</div>
                    <PredictionReadout prediction={res.prediction} />
                    {res.prediction.trust.fallback && <ToneChip tone="fallback" className="mt-2">{res.prediction.trust.fallback_label}</ToneChip>}
                  </div>
                  {v ? (
                    <>
                      <Kpi label={`Voyage fuel (${humanize(v.fuel_type)})`} value={v.fuel_t} digits={2} unit={UNITS.mass} note={`${fmt(v.fuel_rate_kg_h, 0)} ${UNITS.fuelRate} over ${fmt(v.voyage_hours, 1)} ${UNITS.hours}`} />
                      <Kpi label="Operational cost" value={fmtUsd(v.cost.total_usd)} unit={UNITS.currency} />
                      <Kpi label="Lifecycle GHG (WtW)" value={v.ghg.wtw_tco2e} digits={2} unit={UNITS.ghg} />
                    </>
                  ) : (
                    <p className="text-sm text-st-ood lg:col-span-3">No voyage evaluation: the predictor produced no fuel rate ({humanize(res.prediction.trust.state)}).</p>
                  )}
                </div>
              </Panel>
              {v && (
                <div className="grid gap-3 lg:grid-cols-3">
                  <Panel title="Cost breakdown" subtitle={UNITS.currency}>
                    <dl>
                      <Field label="Fuel" value={fmtUsd(v.cost.fuel_usd)} />
                      <Field label="Carbon (EU ETS)" value={fmtUsd(v.cost.carbon_usd)} />
                      <Field label="Shore power (electricity)" value={fmtUsd(v.cost.shore_power_usd)} />
                      <Field label="Schedule penalty" value={fmtUsd(v.cost.schedule_penalty_usd)} />
                      <Field label="FuelEU penalty" value={fmtUsd(v.cost.fueleu_penalty_usd)} />
                      <Field label="Total" value={fmtUsd(v.cost.total_usd)} />
                      <Field label={`Berth (${humanize(v.berth.source)}), included above`} value={fmtUsd(v.berth.cost_usd)} />
                    </dl>
                  </Panel>
                  <Panel title="Lifecycle GHG" subtitle={UNITS.ghg}>
                    <dl>
                      <Field label="Well-to-tank" value={fmt(v.ghg.wtt_tco2e, 2)} />
                      <Field label="Tank-to-wake" value={fmt(v.ghg.ttw_tco2e, 2)} />
                      <Field label="Methane slip" value={fmt(v.ghg.methane_slip_tco2e, 2)} />
                      {v.berth.source === "SHORE POWER" && <Field label="Shore grid electricity" value={fmt(v.berth.ghg_tco2e, 2)} />}
                      <Field label="Well-to-wake" value={fmt(v.ghg.wtw_tco2e, 2)} />
                      <Field label={`Berth ${fmt(v.berth.energy_kwh, 0)} kWh via ${humanize(v.berth.source)}${v.berth.fuel_t > 0 ? ` (${fmt(v.berth.fuel_t, 3)} t fuel)` : ""}, included`} value={fmt(v.berth.ghg_tco2e, 2)} />
                    </dl>
                  </Panel>
                  <Panel title="Schedule & feasibility">
                    <dl>
                      <Field label="Voyage time" value={fmt(v.voyage_hours, 2)} unit={UNITS.hours} />
                      <Field label="Deadline" value={fmt(v.schedule.deadline_h, 1)} unit={UNITS.hours} />
                      <Field label="Delay" value={fmt(v.schedule.delay_h, 2)} unit={UNITS.hours} />
                      <Field label="Feasible" value={v.feasible ? "YES" : "NO — deadline missed"} />
                    </dl>
                  </Panel>
                </div>
              )}
              <div className="grid gap-3 lg:grid-cols-2">
                <Panel title="Input provenance" subtitle="MEASURED vs ASSUMED vs SCENARIO INPUT, per field">
                  <dl>
                    {Object.entries(res.provenance).map(([k, p]) => (
                      <Field key={k} label={k} value={<ProvenanceTag kind={provenanceKind(p)} title={p} />}
                        tag={res.prediction.input[k] !== undefined ? <span className="num text-[11px]">= {typeof res.prediction.input[k] === "number" ? Number((res.prediction.input[k] as number).toFixed(3)) : String(res.prediction.input[k])}</span> : undefined} />
                    ))}
                  </dl>
                  <p className="mt-2 text-[11px] text-muted-foreground">Unsupported here: {res.unsupported_inputs.join("; ")}</p>
                </Panel>
                <Panel title="Assumptions & configuration" subtitle={<>{res.assumptions.fuels_config} · sha256 {res.assumptions.fuels_config_sha256.slice(0, 12)}…</>}>
                  <dl>
                    <Field label="Fuel pathway" value={res.assumptions.fuel.name} />
                    <Field label="Lower heating value" value={fmt(res.assumptions.fuel.lhv_mj_kg, 1)} unit="MJ/kg" />
                    <Field label="Bunker price" value={fmtUsd(res.assumptions.fuel.price_usd_per_tonne)} unit="/t" />
                    <Field label="WtT factor" value={fmt(res.assumptions.fuel.wtt_ghg_g_co2e_mj, 1)} unit="gCO2e/MJ" />
                    <Field label="TtW CO2 factor" value={fmt(res.assumptions.fuel.ttw_co2_g_per_g_fuel, 3)} unit="g/g fuel" />
                    <Field label="Carbon price" value={fmtUsd(res.assumptions.carbon_price_usd_per_tco2)} unit="/tCO2" />
                    <Field label="Shore tariff" value={fmt(res.assumptions.shore_power_tariff_usd_per_kwh, 2)} unit="USD/kWh" />
                    <Field label="Grid emission factor" value={fmt(res.assumptions.shore_power_grid_factor_g_co2e_per_kwh, 0)} unit="gCO2e/kWh" />
                    <Field label="Hotel load" value={fmt(res.assumptions.hotel_load_kw, 0)} unit="kW" tag={<ProvenanceTag kind="ASSUMED" />} />
                    <Field label="Factor source" value={<span className="text-xs">{res.assumptions.fuel.source ?? "—"}</span>} />
                  </dl>
                </Panel>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
