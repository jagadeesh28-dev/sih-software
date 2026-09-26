"use client";

import { FlaskConical, Route, Ship } from "lucide-react";
import { useRouter } from "next/navigation";
import { useHmi } from "@/components/hmi/app-shell";
import { DataState, Kpi, LinkButton, Notice, PageHeader, Panel, ProvenanceTag, StateBadge, ToneChip } from "@/components/hmi/primitives";
import { PredictionReadout } from "@/components/hmi/prediction-view";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Fleet } from "@/lib/api";
import { fmt, fmtTime, fmtUsd, humanize, STATE_META, asHmiState, UNITS, useApi } from "@/lib/hmi";

function fleetAlerts(f: Fleet) {
  const out: { vessel: string; state: string; reason: string }[] = [];
  for (const row of f.vessels) {
    const t = row.prediction.trust;
    if (t.state !== "NORMAL") out.push({ vessel: row.vessel.id, state: t.state, reason: t.reason ?? STATE_META[asHmiState(t.state)].explanation });
    if (t.fallback) out.push({ vessel: row.vessel.id, state: "FALLBACK", reason: t.fallback_label ?? "" });
    if (t.missing_factors.length) out.push({ vessel: row.vessel.id, state: "MISSING_FACTOR", reason: `Defaulted: ${t.missing_factors.join(", ")}` });
  }
  return out.sort((a, b) => STATE_META[asHmiState(b.state)].severity - STATE_META[asHmiState(a.state)].severity);
}

export default function FleetPage() {
  const fleet = useApi(api.fleet, [], 30000);
  const { setActiveVessel } = useHmi();
  const router = useRouter();
  const open = (id: string) => { setActiveVessel(id); router.push(`/vessel/${id}`); };

  return (
    <>
      <PageHeader
        title="Fleet Overview"
        description="Current operating state of each vessel evaluated by the production predictor. Vessel states are fleet defaults (no live telemetry feed is connected)."
        actions={
          <>
            <LinkButton variant="outline" href="/scenario"><FlaskConical className="size-4" aria-hidden /> Run Scenario</LinkButton>
            <LinkButton href="/optimizer"><Route className="size-4" aria-hidden /> Optimize Fleet</LinkButton>
          </>
        }
      />
      <DataState state={fleet} empty={(f) => f.vessels.length === 0}>
        {(f) => {
          const alerts = fleetAlerts(f);
          return (
            <div className="grid gap-3">
              <Panel title="Fleet KPIs" subtitle={`Evaluated ${fmtTime(f.generated_at)}`}>
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
                  <Kpi label="Predicted fuel" value={f.kpis.predicted_fuel_kg_h} unit={UNITS.fuelRate} emphasis
                    tag={<ProvenanceTag kind="MODEL" />} note={`${f.kpis.vessels_with_prediction} of ${f.kpis.vessels} vessels served`} />
                  <Kpi label="Operational cost" value={fmtUsd(f.kpis.cost_usd_per_h)} unit={`${UNITS.currency}/h`}
                    tag={<ProvenanceTag kind="ESTIMATE" title="Configured prices, 1 operating hour" />} note="Configured VLSFO + carbon price" />
                  <Kpi label="Lifecycle GHG (WtW)" value={f.kpis.wtw_tco2e_per_h} digits={2} unit={`${UNITS.ghg}/h`}
                    tag={<ProvenanceTag kind="ESTIMATE" />} note="IMO MEPC.391(81) factors (fuels.yaml)" />
                  <Kpi label="Non-normal vessels" value={String(f.kpis.non_normal)} note="Any state other than NORMAL" />
                  <Kpi label="Schedule status" value="NOT TRACKED" note="No voyage-schedule feed connected" />
                </div>
              </Panel>

              <Panel title="Vessels" subtitle={<>Operating states <ProvenanceTag kind="ASSUMED" title={f.vessels[0]?.provenance} /> · predictions <ProvenanceTag kind="MODEL" /></>}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vessel</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className="text-right">STW ({UNITS.speed})</TableHead>
                      <TableHead>Fuel</TableHead>
                      <TableHead>Predicted fuel / 90% interval</TableHead>
                      <TableHead>Trust</TableHead>
                      <TableHead>OOD band</TableHead>
                      <TableHead>Fallback</TableHead>
                      <TableHead>Schedule</TableHead>
                      <TableHead><span className="sr-only">Actions</span></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {f.vessels.map((row) => {
                      const t = row.prediction.trust;
                      return (
                        <TableRow key={row.vessel.id} className={STATE_META[asHmiState(t.state)].severity >= 3 ? "bg-st-ood/10" : undefined}>
                          <TableCell className="font-semibold">{row.vessel.name}</TableCell>
                          <TableCell className="text-xs">{humanize(row.vessel.vessel_type)}</TableCell>
                          <TableCell className="num text-right">{fmt(row.vessel.stw_kn, 1)}</TableCell>
                          <TableCell className="text-xs uppercase">{row.vessel.fuel_type}</TableCell>
                          <TableCell><PredictionReadout prediction={row.prediction} compact /></TableCell>
                          <TableCell><StateBadge state={t.state} /></TableCell>
                          <TableCell className="text-xs">{humanize(t.ood_band)} <span className="num text-muted-foreground">d={fmt(t.envelope_distance, 2)}</span></TableCell>
                          <TableCell>{t.fallback ? <ToneChip tone="fallback">{t.fallback_label}</ToneChip> : <span className="text-xs text-muted-foreground">none</span>}</TableCell>
                          <TableCell className="text-xs text-muted-foreground" title={row.schedule_note}>not tracked</TableCell>
                          <TableCell><Button size="sm" variant="outline" onClick={() => open(row.vessel.id)}><Ship className="size-3.5" aria-hidden /> Open Vessel</Button></TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </Panel>

              <Panel title="Fleet alerts" subtitle="Derived from the current evaluation of each vessel" actions={<LinkButton size="sm" variant="ghost" href="/alerts">All alerts →</LinkButton>}>
                {alerts.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No OOD, fallback, missing-factor or invalid-input conditions in the current evaluation.</p>
                ) : (
                  <ul className="grid gap-1.5">
                    {alerts.map((a, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm">
                        <StateBadge state={a.state} />
                        <span className="font-semibold">{a.vessel}</span>
                        <span className="text-muted-foreground">{a.reason}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Panel>
              <Notice title="Data basis">Constraint violations appear after a Fleet Optimizer run; this screen evaluates prediction trust only.</Notice>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
