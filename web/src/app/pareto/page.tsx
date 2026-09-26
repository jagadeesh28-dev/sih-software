"use client";

import { useState } from "react";
import { ParetoChart } from "@/components/hmi/charts";
import { DataState, ErrorBox, Field, Loading, Notice, PageHeader, Panel, ProvenanceTag, ToneChip } from "@/components/hmi/primitives";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Resolve } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

export default function ParetoPage() {
  const pareto = useApi(api.pareto, []);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<Resolve>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  const select = async (id: string) => {
    setSelected(id); setDetail(undefined); setError(undefined); setBusy(true);
    try { setDetail(await api.resolvePareto(id)); } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  };

  return (
    <>
      <PageHeader title="Pareto / Trade-offs"
        description="Non-dominated, feasible and penalty-free stored optimizer solutions plotted as operational cost against lifecycle well-to-wake GHG. Duplicate objective vectors are removed; no point is labelled best because no single decision criterion is defined." />
      <DataState state={pareto} empty={(p) => p.points.length === 0}>
        {(p) => (
          <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_400px]">
            <div className="grid content-start gap-3">
              <Panel title="Cost vs lifecycle GHG" subtitle={<><ProvenanceTag kind="STORED" /> {p.source} · {p.points.length} non-dominated penalty-free points from {p.archived_rows} stored rows</>}>
                <p className="text-sm font-medium">{p.summary}</p>
                <ParetoChart points={p.points} selected={selected} onSelect={select} />
                <p className="text-xs text-muted-foreground">Select a point (click, or use the table below) to recover its decision variables.</p>
              </Panel>
              <Panel title="Solutions">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead><TableHead>Formulation</TableHead><TableHead>Algorithm / seed</TableHead>
                      <TableHead className="text-right">Fuel ({UNITS.mass})</TableHead><TableHead className="text-right">Cost ({UNITS.currency})</TableHead>
                      <TableHead className="text-right">WtW ({UNITS.ghg})</TableHead><TableHead className="text-right">Delay ({UNITS.hours})</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {p.points.map((pt) => (
                      <TableRow key={pt.solution_id} className={cn("cursor-pointer", pt.solution_id === selected && "bg-accent")}
                        tabIndex={0} aria-selected={pt.solution_id === selected}
                        onClick={() => select(pt.solution_id)} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && select(pt.solution_id)}>
                        <TableCell className="font-semibold">{pt.solution_id}</TableCell>
                        <TableCell className="text-xs">{humanize(pt.formulation)}</TableCell>
                        <TableCell className="text-xs">{pt.algorithm} / {pt.seed}</TableCell>
                        <TableCell className="num text-right">{fmt(pt.fuel_tonnes, 2)}</TableCell>
                        <TableCell className="num text-right">{fmtUsd(pt.cost_usd)}</TableCell>
                        <TableCell className="num text-right">{fmt(pt.ghg_tonnes, 2)}</TableCell>
                        <TableCell className="num text-right">{fmt(pt.delay_hours, 1)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Panel>
              <Notice title="Selection rule">{p.note}</Notice>
            </div>

            <Panel title={selected ? `Solution ${selected}` : "Solution detail"} className="content-start">
              {!selected && <p className="text-sm text-muted-foreground">No solution selected.</p>}
              {busy && <Loading label="Re-evaluating the stored decision vector…" />}
              {error && <ErrorBox error={error} onRetry={() => selected && select(selected)} />}
              {detail && (
                <div className="grid gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    {detail.reproduced
                      ? <ToneChip tone="normal">REPRODUCED — objectives match archive</ToneChip>
                      : <ToneChip tone="ood">NOT REPRODUCED — objectives differ from archive</ToneChip>}
                  </div>
                  <dl>
                    <Field label="Formulation" value={humanize(detail.solution.formulation)} />
                    <Field label="Algorithm / seed / budget" value={`${detail.solution.algorithm} / ${detail.solution.seed} / ${detail.solution.evaluations}`} />
                    <Field label="Operational cost" value={fmtUsd(detail.solution.cost_usd)} unit={UNITS.currency} />
                    <Field label="Lifecycle WtW GHG" value={fmt(detail.solution.ghg_tonnes, 2)} unit={UNITS.ghg} />
                    <Field label="Fuel" value={fmt(detail.solution.fuel_tonnes, 2)} unit={UNITS.mass} />
                    <Field label="Schedule delay" value={fmt(detail.solution.delay_hours, 2)} unit={UNITS.hours} />
                  </dl>
                  <div>
                    <div className="mb-1 text-[11px] uppercase tracking-wider text-muted-foreground">Decision variables (stored vector, re-evaluated)</div>
                    <Table>
                      <TableHeader>
                        <TableRow><TableHead>Vessel</TableHead><TableHead>Demand</TableHead><TableHead className="text-right">Cargo t</TableHead><TableHead className="text-right">Speed kn</TableHead><TableHead>Fuel</TableHead><TableHead>Shore</TableHead></TableRow>
                      </TableHeader>
                      <TableBody>
                        {detail.rerun.vessels.map((v) => (
                          <TableRow key={v.vessel_id}>
                            <TableCell className="text-xs font-semibold">{v.vessel_id}</TableCell>
                            <TableCell className="text-xs">{v.assigned_demand}</TableCell>
                            <TableCell className="num text-right">{fmt(v.cargo_tonnes, 0)}</TableCell>
                            <TableCell className="num text-right">{fmt(v.speed_kn, 1)}</TableCell>
                            <TableCell className="text-xs uppercase">{humanize(v.fuel)}</TableCell>
                            <TableCell className="text-xs">{v.shore_power ? "YES" : "NO"}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <p className="text-xs text-muted-foreground">{detail.note}</p>
                </div>
              )}
            </Panel>
          </div>
        )}
      </DataState>
    </>
  );
}
