"use client";

import { Anchor, ArrowRight, Clock, Compass, DollarSign, Droplets, Gauge, Leaf, ShieldAlert, Sliders, Wind } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { PredictionReadout } from "@/components/hmi/prediction-view";
import {
  ConfidenceBand,
  DataState,
  ErrorBox,
  Field,
  Kpi,
  Loading,
  Notice,
  PageHeader,
  Panel,
  ProvenanceTag,
  StateBadge,
  TechnicalDetails,
  ToneChip,
  provenanceKind,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { api, type Scenario } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const OVERRIDES = [
  { key: "stw_kn", label: "Speed Through Water (STW)", unit: UNITS.speed, placeholder: "14.5" },
  { key: "draft_m", label: "Operational Draft", unit: UNITS.length, placeholder: "8.2" },
  { key: "displacement_t", label: "Displacement / Loading", unit: UNITS.displacement, placeholder: "25000" },
  { key: "wind_speed_ms", label: "Wind Speed", unit: UNITS.windSpeed, placeholder: "6.5" },
  { key: "wave_height_m", label: "Significant Wave Height (Hs)", unit: UNITS.length, placeholder: "1.8" },
  { key: "water_depth_m", label: "Under-Keel Water Depth", unit: UNITS.length, placeholder: "45.0" },
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
    setBusy(true);
    setError(undefined);
    const overrides = Object.fromEntries(
      Object.entries(ov)
        .filter(([, v]) => v !== "")
        .map(([k, v]) => [k, Number(v)])
    );
    try {
      const r = await api.scenario({
        vessel_id: activeVessel,
        base,
        overrides,
        fuel_type: fuel,
        use_shore_power: shore,
        port_hours: Number(portH),
        distance_nm: Number(dist),
        deadline_h: Number(deadline),
      });
      setRes(r);
      setScenarioId(r.scenario_id);
    } catch (e) {
      setError((e as Error).message);
      setRes(undefined);
    } finally {
      setBusy(false);
    }
  };

  const fuels = Array.from(new Map((fuelOptions.data?.rows ?? []).filter((r) => !r.shore_power).map((r) => [r.fuel, r.assumptions.name])));
  const v = res?.voyage;

  return (
    <>
      <PageHeader
        title="Voyage Scenario Simulation"
        badge={<ToneChip tone="info">Decision Support</ToneChip>}
        description="Simulate what-if voyage configurations with speed, weather, alternative fuel pathways, and port shore power. All predictions and emissions estimates use the verified hydrodynamics and lifecycle carbon accounting engines."
      />

      <div className="grid gap-4 xl:grid-cols-[420px_minmax(0,1fr)]">
        {/* Left Column: Parameter Configuration */}
        <Panel title="Voyage Simulation Parameters" subtitle="Specify vessel, voyage conditions, and environmental overrides">
          <form className="grid gap-4" onSubmit={(e) => { e.preventDefault(); run(); }}>
            {/* Vessel & Baseline State */}
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1">
                <Label htmlFor="vessel" className="text-xs font-medium">Target Vessel</Label>
                <select
                  id="vessel"
                  value={activeVessel}
                  onChange={(e) => setActiveVessel(e.target.value)}
                  className="h-8 w-full min-w-0 rounded-md border border-input/60 bg-input/20 px-2 text-xs font-medium focus:border-cyan-500 focus:outline-none"
                >
                  {vessels.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              </div>

              <div className="grid gap-1">
                <Label htmlFor="base" className="text-xs font-medium">Initial Baseline State</Label>
                <select
                  id="base"
                  value={base}
                  onChange={(e) => setBase(e.target.value as typeof base)}
                  className="h-8 w-full min-w-0 rounded-md border border-input/60 bg-input/20 px-2 text-xs font-medium focus:border-cyan-500 focus:outline-none"
                >
                  <option value="fleet_default">Fleet Default Telemetry</option>
                  <option value="dataset_latest">Latest Recorded Telemetry</option>
                </select>
              </div>
            </div>

            {/* Vessel Hydrodynamics & Environmental Overrides */}
            <div className="rounded-md border border-panel-border bg-panel-2/40 p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
                <Sliders className="size-3.5 text-cyan-400" /> Operational & Weather Overrides
              </div>
              <div className="grid grid-cols-2 gap-2.5">
                {OVERRIDES.map((o) => (
                  <div key={o.key} className="grid gap-1">
                    <Label htmlFor={o.key} className="text-[11px] text-muted-foreground flex justify-between">
                      <span>{o.label}</span>
                      <span className="font-mono text-[10px]">{o.unit}</span>
                    </Label>
                    <Input
                      id={o.key}
                      inputMode="decimal"
                      className="num h-7 text-xs font-mono"
                      placeholder={o.placeholder}
                      value={ov[o.key] ?? ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        setOv((cur) => ({ ...cur, [o.key]: val }));
                      }}
                    />
                  </div>
                ))}
              </div>
              <p className="mt-2 text-[10px] text-muted-foreground">Leaving a field blank uses the baseline vessel operating point.</p>
            </div>

            {/* Route & Energy Management */}
            <div className="rounded-md border border-panel-border bg-panel-2/40 p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
                <Compass className="size-3.5 text-cyan-400" /> Route & Energy Pathways
              </div>

              <div className="grid gap-3">
                <div className="grid gap-1">
                  <Label htmlFor="fuel" className="text-xs">Fuel Pathway Selection</Label>
                  <select
                    id="fuel"
                    value={fuel}
                    onChange={(e) => setFuel(e.target.value)}
                    className="h-8 w-full rounded-md border border-input/60 bg-input/20 px-2 text-xs font-medium focus:border-cyan-500 focus:outline-none"
                  >
                    {fuels.length ? (
                      fuels.map(([k, name]) => (
                        <option key={k} value={k}>{name}</option>
                      ))
                    ) : (
                      <option value="vlsfo">Very Low Sulphur Fuel Oil (VLSFO)</option>
                    )}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2.5">
                  <div className="grid gap-1">
                    <Label htmlFor="dist" className="text-xs">Voyage Distance ({UNITS.distance})</Label>
                    <Input
                      id="dist"
                      inputMode="decimal"
                      className="num h-7 text-xs font-mono"
                      value={dist}
                      onChange={(e) => setDist(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-1">
                    <Label htmlFor="deadline" className="text-xs">Schedule Deadline ({UNITS.hours})</Label>
                    <Input
                      id="deadline"
                      inputMode="decimal"
                      className="num h-7 text-xs font-mono"
                      value={deadline}
                      onChange={(e) => setDeadline(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2.5 items-center pt-1 border-t border-panel-border/50">
                  <div className="grid gap-1">
                    <Label htmlFor="port" className="text-xs">Berth Duration ({UNITS.hours})</Label>
                    <Input
                      id="port"
                      inputMode="decimal"
                      className="num h-7 text-xs font-mono"
                      value={portH}
                      onChange={(e) => setPortH(e.target.value)}
                    />
                  </div>
                  <div className="flex items-center gap-2 pt-4">
                    <Switch id="shore" checked={shore} onCheckedChange={setShore} />
                    <Label htmlFor="shore" className="text-xs cursor-pointer">Cold Ironing (Shore Power)</Label>
                  </div>
                </div>
              </div>
            </div>

            <Button type="submit" disabled={busy} className="h-9 w-full text-xs font-semibold">
              <Compass className="size-4 mr-1.5" /> {busy ? "Computing Hydrodynamic & Carbon Simulation..." : "Simulate Scenario Voyage"}
            </Button>
          </form>
        </Panel>

        {/* Right Column: Scenario Results */}
        <div className="grid content-start gap-4">
          {error && <ErrorBox error={error} />}
          {busy && <Loading label="Evaluating physics resistance, conformal uncertainty, and lifecycle emissions..." />}

          {!res && !busy && !error && (
            <Panel title="Scenario Evaluation Status" subtitle="Awaiting operator input">
              <div className="py-16 text-center text-sm text-muted-foreground">
                <Compass className="mx-auto mb-3 size-10 opacity-30" />
                <p className="font-medium text-foreground">Configure voyage parameters and run the simulation</p>
                <p className="text-xs mt-1 max-w-md mx-auto">
                  The engine will calculate hydrodynamic shaft resistance, predicted fuel consumption, lifecycle emissions (WtW), and financial OPEX including carbon pricing and shore power tariffs.
                </p>
              </div>
            </Panel>
          )}

          {res && (
            <>
              {/* Dignified Operational Notice */}
              <div className="rounded-md border border-cyan-800/60 bg-cyan-950/20 px-4 py-2.5 flex items-start gap-3">
                <Compass className="size-5 text-cyan-400 mt-0.5 shrink-0" />
                <div className="text-xs text-cyan-200/90 leading-relaxed">
                  <span className="font-semibold text-cyan-300">SCENARIO ESTIMATE · MODELLED LIFECYCLE EVALUATION: </span>
                  {res.basis}
                </div>
              </div>

              {/* Primary KPI Strip */}
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                <Kpi
                  label="Predicted Fuel Burn"
                  value={v ? fmt(v.fuel_t, 2) : "—"}
                  unit={UNITS.mass}
                  note={v ? `${fmt(v.fuel_rate_kg_h, 0)} kg/h average rate` : undefined}
                />
                <Kpi
                  label="Operational Expenditure"
                  value={v ? fmtUsd(v.cost.total_usd) : "—"}
                  note={v ? `Includes bunkers, carbon & port berth` : undefined}
                />
                <Kpi
                  label="Lifecycle WtW GHG"
                  value={v ? fmt(v.ghg.wtw_tco2e, 2) : "—"}
                  unit={UNITS.ghg}
                  note={v ? `Well-to-Wake total impact` : undefined}
                />
                <Kpi
                  label="Schedule Adherence"
                  value={v ? (v.feasible ? "ON SCHEDULE" : "DELAYED") : "—"}
                  note={v ? `${fmt(v.voyage_hours, 1)} h total voyage time` : undefined}
                />
              </div>

              {/* Fuel Prediction & Uncertainty Card */}
              <Panel
                title="At-Sea Predicted Consumption Rate"
                subtitle={`Calculated at ${fmt(res.prediction.input.stw_kn as number, 1)} kn STW`}
                actions={<StateBadge state={res.prediction.trust.state} />}
              >
                <div className="grid gap-4 md:grid-cols-2 items-center">
                  <div className="rounded-md bg-panel-2/60 p-4 border border-panel-border/60">
                    <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1 font-medium">Predicted Fuel Burn Rate</div>
                    <div className="text-3xl font-bold font-mono text-cyan-300">
                      {fmt(res.prediction.result.fuel_prediction, 1)}{" "}
                      <span className="text-sm font-normal text-muted-foreground">{UNITS.fuelRate}</span>
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground font-mono">
                      ~ {fmt(((res.prediction.result.fuel_prediction ?? 0) * 24) / 1000, 2)} tonnes / day
                    </div>
                  </div>

                  <div>
                    <ConfidenceBand
                      lower={res.prediction.result.uncertainty?.lower_bound_kg_h}
                      upper={res.prediction.result.uncertainty?.upper_bound_kg_h}
                      value={res.prediction.result.fuel_prediction}
                      confidence={res.prediction.result.uncertainty?.coverage}
                    />
                    <div className="mt-2 text-xs text-muted-foreground">
                      Reliability Assessment:{" "}
                      <span className={cn(
                        "font-semibold",
                        res.prediction.trust.state === "NORMAL" ? "text-emerald-400" : "text-amber-400"
                      )}>
                        {res.prediction.trust.state === "NORMAL" ? "High Confidence (Within Operational Envelope)" : "Attention Required"}
                      </span>
                    </div>
                  </div>
                </div>
              </Panel>

              {/* Breakdown Grid: Cost vs GHG vs Schedule */}
              {v && (
                <div className="grid gap-4 lg:grid-cols-3">
                  {/* Financial Breakdown */}
                  <Panel title="Voyage OPEX Breakdown" subtitle="Bunkers, Carbon & Berth Tariffs">
                    <dl className="grid gap-1.5 text-xs">
                      <Field label="Bunker Fuel Cost" value={fmtUsd(v.cost.fuel_usd)} />
                      <Field label="EU ETS Carbon Cost" value={fmtUsd(v.cost.carbon_usd)} />
                      <Field label="Shore Power Tariff" value={fmtUsd(v.cost.shore_power_usd)} />
                      <Field label="Schedule Delay Penalty" value={fmtUsd(v.cost.schedule_penalty_usd)} />
                      <Field label="FuelEU Maritime Penalty" value={fmtUsd(v.cost.fueleu_penalty_usd)} />
                      <div className="border-t pt-1.5 mt-1 font-semibold">
                        <Field label="Total Voyage OPEX" value={<span className="text-cyan-300 font-mono text-sm">{fmtUsd(v.cost.total_usd)}</span>} />
                      </div>
                      <Field
                        label={`Berth Energy (${humanize(v.berth.source)})`}
                        value={fmtUsd(v.berth.cost_usd)}
                        tag={<span className="text-[10px] text-muted-foreground">(included above)</span>}
                      />
                    </dl>
                  </Panel>

                  {/* Carbon Accounting */}
                  <Panel title="Lifecycle GHG Breakdown" subtitle="Well-to-Tank & Tank-to-Wake (tCO2e)">
                    <dl className="grid gap-1.5 text-xs">
                      <Field label="Well-to-Tank (Upstream)" value={fmt(v.ghg.wtt_tco2e, 2)} unit={UNITS.ghg} />
                      <Field label="Tank-to-Wake (Combustion)" value={fmt(v.ghg.ttw_tco2e, 2)} unit={UNITS.ghg} />
                      <Field label="Methane Slip Factor" value={fmt(v.ghg.methane_slip_tco2e, 2)} unit={UNITS.ghg} />
                      {v.berth.source === "SHORE POWER" && (
                        <Field label="Shore Grid Upstream GHG" value={fmt(v.berth.ghg_tco2e, 2)} unit={UNITS.ghg} />
                      )}
                      <div className="border-t pt-1.5 mt-1 font-semibold">
                        <Field label="Total Well-to-Wake GHG" value={<span className="text-emerald-300 font-mono text-sm">{fmt(v.ghg.wtw_tco2e, 2)} tCO2e</span>} />
                      </div>
                      <Field
                        label={`Berth: ${fmt(v.berth.energy_kwh, 0)} kWh via ${humanize(v.berth.source)}`}
                        value={fmt(v.berth.ghg_tco2e, 2)}
                        unit={UNITS.ghg}
                      />
                    </dl>
                  </Panel>

                  {/* Schedule & Feasibility */}
                  <Panel title="Voyage Schedule & Constraints" subtitle="Transit Time and Berth Duration">
                    <dl className="grid gap-1.5 text-xs">
                      <Field label="Sea Transit Duration" value={fmt(v.voyage_hours, 1)} unit={UNITS.hours} />
                      <Field label="Berth Time at Port" value={fmt(Number(portH), 1)} unit={UNITS.hours} />
                      <Field label="Total Voyage Time" value={fmt(v.voyage_hours + Number(portH), 1)} unit={UNITS.hours} />
                      <Field label="Contractual Deadline" value={fmt(v.schedule.deadline_h, 1)} unit={UNITS.hours} />
                      <Field label="Estimated Delay" value={fmt(v.schedule.delay_h, 1)} unit={UNITS.hours} />
                      <div className="border-t pt-1.5 mt-1">
                        <Field
                          label="Schedule Feasibility"
                          value={
                            v.feasible ? (
                              <ToneChip tone="normal">FEASIBLE (ON SCHEDULE)</ToneChip>
                            ) : (
                              <ToneChip tone="ood">DEADLINE MISSED</ToneChip>
                            )
                          }
                        />
                      </div>
                    </dl>
                  </Panel>
                </div>
              )}

              {/* Technical Details Progressive Disclosure */}
              <TechnicalDetails title="Scientific Assumptions & Data Provenance">
                <div className="grid gap-3 lg:grid-cols-2 text-xs">
                  <div>
                    <div className="font-semibold text-foreground mb-1">Input Variable Provenance</div>
                    <dl className="grid gap-1">
                      {Object.entries(res.provenance).map(([k, p]) => (
                        <Field
                          key={k}
                          label={k}
                          value={<ProvenanceTag kind={provenanceKind(p)} title={p} />}
                          tag={
                            res.prediction.input[k] !== undefined ? (
                              <span className="num text-[11px] font-mono">
                                = {typeof res.prediction.input[k] === "number"
                                  ? Number((res.prediction.input[k] as number).toFixed(2))
                                  : String(res.prediction.input[k])}
                              </span>
                            ) : undefined
                          }
                        />
                      ))}
                    </dl>
                  </div>

                  <div>
                    <div className="font-semibold text-foreground mb-1">Fuel Pathway Parameters ({res.assumptions.fuel.name})</div>
                    <dl className="grid gap-1">
                      <Field label="Lower Heating Value (LHV)" value={fmt(res.assumptions.fuel.lhv_mj_kg, 1)} unit="MJ/kg" />
                      <Field label="Bunker Fuel Price" value={fmtUsd(res.assumptions.fuel.price_usd_per_tonne)} unit="/t" />
                      <Field label="Upstream WtT Factor" value={fmt(res.assumptions.fuel.wtt_ghg_g_co2e_mj, 1)} unit="gCO2e/MJ" />
                      <Field label="Combustion TtW CO2 Factor" value={fmt(res.assumptions.fuel.ttw_co2_g_per_g_fuel, 3)} unit="g/g fuel" />
                      <Field label="EU ETS Carbon Allowance" value={fmtUsd(res.assumptions.carbon_price_usd_per_tco2)} unit="/tCO2" />
                      <Field label="Shore Electricity Tariff" value={fmt(res.assumptions.shore_power_tariff_usd_per_kwh, 2)} unit="USD/kWh" />
                      <Field label="Hotel Load Demand" value={fmt(res.assumptions.hotel_load_kw, 0)} unit="kW" />
                    </dl>
                  </div>
                </div>
              </TechnicalDetails>
            </>
          )}
        </div>
      </div>
    </>
  );
}
