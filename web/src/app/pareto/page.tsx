"use client";

import { CheckCircle2, ChevronRight, Compass, GitCompare, Layers, Scale } from "lucide-react";
import { useState } from "react";
import { ParetoChart } from "@/components/hmi/charts";
import {
  DataState,
  ErrorBox,
  Field,
  Kpi,
  Loading,
  PageHeader,
  Panel,
  TechnicalDetails,
  ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Resolve } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

// Baseline reference for operational plan comparison
const BASELINE_PLAN = {
  fuel_t: 382.40,
  cost_usd: 286800,
  ghg_tco2e: 1223.68,
  delay_h: 0.0,
};

export default function ParetoPage() {
  const pareto = useApi(api.pareto, []);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<Resolve>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();
  const [showComparison, setShowComparison] = useState(false);

  const select = async (id: string) => {
    setSelected(id);
    setDetail(undefined);
    setError(undefined);
    setBusy(true);
    try {
      setDetail(await api.resolvePareto(id));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Multi-Objective Decision Space"
        badge={<ToneChip tone="normal">Pareto Optimal Frontier</ToneChip>}
        description="Interactive trade-off analysis between operational expenditure (OPEX) and lifecycle well-to-wake emissions (WtW GHG). Every plotted point represents a fully feasible, constraint-satisfying fleet dispatch plan."
      />

      <DataState state={pareto} empty={(p) => p.points.length === 0}>
        {(p) => {
          // Identify frontier extremes for operator orientation
          const minCost = [...p.points].sort((a, b) => a.cost_usd - b.cost_usd)[0];
          const minGhg = [...p.points].sort((a, b) => a.ghg_tonnes - b.ghg_tonnes)[0];
          const activeSolution = p.points.find((pt) => pt.solution_id === selected);

          return (
            <div className="grid gap-4">
              {/* Executive Decision Header Strip */}
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <Kpi
                  label="Non-Dominated Solutions"
                  value={p.points.length}
                  note={`Filtered from ${p.archived_rows} verified optimizer runs`}
                />
                <Kpi
                  label="Minimum Cost Frontier"
                  value={minCost ? fmtUsd(minCost.cost_usd) : "—"}
                  note={minCost ? `Solution ${minCost.solution_id} (${fmt(minCost.ghg_tonnes, 1)} tCO2e)` : undefined}
                />
                <Kpi
                  label="Minimum GHG Frontier"
                  value={minGhg ? fmt(minGhg.ghg_tonnes, 1) : "—"}
                  unit={UNITS.ghg}
                  note={minGhg ? `Solution ${minGhg.solution_id} (${fmtUsd(minGhg.cost_usd)})` : undefined}
                />
                <Kpi
                  label="Decision Guidance"
                  value="Trade-off Selection"
                  note="Select a plan below to inspect vessel setpoints"
                />
              </div>

              {/* Main Layout: Left = Chart + Table; Right = Solution Inspector */}
              <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_480px]">
                <div className="grid content-start gap-4">
                  {/* Pareto Frontier Scatter Chart */}
                  <Panel
                    title="Fleet OPEX vs. Lifecycle GHG Trade-off Frontier"
                    subtitle="Interactive scatter plot · Click any diamond to load full vessel speed & bunker configuration"
                  >
                    <ParetoChart points={p.points} selected={selected} onSelect={select} />
                    <div className="mt-2 flex flex-wrap items-center justify-between text-xs text-muted-foreground">
                      <span>X-Axis: Operational Cost (Bunkers + Carbon EU ETS + Shore Power)</span>
                      <span>Y-Axis: Well-to-Wake Lifecycle GHG (tCO2e)</span>
                    </div>
                  </Panel>

                  {/* Available Solutions Table */}
                  <Panel
                    title="Verified Trade-off Candidates"
                    subtitle="Non-dominated solutions ordered by operational profile"
                  >
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-24">Plan ID</TableHead>
                          <TableHead>Optimization Target</TableHead>
                          <TableHead className="text-right">Fuel ({UNITS.mass})</TableHead>
                          <TableHead className="text-right">Cost ({UNITS.currency})</TableHead>
                          <TableHead className="text-right">WtW GHG ({UNITS.ghg})</TableHead>
                          <TableHead className="text-right">Delay ({UNITS.hours})</TableHead>
                          <TableHead className="w-20 text-center">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {p.points.map((pt) => {
                          const isSel = pt.solution_id === selected;
                          return (
                            <TableRow
                              key={pt.solution_id}
                              className={cn("cursor-pointer transition-colors", isSel && "bg-cyan-950/40 border-l-2 border-cyan-500")}
                              tabIndex={0}
                              aria-selected={isSel}
                              onClick={() => select(pt.solution_id)}
                              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && select(pt.solution_id)}
                            >
                              <TableCell className="font-semibold text-cyan-300">
                                <div>#{pt.solution_id}</div>
                                <span className="text-[10px] text-muted-foreground uppercase font-mono font-normal">
                                  OPTION {String.fromCharCode(65 + p.points.indexOf(pt))}
                                </span>
                              </TableCell>
                              <TableCell className="text-xs">
                                <div className="font-medium text-foreground">
                                  {pt.solution_id === minCost?.solution_id
                                    ? "Lower-Cost Candidate"
                                    : pt.solution_id === minGhg?.solution_id
                                    ? "Lower-GHG Candidate"
                                    : pt.delay_hours === 0
                                    ? "Schedule-Priority Option"
                                    : "Balanced Trade-Off Candidate"}
                                </div>
                                <div className="text-[10px] text-muted-foreground mt-0.5">{humanize(pt.formulation)}</div>
                              </TableCell>
                              <TableCell className="num text-right font-mono">{fmt(pt.fuel_tonnes, 2)}</TableCell>
                              <TableCell className="num text-right font-mono text-cyan-200">{fmtUsd(pt.cost_usd)}</TableCell>
                              <TableCell className="num text-right font-mono text-emerald-300">{fmt(pt.ghg_tonnes, 2)}</TableCell>
                              <TableCell className="num text-right font-mono">{fmt(pt.delay_hours, 1)}</TableCell>
                              <TableCell className="text-center">
                                <Button
                                  size="sm"
                                  variant={isSel ? "default" : "ghost"}
                                  className="h-7 px-2 text-xs"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    select(pt.solution_id);
                                  }}
                                >
                                  {isSel ? "Active" : "Inspect"}
                                </Button>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </Panel>
                </div>

                {/* Right Column: Solution Inspector */}
                <div className="grid content-start gap-4">
                  <Panel
                    title={selected ? `Dispatch Plan #${selected}` : "Dispatch Plan Inspector"}
                    subtitle={selected ? "Vessel setpoints and objective comparison" : "Select a point on the chart to inspect"}
                  >
                    {!selected && (
                      <div className="py-12 text-center text-sm text-muted-foreground">
                        <Compass className="mx-auto mb-2 size-8 opacity-40" />
                        <p>No plan currently selected.</p>
                        <p className="text-xs mt-1">Click any solution diamond on the chart or select a row in the table.</p>
                      </div>
                    )}

                    {busy && <Loading label="Re-evaluating verified dispatch vector..." />}
                    {error && <ErrorBox error={error} onRetry={() => selected && select(selected)} />}

                    {detail && (
                      <div className="grid gap-4">
                        {/* Summary Metrics of Selected Plan */}
                        <div className="grid grid-cols-2 gap-2 rounded-md border border-panel-border bg-panel-2/60 p-3">
                          <div>
                            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Operating Cost</div>
                            <div className="text-lg font-bold text-cyan-300">{fmtUsd(detail.solution.cost_usd)}</div>
                          </div>
                          <div>
                            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Lifecycle GHG</div>
                            <div className="text-lg font-bold text-emerald-300">{fmt(detail.solution.ghg_tonnes, 2)} <span className="text-xs font-normal">tCO2e</span></div>
                          </div>
                          <div className="mt-2">
                            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Bunker Fuel</div>
                            <div className="text-sm font-semibold">{fmt(detail.solution.fuel_tonnes, 2)} <span className="text-xs font-normal">tonnes</span></div>
                          </div>
                          <div className="mt-2">
                            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Schedule Delay</div>
                            <div className="text-sm font-semibold">{fmt(detail.solution.delay_hours, 1)} <span className="text-xs font-normal">hours</span></div>
                          </div>
                        </div>

                        {/* Comparison against Baseline Plan */}
                        <div className="rounded-md border border-panel-border bg-panel-1 p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                              <GitCompare className="size-3.5 text-cyan-400" /> Variance vs. Baseline Fleet Plan
                            </span>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 text-[11px] px-1.5"
                              onClick={() => setShowComparison(!showComparison)}
                            >
                              {showComparison ? "Hide Details" : "Show Full Table"}
                            </Button>
                          </div>

                          {(() => {
                            const costDelta = detail.solution.cost_usd - BASELINE_PLAN.cost_usd;
                            const costPct = (costDelta / BASELINE_PLAN.cost_usd) * 100;
                            const ghgDelta = detail.solution.ghg_tonnes - BASELINE_PLAN.ghg_tco2e;
                            const ghgPct = (ghgDelta / BASELINE_PLAN.ghg_tco2e) * 100;
                            const fuelDelta = detail.solution.fuel_tonnes - BASELINE_PLAN.fuel_t;
                            const fuelPct = (fuelDelta / BASELINE_PLAN.fuel_t) * 100;

                            return (
                              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                                <div className="rounded bg-panel-2/80 p-2">
                                  <div className="text-[10px] text-muted-foreground">Fuel Variance</div>
                                  <div className={cn("font-mono font-semibold", fuelDelta <= 0 ? "text-emerald-400" : "text-amber-400")}>
                                    {fuelDelta <= 0 ? "" : "+"}{fmt(fuelDelta, 1)} t ({fmt(fuelPct, 1)}%)
                                  </div>
                                </div>
                                <div className="rounded bg-panel-2/80 p-2">
                                  <div className="text-[10px] text-muted-foreground">Cost Variance</div>
                                  <div className={cn("font-mono font-semibold", costDelta <= 0 ? "text-emerald-400" : "text-amber-400")}>
                                    {costDelta <= 0 ? "" : "+"}{fmtUsd(costDelta)} ({fmt(costPct, 1)}%)
                                  </div>
                                </div>
                                <div className="rounded bg-panel-2/80 p-2">
                                  <div className="text-[10px] text-muted-foreground">GHG Variance</div>
                                  <div className={cn("font-mono font-semibold", ghgDelta <= 0 ? "text-emerald-400" : "text-amber-400")}>
                                    {ghgDelta <= 0 ? "" : "+"}{fmt(ghgDelta, 1)} t ({fmt(ghgPct, 1)}%)
                                  </div>
                                </div>
                              </div>
                            );
                          })()}

                          {showComparison && (
                            <table className="mt-3 w-full text-xs border-t pt-2">
                              <thead>
                                <tr className="text-muted-foreground text-[10px] uppercase text-left">
                                  <th className="py-1">Metric</th>
                                  <th className="text-right">Baseline</th>
                                  <th className="text-right">Plan #{selected}</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-panel-border/50">
                                <tr>
                                  <td className="py-1 text-muted-foreground">Fuel Consumption</td>
                                  <td className="text-right font-mono">{fmt(BASELINE_PLAN.fuel_t, 1)} t</td>
                                  <td className="text-right font-mono font-semibold">{fmt(detail.solution.fuel_tonnes, 1)} t</td>
                                </tr>
                                <tr>
                                  <td className="py-1 text-muted-foreground">Operational Cost</td>
                                  <td className="text-right font-mono">{fmtUsd(BASELINE_PLAN.cost_usd)}</td>
                                  <td className="text-right font-mono font-semibold">{fmtUsd(detail.solution.cost_usd)}</td>
                                </tr>
                                <tr>
                                  <td className="py-1 text-muted-foreground">Lifecycle WtW GHG</td>
                                  <td className="text-right font-mono">{fmt(BASELINE_PLAN.ghg_tco2e, 1)} t</td>
                                  <td className="text-right font-mono font-semibold">{fmt(detail.solution.ghg_tonnes, 1)} t</td>
                                </tr>
                                <tr>
                                  <td className="py-1 text-muted-foreground">Schedule Delay</td>
                                  <td className="text-right font-mono">{fmt(BASELINE_PLAN.delay_h, 1)} h</td>
                                  <td className="text-right font-mono font-semibold">{fmt(detail.solution.delay_hours, 1)} h</td>
                                </tr>
                              </tbody>
                            </table>
                          )}
                        </div>

                        {/* Fleet Dispatch Allocation Table */}
                        <div>
                          <div className="mb-2 text-[11px] uppercase tracking-wider text-muted-foreground font-medium flex items-center justify-between">
                            <span>Vessel Speed & Bunker Allocation</span>
                            <span className="text-[10px] text-muted-foreground">{detail.rerun.vessels.length} vessels assigned</span>
                          </div>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead className="py-1 text-xs">Vessel</TableHead>
                                <TableHead className="py-1 text-xs">Route</TableHead>
                                <TableHead className="py-1 text-right text-xs">Speed</TableHead>
                                <TableHead className="py-1 text-xs">Fuel</TableHead>
                                <TableHead className="py-1 text-center text-xs">Shore Pwr</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {detail.rerun.vessels.map((v) => (
                                <TableRow key={v.vessel_id}>
                                  <TableCell className="py-1.5 text-xs font-semibold text-foreground">
                                    {v.vessel_id}
                                  </TableCell>
                                  <TableCell className="py-1.5 text-xs text-muted-foreground">
                                    {v.assigned_demand}
                                  </TableCell>
                                  <TableCell className="py-1.5 num text-right text-xs font-mono">
                                    {fmt(v.speed_kn, 1)} kn
                                  </TableCell>
                                  <TableCell className="py-1.5 text-xs uppercase font-medium">
                                    {humanize(v.fuel)}
                                  </TableCell>
                                  <TableCell className="py-1.5 text-center text-xs">
                                    {v.shore_power ? (
                                      <span className="inline-flex items-center text-emerald-400 text-[11px] font-semibold">
                                        YES
                                      </span>
                                    ) : (
                                      <span className="text-muted-foreground text-[11px]">NO</span>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>

                        {/* Operator Action Strip */}
                        <div className="flex items-center gap-2 pt-2 border-t">
                          <Button className="w-full h-8 text-xs font-semibold">
                            <CheckCircle2 className="size-3.5 mr-1 text-emerald-400" /> Apply Dispatch Recommendation
                          </Button>
                        </div>

                        {/* Collapsible Scientific / Mathematical Details Drawer */}
                        <TechnicalDetails title="Optimizer Vector & Scientific Reproduction">
                          <dl className="grid grid-cols-2 gap-2 text-xs">
                            <Field label="Optimization Target" value={humanize(detail.solution.formulation)} />
                            <Field
                              label="Algorithm & Seed"
                              value={`${detail.solution.algorithm} (Seed: ${detail.solution.seed})`}
                            />
                            <Field label="Evaluations Budget" value={detail.solution.evaluations.toLocaleString()} />
                            <Field
                              label="Archive Verification"
                              value={
                                detail.reproduced ? (
                                  <span className="text-emerald-400 font-medium">Verified Exact Match</span>
                                ) : (
                                  <span className="text-amber-400 font-medium">Discrepancy Detected</span>
                                )
                              }
                            />
                          </dl>
                          <p className="mt-2 text-[11px] text-muted-foreground leading-relaxed">
                            {detail.note}
                          </p>
                        </TechnicalDetails>
                      </div>
                    )}
                  </Panel>
                </div>
              </div>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
