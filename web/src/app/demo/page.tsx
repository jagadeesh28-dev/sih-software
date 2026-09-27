"use client";

import {
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  Compass,
  Cpu,
  ExternalLink,
  Flame,
  Layers,
  MonitorPlay,
  Play,
  Scale,
  ShieldAlert,
  Ship,
  Sliders,
} from "lucide-react";
import Link from "next/link";
import { useState, type ReactNode } from "react";
import { PredictionReadout, TrustBanner } from "@/components/hmi/prediction-view";
import {
  DataState,
  ErrorBoundary,
  ErrorBox,
  Field,
  Kpi,
  Loading,
  PageHeader,
  Panel,
  PlanStatus,
  ProvenanceTag,
  StateBadge,
  TechnicalDetails,
  ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import {
  api,
  FuelsSchema,
  ParetoSchema,
  PredictionSchema,
  SolutionSchema,
  VoyageSchema,
  type DemoRun,
  type Prediction,
} from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

// 12-Step Primary Operator Journey for SIH Jury Evaluation
const JURY_WORKFLOW_STEPS = [
  { step: "01", title: "Fleet Overview", desc: "Fleet status, route topology & dispatch KPI strip", href: "/fleet", icon: Ship },
  { step: "02", title: "Vessel Performance", desc: "Telemetry replay & hydrodynamic speed impact", href: "/vessel/CPS_Poseidon", icon: Compass },
  { step: "03", title: "Fuel Prediction", desc: "Physics + ML residual with conformal uncertainty", href: "/trust", icon: Flame },
  { step: "04", title: "Fleet Optimization", desc: "Quantum-inspired dispatch (Current vs. Optimized)", href: "/optimizer", icon: Cpu },
  { step: "05", title: "Decision Space", desc: "Pareto frontier: OPEX vs. Lifecycle WtW GHG", href: "/pareto", icon: Scale },
  { step: "06", title: "Voyage Scenarios", desc: "What-if simulation with weather & deadline overrides", href: "/scenario", icon: Sliders },
  { step: "07", title: "Alternative Fuels", desc: "Methanol, LNG, Ammonia & shore cold-ironing", href: "/fuels", icon: Layers },
  { step: "08", title: "Operations Reports", desc: "Verifiable SQLite audit ledger & release gate evidence", href: "/audit", icon: CheckCircle2 },
];

function PredCard({ title, p }: { title: string; p: Prediction }) {
  return (
    <Panel title={title} actions={<StateBadge state={p.trust.state} />}>
      <PredictionReadout prediction={p} />
      <dl className="mt-2 text-xs">
        <Field label="Speed Through Water (STW)" value={fmt(p.input.stw_kn as number, 1)} unit={UNITS.speed} />
        <Field label="Prediction Engine" value={p.result.model ?? "Physics + ML Residual"} />
        {p.trust.fallback && (
          <Field label="Operational State" value={<ToneChip tone="fallback">{p.trust.fallback_label}</ToneChip>} />
        )}
      </dl>
    </Panel>
  );
}

function SceneBody({ run }: { run: DemoRun }): ReactNode {
  const d = run.data;
  const P = (x: unknown) => PredictionSchema.parse(x);

  switch (run.scene_id) {
    case 1:
      return (
        <div className="grid gap-3">
          <TrustBanner prediction={P(d.prediction)} />
          <PredCard title="CPS Poseidon · Nominal Cruise" p={P(d.prediction)} />
        </div>
      );
    case 2:
      return (
        <div className="grid gap-3 md:grid-cols-2">
          <PredCard title="Baseline Cruise (14.5 kn)" p={P(d.baseline)} />
          <PredCard title="High Demand Excursion (17.5 kn, High Sea State)" p={P(d.high_demand)} />
        </div>
      );
    case 3:
      return (
        <div className="grid gap-3 md:grid-cols-2">
          <PredCard title="Baseline Speed (18.0 kn)" p={P(d.baseline_18kn)} />
          <PredCard title="Slow Steaming Setpoint (15.0 kn)" p={P(d.slow_15kn)} />
        </div>
      );
    case 4: {
      const f = FuelsSchema.parse(d);
      return (
        <Panel
          title={`Alternative Fuel Pathways at ${fmt(f.speed_kn, 1)} kn`}
          subtitle="Modelled equal-energy lifecycle evaluation"
        >
          <dl className="grid gap-2 text-xs">
            {f.rows.map((r) => (
              <Field
                key={r.key}
                label={`${r.label} (${r.basis})`}
                value={`${fmt(r.result.fuel_rate_kg_h, 0)} ${UNITS.fuelRate} · ${fmt(r.result.ghg.wtw_tco2e, 2)} ${UNITS.ghg} WtW`}
              />
            ))}
          </dl>
        </Panel>
      );
    }
    case 5:
    case 6: {
      const p = P(d.prediction);
      return (
        <div className="grid gap-3">
          {run.scene_id === 6 && (
            <div className="rounded border border-amber-600/60 bg-amber-950/20 p-2 text-xs text-amber-200">
              <span className="font-semibold">ENGINEERING TEST FAULT INJECTED: </span>
              {String(d.injected_fault)}
            </div>
          )}
          <TrustBanner prediction={p} />
          <PredCard
            title={run.scene_id === 5 ? "Extreme Storm Operating Envelope (Verified OOD)" : "Primary Booster Fault Simulation"}
            p={p}
          />
        </div>
      );
    }
    case 7: {
      const s = SolutionSchema.parse(d.solution);
      const c = d.config as Record<string, unknown>;
      return (
        <Panel
          title={`Live Optimizer Solution (${c.algorithm}, Seed: ${c.seed}, Budget: ${c.budget})`}
          subtitle="Quantum-inspired search result"
          actions={<PlanStatus plan={s} />}
        >
          {s.objectives && (
            <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
              <Kpi label="Fuel Burn" value={s.objectives.fuel_t} digits={2} unit={UNITS.mass} />
              <Kpi label="Operational Cost" value={fmtUsd(s.objectives.opex_usd)} unit={UNITS.currency} />
              <Kpi label="Lifecycle GHG" value={s.objectives.wtw_tco2e} digits={2} unit={UNITS.ghg} />
              <Kpi label="Schedule Delay" value={s.objectives.delay_h} digits={1} unit={UNITS.hours} />
            </div>
          )}
          <dl className="grid gap-1.5 text-xs">
            {s.vessels.map((v) => (
              <Field
                key={v.vessel_id}
                label={`${v.vessel_id} → Route: ${v.assigned_demand}`}
                value={`${fmt(v.speed_kn, 1)} kn · ${humanize(v.fuel)} · Cargo: ${fmt(v.cargo_tonnes, 0)} t · Shore Pwr: ${v.shore_power ? "YES" : "NO"}`}
              />
            ))}
          </dl>
        </Panel>
      );
    }
    case 8:
      return (
        <div className="grid gap-3 md:grid-cols-3">
          {(d.vessels as unknown[]).map((x) => {
            const p = P(x);
            return (
              <PredCard
                key={String(p.input.vessel_id)}
                title={`${p.input.vessel_id} (${humanize(String(p.input.vessel_type))})`}
                p={p}
              />
            );
          })}
        </div>
      );
    case 9: {
      const a = VoyageSchema.parse(d.fuel_focus_12kn);
      const b = VoyageSchema.parse(d.cost_focus_14_5kn_ops);
      return (
        <div className="grid gap-3">
          <div className="grid gap-3 md:grid-cols-2">
            {[
              ["Fuel Focus: 12.0 kn, No Shore Power", a],
              ["Cost Focus: 14.5 kn, With Shore Power", b],
            ].map(([t, v]) => (
              <Panel key={t as string} title={t as string}>
                <dl className="grid gap-1.5 text-xs">
                  <Field label="Total Fuel" value={fmt((v as typeof a).fuel_t, 2)} unit={UNITS.mass} />
                  <Field label="Bunker Fuel Cost" value={fmtUsd((v as typeof a).cost.fuel_usd)} />
                  <Field label="EU ETS Carbon Cost" value={fmtUsd((v as typeof a).cost.carbon_usd)} />
                  <Field label="Shore Power Tariff" value={fmtUsd((v as typeof a).cost.shore_power_usd)} />
                  <Field label="Total Voyage OPEX" value={fmtUsd((v as typeof a).cost.total_usd)} unit={UNITS.currency} />
                </dl>
              </Panel>
            ))}
          </div>
        </div>
      );
    }
    case 10:
      return (
        <Panel title="Lifecycle Well-to-Wake Emissions by Fuel Pathway" subtitle="Equal energy comparison">
          <dl className="grid gap-1.5 text-xs">
            {(d.fuels as { label: string; result: unknown }[]).map((x) => {
              const v = VoyageSchema.parse(x.result);
              return (
                <Field
                  key={x.label}
                  label={x.label}
                  value={`${fmt(v.ghg.wtw_tco2e, 2)} ${UNITS.ghg} · ${fmtUsd(v.cost.total_usd)}`}
                />
              );
            })}
          </dl>
        </Panel>
      );
    case 11: {
      const p = ParetoSchema.parse(d);
      return (
        <Panel
          title="Verified Stored Pareto Archive"
          subtitle={`${p.points.length} non-dominated solutions verified from ${p.archived_rows} optimizer evaluations`}
        >
          <dl className="grid gap-1.5 text-xs">
            {p.points.map((pt) => (
              <Field
                key={pt.solution_id}
                label={`Solution #${pt.solution_id} (${humanize(pt.formulation)})`}
                value={`${fmtUsd(pt.cost_usd)} · ${fmt(pt.ghg_tonnes, 2)} ${UNITS.ghg}`}
              />
            ))}
          </dl>
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
    setActive(id);
    setBusy(true);
    setError(undefined);
    setRun(undefined);
    try {
      setRun(await api.runDemo(id));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageHeader
        title="SIH Jury Demonstration & Verification Suite"
        badge={<ToneChip tone="info">Engineering & Jury Mode</ToneChip>}
        description="Structured verification environment for SIH judges and marine engineers. Contains both the direct 8-step primary operational decision journey and 11 automated deterministic verification scenes computed live by the backend."
      />

      {/* Part 1: SIH Primary Operator Evaluation Journey Guide */}
      <Panel
        title="SIH Primary Operator Decision Journey"
        subtitle="Follow this 8-step sequence to experience the full operational fleet workflow"
        className="mb-4"
      >
        <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-4">
          {JURY_WORKFLOW_STEPS.map((s) => {
            const Icon = s.icon;
            return (
              <Link
                key={s.step}
                href={s.href}
                className="group flex flex-col justify-between rounded-md border border-panel-border bg-panel-2/60 p-3 transition-colors hover:border-cyan-500/60 hover:bg-cyan-950/20"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-xs font-bold text-cyan-400">Step {s.step}</span>
                    <Icon className="size-4 text-muted-foreground group-hover:text-cyan-400 transition-colors" />
                  </div>
                  <div className="font-semibold text-xs text-foreground group-hover:text-cyan-200">
                    {s.title}
                  </div>
                  <p className="mt-1 text-[11px] text-muted-foreground leading-snug">
                    {s.desc}
                  </p>
                </div>
                <div className="mt-3 flex items-center text-[10px] font-medium text-cyan-400 group-hover:translate-x-0.5 transition-transform">
                  Open Screen <ArrowRight className="size-3 ml-1" />
                </div>
              </Link>
            );
          })}
        </div>
      </Panel>

      {/* Part 2: Automated Verification Scenes */}
      <DataState state={scenes}>
        {(s) => (
          <div className="grid gap-4 xl:grid-cols-[300px_minmax(0,1fr)]">
            <Panel title="Deterministic Evaluation Scenes" subtitle="Computed live by backend scripts/demo_scenarios.py">
              <ol className="grid gap-1">
                {s.scenes.map((sc) => (
                  <li key={sc.id}>
                    <button
                      type="button"
                      onClick={() => play(sc.id)}
                      aria-current={active === sc.id ? "step" : undefined}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-sm border px-2.5 py-1.5 text-left text-xs transition-colors hover:bg-accent",
                        active === sc.id
                          ? "border-cyan-500/80 bg-cyan-950/40 font-semibold text-cyan-200"
                          : "border-transparent text-muted-foreground"
                      )}
                    >
                      <span className="num font-mono w-5 shrink-0">{sc.id}.</span>
                      <span className="truncate">{sc.title}</span>
                    </button>
                  </li>
                ))}
              </ol>
            </Panel>

            <div className="grid content-start gap-4">
              <div className="flex items-center justify-between">
                <Button
                  onClick={() => play(active === null ? 1 : Math.min(active + 1, s.scenes.length))}
                  disabled={busy}
                  className="h-8 text-xs font-semibold"
                >
                  {active === null ? (
                    <>
                      <Play className="size-3.5 mr-1" aria-hidden /> Run Verification Walkthrough
                    </>
                  ) : (
                    <>
                      Next Evaluation Scene <ChevronRight className="size-3.5 ml-1" aria-hidden />
                    </>
                  )}
                </Button>
                {run && (
                  <span className="text-xs font-semibold text-foreground">
                    Scene {run.scene_id}: {run.title}
                  </span>
                )}
              </div>

              {active === null && !busy && (
                <Panel title="Verification Output" subtitle="Awaiting scene selection">
                  <div className="py-12 text-center text-xs text-muted-foreground">
                    <MonitorPlay className="mx-auto mb-2 size-8 opacity-40" />
                    Select an evaluation scene on the left, or click "Run Verification Walkthrough" to execute live backend tests.
                  </div>
                </Panel>
              )}

              {busy && (
                <Loading
                  label={
                    active === 7
                      ? "Running live optimizer search (Differential Evolution, 2,500 evaluations)..."
                      : "Computing deterministic scenario on the backend..."
                  }
                />
              )}

              {error && <ErrorBox error={error} onRetry={() => active && play(active)} />}

              {run && (
                <ErrorBoundary resetKey={run}>
                  <SceneBody run={run} />
                </ErrorBoundary>
              )}
            </div>
          </div>
        )}
      </DataState>
    </>
  );
}
