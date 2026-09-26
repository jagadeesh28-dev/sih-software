"use client";

import { Check, Play, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ConfirmAction } from "@/components/hmi/confirm";
import {
  DataState, ErrorBox, Field, Kpi, Notice, PageHeader, Panel, PlanStatus, ProvenanceTag, ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Job } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";

const WEIGHT_LABELS = ["Fuel", "OPEX", "WtW GHG", "Schedule", "Risk (CVaR)"];
const TERMINAL = new Set(["DONE", "ERROR"]);

export default function OptimizerPage() {
  const cfg = useApi(api.optimizerConfig, [], 5000);
  const [algorithm, setAlgorithm] = useState("Hybrid_QI_A5");
  const [seed, setSeed] = useState("1005");
  const [budget, setBudget] = useState(2500);
  const [weights, setWeights] = useState([0.35, 0.35, 0.3, 0, 0]);
  const [job, setJob] = useState<Job>();
  const [error, setError] = useState<string>();
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!job || TERMINAL.has(job.status)) return;
    const id = setInterval(() => {
      api.job(job.job_id).then(setJob).catch((e: Error) => setError(e.message));
    }, 400);
    return () => clearInterval(id);
  }, [job]);

  const start = async () => {
    setError(undefined);
    try { setJob(await api.optimize({ algorithm, seed: Number(seed), budget, weights })); }
    catch (e) { setError((e as Error).message); }
  };
  const decide = async (d: "ACCEPT" | "REJECT") => {
    if (!job) return;
    try { setJob(await api.decide(job.job_id, d, note)); } catch (e) { setError((e as Error).message); }
  };

  const running = job && !TERMINAL.has(job.status);
  const r = job?.result;
  const pct = job ? Math.round((100 * job.evaluations) / job.budget) : 0;

  return (
    <>
      <PageHeader title="Fleet Optimizer" badge={<ToneChip tone="warning">ADVISORY ONLY</ToneChip>}
        description="Runs the repository's heterogeneous-fleet optimizer on the real-telemetry calibrated evaluator. Progress is the evaluator's own evaluation counter. Results require human acceptance; no vessel or engine commands are issued." />
      <DataState state={cfg}>
        {(c) => (
          <div className="grid gap-3 xl:grid-cols-[360px_minmax(0,1fr)]">
            <div className="grid content-start gap-3">
              <Panel title="Solver" subtitle={c.evaluator_ready ? "Evaluator ready" : c.evaluator_error ? "Evaluator failed" : "Evaluator loading surrogates (~30 s)…"}>
                <form className="grid gap-2" onSubmit={(e) => { e.preventDefault(); start(); }}>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="grid gap-1">
                      <Label htmlFor="alg" className="text-xs">Algorithm</Label>
                      <select id="alg" value={algorithm} onChange={(e) => setAlgorithm(e.target.value)} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                        {c.algorithms.map((a) => <option key={a} value={a}>{humanize(a)}</option>)}
                      </select>
                    </div>
                    <div className="grid gap-1">
                      <Label htmlFor="budget" className="text-xs">Evaluation budget</Label>
                      <select id="budget" value={budget} onChange={(e) => setBudget(Number(e.target.value))} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                        {c.budgets.map((b) => <option key={b} value={b}>{b.toLocaleString()}</option>)}
                      </select>
                    </div>
                    <div className="grid gap-1">
                      <Label htmlFor="seed" className="text-xs">RNG seed</Label>
                      <Input id="seed" inputMode="numeric" className="num h-8" value={seed} onChange={(e) => setSeed(e.target.value)} />
                    </div>
                    <div className="grid gap-1">
                      <Label htmlFor="form" className="text-xs">Weight preset</Label>
                      <select id="form" defaultValue="" onChange={(e) => e.target.value && setWeights(c.formulations[e.target.value])} className="h-8 w-full min-w-0 rounded-md border bg-input/30 px-2 text-sm">
                        <option value="">custom</option>
                        {Object.keys(c.formulations).map((f) => <option key={f} value={f}>{humanize(f)}</option>)}
                      </select>
                    </div>
                  </div>
                  <fieldset className="grid gap-1.5 rounded-md border p-2">
                    <legend className="px-1 text-[11px] uppercase tracking-wider text-muted-foreground">Objective weights</legend>
                    {WEIGHT_LABELS.map((l, i) => (
                      <div key={l} className="grid grid-cols-[92px_1fr_40px] items-center gap-2">
                        <Label htmlFor={`w${i}`} className="text-xs">{l}</Label>
                        <input id={`w${i}`} type="range" min={0} max={1} step={0.05} value={weights[i]}
                          onChange={(e) => setWeights(weights.map((w, j) => (j === i ? Number(e.target.value) : w)))} className="accent-[var(--primary)]" />
                        <span className="num text-right text-xs">{weights[i].toFixed(2)}</span>
                      </div>
                    ))}
                  </fieldset>
                  <Button type="submit" disabled={!!running || !c.evaluator_ready}><Play className="size-4" aria-hidden /> {running ? "Running…" : "Run optimizer"}</Button>
                </form>
              </Panel>
              <Panel title="Constraints enforced by the evaluator" subtitle="Phase4FleetEvaluator docstring (source of truth)">
                <pre className="whitespace-pre-wrap text-xs text-muted-foreground">{c.constraints_doc?.trim()}</pre>
                <p className="mt-2 text-xs text-muted-foreground">Also enforced: per-vessel speed bounds, fuel–engine compatibility, deadline breach, surrogate operating domain.</p>
              </Panel>
            </div>

            <div className="grid content-start gap-3">
              {error && <ErrorBox error={error} />}
              <Panel title="Progress">
                {job ? (
                  <div className="grid gap-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>{job.job_id} · {humanize(job.params.algorithm)} · seed {job.params.seed}</span>
                      <ToneChip tone={job.status === "ERROR" ? "ood" : job.status === "DONE" ? "normal" : "info"}>{humanize(job.status)}</ToneChip>
                    </div>
                    <div role="progressbar" aria-valuenow={job.evaluations} aria-valuemin={0} aria-valuemax={job.budget} aria-label="Objective evaluations"
                      className="h-2 overflow-hidden rounded-sm bg-panel-2">
                      <div className="h-full bg-primary transition-[width]" style={{ width: `${pct}%` }} />
                    </div>
                    <div className="num text-xs text-muted-foreground">
                      {job.evaluations.toLocaleString()} / {job.budget.toLocaleString()} evaluations · {job.feasible_evaluations.toLocaleString()} feasible
                    </div>
                    {job.error && <ErrorBox error={job.error} />}
                  </div>
                ) : <p className="text-sm text-muted-foreground">No run in this session. Configure the solver and press Run optimizer.</p>}
              </Panel>

              {r && (
                <>
                  <div className="rounded-md border-2 border-st-warning bg-st-warning/10 p-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-sm font-bold tracking-wide text-st-warning">{job?.advisory}</span>
                      <ToneChip tone={job?.recommendation_status === "ACCEPTED" ? "normal" : job?.recommendation_status === "REJECTED" ? "ood" : "warning"}>
                        {humanize(job?.recommendation_status ?? "")}
                      </ToneChip>
                      <PlanStatus plan={r} />
                    </div>
                    {job?.recommendation_status === "PENDING_REVIEW" && (
                      <div className="mt-3 flex flex-wrap items-end gap-2">
                        <div className="grid min-w-64 flex-1 gap-1">
                          <Label htmlFor="note" className="text-xs">Operator note (recorded in audit)</Label>
                          <Input id="note" value={note} onChange={(e) => setNote(e.target.value)} className="h-8" maxLength={500} />
                        </div>
                        <ConfirmAction trigger={<><Check className="size-4" aria-hidden /> Accept plan</>} title="Accept advisory plan?"
                          description="This records your acceptance in the session audit ledger. No vessel or engine commands are sent; execution remains with the master and fleet superintendent."
                          confirmLabel="Record acceptance" onConfirm={() => decide("ACCEPT")} />
                        <ConfirmAction variant="destructive" trigger={<><X className="size-4" aria-hidden /> Reject plan</>} title="Reject advisory plan?"
                          description="This records your rejection in the session audit ledger." confirmLabel="Record rejection" onConfirm={() => decide("REJECT")} />
                      </div>
                    )}
                  </div>

                  <Panel title="Objective vector" subtitle={<>Best solution found by {humanize(job?.params.algorithm)} <ProvenanceTag kind="MODEL" /></>}>
                    {r.objectives ? (
                      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
                        <Kpi label="Fuel" value={r.objectives.fuel_t} digits={2} unit={UNITS.mass} />
                        <Kpi label="Operational cost" value={fmtUsd(r.objectives.opex_usd)} unit={UNITS.currency} />
                        <Kpi label="Lifecycle WtW GHG" value={r.objectives.wtw_tco2e} digits={2} unit={UNITS.ghg} />
                        <Kpi label="Schedule delay" value={r.objectives.delay_h} digits={2} unit={UNITS.hours} />
                        <Kpi label="CVaR risk (CVaR₀.₈ − E[loss], normalized)" value={fmt(r.objectives.risk_cvar_excess, 4)} />
                      </div>
                    ) : <p className="text-sm text-st-ood">Not simulated: the plan violates a hard constraint, so the evaluator produced no objective vector.</p>}
                  </Panel>

                  <Panel title="Selected plan — decision variables">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Vessel</TableHead><TableHead>Assigned demand</TableHead>
                          <TableHead className="text-right">Cargo ({UNITS.mass})</TableHead><TableHead className="text-right">Speed ({UNITS.speed})</TableHead>
                          <TableHead>Fuel</TableHead><TableHead>Shore power</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {r.vessels.map((pv) => (
                          <TableRow key={pv.vessel_id}>
                            <TableCell className="font-semibold">{pv.vessel_id}</TableCell>
                            <TableCell>{pv.assigned_demand ?? "—"}</TableCell>
                            <TableCell className="num text-right">{fmt(pv.cargo_tonnes, 0)}</TableCell>
                            <TableCell className="num text-right">{fmt(pv.speed_kn, 1)}</TableCell>
                            <TableCell className="uppercase">{humanize(pv.fuel)}</TableCell>
                            <TableCell>{pv.shore_power == null ? "—" : pv.shore_power ? "YES" : "NO"}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {r.hard_violations.length > 0 && (
                      <div className="mt-3 rounded-md border border-st-fallback bg-st-fallback/10 p-2 text-sm">
                        <div className="font-semibold text-st-fallback">Hard constraint violations</div>
                        <ul className="list-inside list-disc text-xs">{r.hard_violations.map((h) => <li key={h}>{h}</li>)}</ul>
                      </div>
                    )}
                    <p className="mt-2 text-xs text-muted-foreground">{fmt(r.evaluations, 0)} evaluations · {fmt(r.runtime_s, 2)} s runtime</p>
                  </Panel>
                </>
              )}

              <Panel title="Fleet & demands" subtitle={<>Demands <ProvenanceTag kind="ASSUMED" title="SYNTHETIC_OPERATIONAL_SCENARIO" /> synthetic operational scenario</>}>
                <div className="grid gap-3 lg:grid-cols-2">
                  <dl>
                    {c.vessels.map((v) => (
                      <Field key={v.vessel_id} label={`${v.vessel_id} (${humanize(v.class_family)})`}
                        value={`${fmt(v.min_speed_knots, 0)}–${fmt(v.max_speed_knots, 0)} ${UNITS.speed} · DWT ${fmt(v.deadweight_tonnes, 0)} t`} />
                    ))}
                  </dl>
                  <dl>
                    {c.demands.map((d) => (
                      <Field key={d.demand_id} label={`${d.demand_id}: ${d.origin} → ${d.destination}`}
                        value={`${fmt(d.distance_nm, 0)} ${UNITS.distance} · ${fmt(d.cargo_quantity_tonnes, 0)} t · ≤${fmt(d.deadline_hours, 0)} ${UNITS.hours}`} />
                    ))}
                  </dl>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">Decision variables per vessel: {c.decision_variables_per_vessel.join(", ")}.</p>
              </Panel>
              {!job && <Notice title="Human-in-the-loop">Every recommendation starts as PENDING REVIEW and must be accepted or rejected by an operator.</Notice>}
            </div>
          </div>
        )}
      </DataState>
    </>
  );
}
