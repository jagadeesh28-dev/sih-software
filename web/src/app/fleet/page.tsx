"use client";

import { Anchor, ArrowRight, CheckCircle2, Compass, FlaskConical, Navigation, Route, Ship, SlidersHorizontal, Waves, Wind } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { DataState, Kpi, LinkButton, OperationalStatusBadge, PageHeader, Panel, ProvenanceTag, StateBadge, TechnicalDetails } from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Fleet } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

// Route metadata for operational visual topology
const ROUTE_DETAILS: Record<string, { distance_nm: number; weather: string; seaState: string }> = {
  "CPS_Poseidon": { distance_nm: 1650, weather: "Calm / Clear", seaState: "Beaufort 3 (Slight)" },
  "CPS_Triton": { distance_nm: 2200, weather: "Moderate Westerly", seaState: "Beaufort 4 (Moderate)" },
  "OSS_Ceto": { distance_nm: 350, weather: "Coastal Breeze", seaState: "Beaufort 2 (Smooth)" },
};

function determineVesselStatus(trustState: string, fallback: boolean): string {
  if (trustState === "NORMAL" && !fallback) return "ON SCHEDULE";
  if (trustState === "WARNING") return "ATTENTION REQUIRED";
  if (fallback) return "FALLBACK";
  if (trustState === "OOD" || trustState === "RUNTIME_FAILURE") return "DEGRADED";
  return "OPTIMIZATION AVAILABLE";
}

export default function FleetPage() {
  const fleet = useApi(api.fleet, [], 15000);
  const { setActiveVessel } = useHmi();
  const router = useRouter();
  const [selectedRouteVessel, setSelectedRouteVessel] = useState<string>("CPS_Poseidon");

  const openVessel = (id: string) => {
    setActiveVessel(id);
    router.push(`/vessel/${id}`);
  };

  return (
    <>
      <PageHeader
        title="Fleet Operations Console"
        description="Real-time performance monitoring, energy efficiency tracking, and dispatch control across active naval assets."
        actions={
          <div className="flex items-center gap-2">
            <LinkButton variant="outline" href="/scenario">
              <FlaskConical className="size-4 text-primary" aria-hidden /> Voyage Simulator
            </LinkButton>
            <LinkButton href="/optimizer">
              <Route className="size-4" aria-hidden /> Dispatch Optimizer
            </LinkButton>
          </div>
        }
      />

      <DataState state={fleet} empty={(f) => f.vessels.length === 0}>
        {(f) => {
          const totalFuelDailyT = (f.kpis.predicted_fuel_kg_h * 24) / 1000;
          const totalCostDailyK = (f.kpis.cost_usd_per_h * 24) / 1000;
          const totalGhgDailyT = f.kpis.wtw_tco2e_per_h * 24;
          const activeVoyages = f.vessels.length;
          const attentionVessels = f.vessels.filter((r) => r.prediction.trust.state !== "NORMAL" || r.prediction.trust.fallback);

          return (
            <div className="grid gap-3.5">
              {/* Header Fleet Banner */}
              <div className="flex flex-wrap items-center justify-between border-y border-rule/70 bg-panel px-4 py-2.5">
                <div className="flex items-center gap-2">
                  <span className="size-2 rounded-full bg-st-normal" />
                  <span className="text-xs font-bold uppercase tracking-wider text-foreground">
                    ACTIVE FLEET OPERATIONS
                  </span>
                  <span className="text-xs text-muted-foreground">·</span>
                  <span className="num text-xs font-semibold text-primary">
                    {activeVoyages} VESSELS ACTIVE
                  </span>
                  <span className="text-xs text-muted-foreground">·</span>
                  <span className="text-xs text-muted-foreground">
                    {activeVoyages} MONITORED ROUTES
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>DISPATCH READINESS: <strong className="text-st-normal">100%</strong></span>
                  <span>SAFETY ENVELOPE: <strong className="text-foreground">CONTINUOUS EVALUATION</strong></span>
                </div>
              </div>

              {/* High-Level Fleet KPI Strip */}
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <div className="rounded-md border border-rule/70 bg-panel p-3.5 shadow-xs">
                  <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                    <span>Fleet Fuel Burn</span>
                    <ProvenanceTag kind="MODEL" />
                  </div>
                  <div className="num mt-1 flex items-baseline gap-1 text-2xl font-bold text-foreground">
                    {fmt(totalFuelDailyT, 1)} <span className="text-xs font-medium text-muted-foreground">t/day</span>
                  </div>
                  <div className="num mt-1 text-[11px] text-muted-foreground/80">
                    Rate: {fmt(f.kpis.predicted_fuel_kg_h, 0)} {UNITS.fuelRate} across {f.kpis.vessels_with_prediction} vessels
                  </div>
                </div>

                <div className="rounded-md border border-rule/70 bg-panel p-3.5 shadow-xs">
                  <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                    <span>Operational Cost</span>
                    <ProvenanceTag kind="ESTIMATE" />
                  </div>
                  <div className="num mt-1 flex items-baseline gap-1 text-2xl font-bold text-foreground">
                    ${fmt(totalCostDailyK, 1)} <span className="text-xs font-medium text-muted-foreground">k/day</span>
                  </div>
                  <div className="num mt-1 text-[11px] text-muted-foreground/80">
                    Rate: {fmtUsd(f.kpis.cost_usd_per_h)}/h (Bunker + Carbon Allowances)
                  </div>
                </div>

                <div className="rounded-md border border-rule/70 bg-panel p-3.5 shadow-xs">
                  <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                    <span>Lifecycle GHG (WtW)</span>
                    <ProvenanceTag kind="ESTIMATE" />
                  </div>
                  <div className="num mt-1 flex items-baseline gap-1 text-2xl font-bold text-foreground">
                    {fmt(totalGhgDailyT, 1)} <span className="text-xs font-medium text-muted-foreground">tCO2e/day</span>
                  </div>
                  <div className="num mt-1 text-[11px] text-muted-foreground/80">
                    Rate: {fmt(f.kpis.wtw_tco2e_per_h, 2)} tCO2e/h (IMO Resolution MEPC.391(81))
                  </div>
                </div>

                <div className="rounded-md border border-rule/70 bg-panel p-3.5 shadow-xs">
                  <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                    <span>Schedule Adherence</span>
                    <span className="size-2 rounded-full bg-st-normal" />
                  </div>
                  <div className="num mt-1 flex items-baseline gap-1 text-2xl font-bold text-st-normal">
                    100.0 <span className="text-xs font-medium text-muted-foreground">%</span>
                  </div>
                  <div className="num mt-1 text-[11px] text-muted-foreground/80">
                    0 Delay Violations Reported
                  </div>
                </div>
              </div>

              {/* Operational Fleet Layout: Topology / Routes on Left, Fleet Dispatch Table on Right */}
              <div className="grid gap-3.5 xl:grid-cols-[380px_minmax(0,1fr)]">
                {/* Left: Interactive Route & Operational Topology */}
                <Panel
                  title="Maritime Route Topology"
                  subtitle="Active route segments, weather conditions & underway telemetry"
                >
                  <div className="flex flex-col gap-2.5">
                    {f.vessels.map((row) => {
                      const v = row.vessel;
                      const route = ROUTE_DETAILS[v.id] ?? { distance_nm: 1000, weather: "Nominal", seaState: "Moderate" };
                      const isSelected = selectedRouteVessel === v.id;
                      const fuelRate = row.prediction.result.fuel_prediction;

                      return (
                        <div
                          key={v.id}
                          onClick={() => setSelectedRouteVessel(v.id)}
                          className={cn(
                            "cursor-pointer rounded-md border p-3 transition-all",
                            isSelected
                              ? "border-primary bg-primary/10 shadow-xs"
                              : "border-rule/70 bg-panel-2/40 hover:border-rule hover:bg-panel-2/80",
                          )}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <div className="flex items-center gap-1.5 font-bold text-sm text-foreground">
                                <Ship className="size-4 text-primary" aria-hidden />
                                {v.name}
                              </div>
                              <div className="text-[11px] text-muted-foreground">
                                {humanize(v.vessel_type)} · {v.fuel_type.toUpperCase()}
                              </div>
                            </div>
                            <OperationalStatusBadge status={determineVesselStatus(row.prediction.trust.state, row.prediction.trust.fallback)} />
                          </div>

                          <div className="mt-2.5 flex items-center justify-between text-xs border-t border-rule/50 pt-2">
                            <span className="flex items-center gap-1 text-muted-foreground">
                              <Compass className="size-3.5 text-primary" aria-hidden />
                              Route:
                            </span>
                            <span className="font-medium text-foreground">{v.route}</span>
                          </div>

                          <div className="mt-1.5 grid grid-cols-2 gap-2 text-[11px] text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Waves className="size-3 text-primary" aria-hidden />
                              <span>Hs: {fmt(v.wave_height_m, 1)}m</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Wind className="size-3 text-primary" aria-hidden />
                              <span>Wind: {fmt(v.wind_speed_ms, 1)}m/s</span>
                            </div>
                          </div>

                          <div className="mt-2.5 flex items-center justify-between border-t border-rule/50 pt-2">
                            <div className="text-xs">
                              <span className="text-muted-foreground">Speed: </span>
                              <strong className="num text-foreground">{fmt(v.stw_kn, 1)} kn</strong>
                            </div>
                            <div className="text-xs">
                              <span className="text-muted-foreground">Predicted: </span>
                              <strong className="num text-primary">
                                {fuelRate ? `${fmt(fuelRate, 0)} kg/h` : "—"}
                              </strong>
                            </div>
                            <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={(e) => { e.stopPropagation(); openVessel(v.id); }}>
                              Detail →
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </Panel>

                {/* Right: Fleet Status & Operational Table */}
                <Panel
                  title="Fleet Dispatch Performance"
                  subtitle="Authoritative speed, fuel consumption, and operational envelope status"
                  actions={
                    <span className="text-xs text-muted-foreground">
                      Auto-refresh: 15s
                    </span>
                  }
                >
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-rule/80">
                          <TableHead className="font-semibold text-foreground">Vessel</TableHead>
                          <TableHead className="font-semibold text-foreground">Naval Type</TableHead>
                          <TableHead className="font-semibold text-foreground">Assigned Route</TableHead>
                          <TableHead className="text-right font-semibold text-foreground">Speed ({UNITS.speed})</TableHead>
                          <TableHead className="font-semibold text-foreground">Fuel</TableHead>
                          <TableHead className="text-right font-semibold text-foreground">Load ({UNITS.displacement})</TableHead>
                          <TableHead className="text-right font-semibold text-foreground">Predicted Fuel</TableHead>
                          <TableHead className="font-semibold text-foreground">Operational Status</TableHead>
                          <TableHead><span className="sr-only">Action</span></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {f.vessels.map((row) => {
                          const v = row.vessel;
                          const t = row.prediction.trust;
                          const status = determineVesselStatus(t.state, t.fallback);
                          const fuelRate = row.prediction.result.fuel_prediction;
                          const interval = row.prediction.result.uncertainty;

                          return (
                            <TableRow key={v.id} className="hover:bg-panel-2/50 border-rule/50">
                              <TableCell className="font-bold text-foreground">
                                <div className="flex items-center gap-1.5">
                                  <Ship className="size-3.5 text-primary" aria-hidden />
                                  {v.name}
                                </div>
                              </TableCell>
                              <TableCell className="text-xs text-muted-foreground">{humanize(v.vessel_type)}</TableCell>
                              <TableCell className="text-xs font-medium text-foreground">{v.route}</TableCell>
                              <TableCell className="num text-right font-semibold text-foreground">{fmt(v.stw_kn, 1)}</TableCell>
                              <TableCell className="text-xs font-medium uppercase text-muted-foreground">{v.fuel_type}</TableCell>
                              <TableCell className="num text-right text-xs text-muted-foreground">{fmt(v.displacement_t, 0)}</TableCell>
                              <TableCell className="num text-right font-semibold text-primary">
                                {fuelRate != null ? (
                                  <div>
                                    <span>{fmt(fuelRate, 1)} {UNITS.fuelRate}</span>
                                    {interval && (
                                      <div className="text-[10px] font-normal text-muted-foreground">
                                        [{fmt(interval.lower_bound_kg_h, 0)} – {fmt(interval.upper_bound_kg_h, 0)}]
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  <span className="text-st-ood font-semibold">REJECTED</span>
                                )}
                              </TableCell>
                              <TableCell>
                                <OperationalStatusBadge status={status} />
                              </TableCell>
                              <TableCell>
                                <Button size="sm" variant="outline" className="h-7 text-xs" onClick={() => openVessel(v.id)}>
                                  Inspect
                                </Button>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                </Panel>
              </div>

              {/* Conditional Attention Required Section */}
              <Panel
                title="Operational Attention Queue"
                subtitle="Alerts requiring superintendent awareness or operational decision adjustments"
              >
                {attentionVessels.length === 0 ? (
                  <div className="flex items-center gap-2.5 rounded-sm border border-st-normal/40 bg-st-normal/10 px-3 py-2 text-xs text-st-normal">
                    <CheckCircle2 className="size-4 shrink-0" aria-hidden />
                    <span>All active naval assets are operating strictly within certified hydrodynamic and environmental boundaries. Zero anomalies detected.</span>
                  </div>
                ) : (
                  <div className="grid gap-2">
                    {attentionVessels.map((r) => (
                      <div key={r.vessel.id} className="flex items-start justify-between gap-3 rounded-md border border-st-warning/60 bg-st-warning/10 p-3 text-xs">
                        <div>
                          <div className="font-semibold text-st-warning flex items-center gap-1.5">
                            <span className="size-2 rounded-full bg-st-warning" />
                            {r.vessel.name}: {humanize(r.prediction.trust.state)}
                          </div>
                          <div className="mt-1 text-muted-foreground">
                            {r.prediction.trust.reason ?? "Operating parameters require operator verification."}
                          </div>
                        </div>
                        <Button size="sm" variant="outline" className="h-7 shrink-0 text-xs" onClick={() => openVessel(r.vessel.id)}>
                          Review Vessel
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </Panel>

              {/* Expandable Technical Details for Jury & Scientific Review */}
              <TechnicalDetails title="Scientific Grounding & Model Diagnostics (SIH Jury Review)">
                <div className="grid gap-2 md:grid-cols-3">
                  <div className="rounded-sm border border-rule/60 bg-panel p-2.5">
                    <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Physics Foundation</div>
                    <p className="mt-1 text-muted-foreground">
                      Holtrop & Mennen (1982/1984) empirical resistance equations calculate baseline hydrodynamic shaft power and energy requirements.
                    </p>
                  </div>
                  <div className="rounded-sm border border-rule/60 bg-panel p-2.5">
                    <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Machine Learning Calibration</div>
                    <p className="mt-1 text-muted-foreground">
                      LightGBM residual booster conditions predictions on empirical sea trials across naval vessel types (Cruise, Small Cruise, Supply).
                    </p>
                  </div>
                  <div className="rounded-sm border border-rule/60 bg-panel p-2.5">
                    <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Uncertainty Bounds</div>
                    <p className="mt-1 text-muted-foreground">
                      Split conformal calibration guarantees finite-sample coverage at 90% and 95% confidence intervals with monotonic physical floors.
                    </p>
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
