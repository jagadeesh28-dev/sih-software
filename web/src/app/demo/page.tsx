"use client";

import { ChevronRight, MonitorPlay, Play } from "lucide-react";
import { useState, type ReactNode } from "react";
import { PredictionReadout, TrustBanner } from "@/components/hmi/prediction-view";
import { DataState, ErrorBoundary, ErrorBox, Field, Kpi, Loading, PageHeader, Panel, PlanStatus, ProvenanceTag, StateBadge, ToneChip } from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import {
  api, FuelsSchema, ParetoSchema, PredictionSchema, SolutionSchema, VoyageSchema, type DemoRun, type Prediction,
} from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

function PredCard({ title, p }: { title: string; p: Prediction }) {
  return (
    <Panel title={title} actions={<StateBadge state={p.trust.state} />}>
      <PredictionReadout prediction={p} />
      <dl className="mt-2">
        <Field label="STW" value={fmt(p.input.stw_kn as number, 1)} unit={UNITS.speed} />
        <Field label="Served by" value={p.result.model ?? "none"} />
        {p.trust.fallback && <Field label="Fallback" value={<ToneChip tone="fallback">{p.trust.fallback_label}</ToneChip>} />}
      </dl>
    </Panel>
  );
}

function SceneBody({ run }: { run: DemoRun }): ReactNode {
  const d = run.data;
  const P = (x: unknown) => PredictionSchema.parse(x);
  switch (run.scene_id) {
    case 1:
      return <div className="grid gap-3"><TrustBanner prediction={P(d.prediction)} /><PredCard title="CPS_Poseidon · normal cruise" p={P(d.prediction)} /></div>;
    case 2:
      return <div className="grid gap-3 md:grid-cols-2"><PredCard title="Baseline (normal cruise)" p={P(d.baseline)} /><PredCard title="High demand (higher speed, sea state and wind)" p={P(d.high_demand)} /></div>;
    case 3:
      return <div className="grid gap-3 md:grid-cols-2"><PredCard title="Baseline speed" p={P(d.baseline_18kn)} /><PredCard title="Slow steaming" p={P(d.slow_15kn)} /></div>;
    case 5:
    case 6: {
      const p = P(d.prediction);
      return (
        <div className="grid gap-3">
          {run.scene_id === 6 && <ToneChip tone="ood">INJECTED FAULT: {String(d.injected_fault)}</ToneChip>}
          <TrustBanner prediction={p} />
          <PredCard title={run.scene_id === 5 ? "Storm input (verified demo scene)" : "Normal cruise with failed QI boosters"} p={p} />
        </div>
      );
    }
    case 4: {
      const f = FuelsSchema.parse(d);
      return (
        <Panel title={`Fuel pathways at ${fmt(f.speed_kn, 1)} kn`} subtitle={<ToneChip tone="demo">SCENARIO ESTIMATE — NOT MEASURED GREEN-FUEL TELEMETRY</ToneChip>}>
          <dl>{f.rows.map((r) => <Field key={r.key} label={`${r.label} · ${r.basis}`} value={`${fmt(r.result.fuel_rate_kg_h, 0)} ${UNITS.fuelRate} · ${fmt(r.result.ghg.wtw_tco2e, 3)} ${UNITS.ghg}`} />)}</dl>
        </Panel>
      );
    }
    case 7: {
      const s = SolutionSchema.parse(d.solution);
      const c = d.config as Record<string, unknown>;
      return (
        <Panel title={`Live optimizer run · ${c.algorithm} seed ${c.seed} budget ${c.budget}`} subtitle={<ToneChip tone="warning">ADVISORY — REQUIRES HUMAN ACCEPTANCE</ToneChip>}
          actions={<PlanStatus plan={s} />}>
          {s.objectives && (
            <div className="mb-3 grid grid-cols-2 gap-4 md:grid-cols-4">
              <Kpi label="Fuel" value={s.objectives.fuel_t} digits={2} unit={UNITS.mass} />
              <Kpi label="OPEX" value={fmtUsd(s.objectives.opex_usd)} unit={UNITS.currency} />
              <Kpi label="WtW GHG" value={s.objectives.wtw_tco2e} digits={2} unit={UNITS.ghg} />
              <Kpi label="Delay" value={s.objectives.delay_h} digits={2} unit={UNITS.hours} />
            </div>
          )}
          <dl>{s.vessels.map((v) => <Field key={v.vessel_id} label={`${v.vessel_id} → ${v.assigned_demand}`} value={`${fmt(v.speed_kn, 1)} ${UNITS.speed} · ${humanize(v.fuel)} · cargo ${fmt(v.cargo_tonnes, 0)} t · shore ${v.shore_power ? "yes" : "no"}`} />)}</dl>
        </Panel>
      );
    }
    case 8:
      return <div className="grid gap-3 md:grid-cols-3">{(d.vessels as unknown[]).map((x) => { const p = P(x); return <PredCard key={String(p.input.vessel_id)} title={`${p.input.vessel_id} (${humanize(String(p.input.vessel_type))})`} p={p} />; })}</div>;
    case 9: {
      const a = VoyageSchema.parse(d.fuel_focus_12kn);
      const b = VoyageSchema.parse(d.cost_focus_14_5kn_ops);
      return (
        <div className="grid gap-3">
          <ToneChip tone="info">{String(d.basis)}</ToneChip>
          <div className="grid gap-3 md:grid-cols-2">
            {([["Fuel focus · slower, no shore power", a], ["Cost focus · faster + shore power", b]] as const).map(([t, v]) => (
              <Panel key={t} title={t}>
                <dl>
                  <Field label="Fuel" value={fmt(v.fuel_t, 2)} unit={UNITS.mass} />
                  <Field label="Fuel cost" value={fmtUsd(v.cost.fuel_usd)} />
                  <Field label="Carbon cost" value={fmtUsd(v.cost.carbon_usd)} />
                  <Field label="Shore power" value={fmtUsd(v.cost.shore_power_usd)} />
                  <Field label="Total OPEX" value={fmtUsd(v.cost.total_usd)} unit={UNITS.currency} />
                </dl>
              </Panel>
            ))}
          </div>
        </div>
      );
    }
    case 10:
      return (
        <Panel title="Well-to-wake GHG by pathway" subtitle={<ToneChip tone="demo">{String(d.basis)}</ToneChip>}>
          <dl>{(d.fuels as { label: string; result: unknown }[]).map((x) => { const v = VoyageSchema.parse(x.result); return <Field key={x.label} label={x.label} value={`${fmt(v.ghg.wtw_tco2e, 2)} ${UNITS.ghg} · ${fmtUsd(v.cost.total_usd)}`} />; })}</dl>
        </Panel>
      );
    case 11: {
      const p = ParetoSchema.parse(d);
      return (
        <Panel title="Stored Pareto archive" subtitle={<><ProvenanceTag kind="STORED" /> {p.points.length} non-dominated penalty-free points from {p.archived_rows} rows</>}>
          <dl>{p.points.map((pt) => <Field key={pt.solution_id} label={`${pt.solution_id} · ${humanize(pt.formulation)}`} value={`${fmtUsd(pt.cost_usd)} · ${fmt(pt.ghg_tonnes, 2)} ${UNITS.ghg}`} />)}</dl>
          <p className="mt-2 text-xs text-muted-foreground">There is no single optimum; the operator weighs cost against emissions.</p>
        </Panel>
      );
    }
    default:
      return <pre className="text-xs">{JSON.stringify(d, null, 2)}</pre>;
  }
}

export default function DemoPage() {
  const scenes = useApi(api.demoScenes, []);
  const [run, setRun] = useState<DemoRun>();
  const [active, setActive] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  const play = async (id: number) => {
    setActive(id); setBusy(true); setError(undefined); setRun(undefined);
    try { setRun(await api.runDemo(id)); } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  };


  return (
    <>
      <div role="note" className="mb-3 flex items-center gap-3 rounded-md border-2 border-st-demo bg-st-demo/15 px-4 py-2">
        <MonitorPlay className="size-6 text-st-demo" aria-hidden />
        <div className="text-base font-bold tracking-[0.2em] text-st-demo">DEMO MODE · SIMULATION</div>
        <div className="text-xs text-muted-foreground">Deterministic scenes from scripts/demo_scenarios.py, computed live by the backend. This is not live vessel telemetry.</div>
      </div>
      <PageHeader title="Demonstration workflow" badge={<ToneChip tone="demo">DEMO</ToneChip>} />
      <DataState state={scenes}>
        {(s) => (
          <div className="grid gap-3 xl:grid-cols-[280px_minmax(0,1fr)]">
            <Panel title="Scenes" subtitle={s.source}>
              <ol className="grid gap-1">
                {s.scenes.map((sc) => (
                  <li key={sc.id}>
                    <button type="button" onClick={() => play(sc.id)} aria-current={active === sc.id ? "step" : undefined}
                      className={cn("flex w-full items-center gap-2 rounded-sm border px-2 py-1.5 text-left text-sm hover:bg-accent",
                        active === sc.id ? "border-st-demo bg-st-demo/10 font-semibold" : "border-transparent")}>
                      <span className="num w-5 text-muted-foreground">{sc.id}</span>{sc.title}
                    </button>
                  </li>
                ))}
              </ol>
            </Panel>
            <div className="grid content-start gap-3">
              {active === null && <p className="text-sm text-muted-foreground">Select a scene, or start the walkthrough.</p>}
              <div className="flex items-center gap-2">
                <Button onClick={() => play(active === null ? 1 : Math.min(active + 1, s.scenes.length))} disabled={busy}>
                  {active === null ? <><Play className="size-4" aria-hidden /> Start walkthrough</> : <>Next scene <ChevronRight className="size-4" aria-hidden /></>}
                </Button>
                {run && <span className="text-sm font-semibold">Scene {run.scene_id}: {run.title}</span>}
              </div>
              {busy && <Loading label={active === 7 ? "Running the real optimizer (DE, 2,500 evaluations)…" : "Computing scene on the backend…"} />}
              {error && <ErrorBox error={error} onRetry={() => active && play(active)} />}
              {run && <ErrorBoundary resetKey={run}><SceneBody run={run} /></ErrorBoundary>}
            </div>
          </div>
        )}
      </DataState>
    </>
  );
}
