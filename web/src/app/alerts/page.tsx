"use client";

import { AlertOctagon, AlertTriangle, CheckCircle, Info, RefreshCw, ShieldAlert, ShieldCheck } from "lucide-react";
import {
  DataState,
  Kpi,
  LinkButton,
  Notice,
  PageHeader,
  Panel,
  StateBadge,
  TechnicalDetails,
  ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { STATE_META, TONE_CLASS, asHmiState, fmtTime, useApi, type HmiState } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const SAFETY_LEVELS = [
  { level: 3, label: "Level 3: Critical Safety", tone: "ood", icon: AlertOctagon, desc: "Immediate operational intervention required" },
  { level: 2, label: "Level 2: Attention Required", tone: "warning", icon: AlertTriangle, desc: "Operation outside envelope or fallback active" },
  { level: 1, label: "Level 1: Operational Notice", tone: "info", icon: Info, desc: "Informational dispatch or factor update" },
  { level: 0, label: "Level 0: Nominal", tone: "normal", icon: CheckCircle, desc: "All systems operating within validated envelope" },
] as const;

export default function AlertsPage() {
  const alerts = useApi(api.alerts, [], 15000);

  return (
    <>
      <PageHeader
        title="Safety Alerts & Operational Queue"
        badge={<ToneChip tone="warning">Safety-Critical Monitoring</ToneChip>}
        description="Active operational exception queue categorized by safety-critical priority. Monitors operating envelope excursions, reference model fallback activations, and constraint feasibility."
        actions={
          <Button variant="outline" size="sm" onClick={alerts.reload} className="h-8 text-xs">
            <RefreshCw className="size-3.5 mr-1" aria-hidden /> Refresh Queue
          </Button>
        }
      />

      <DataState state={alerts}>
        {(a) => {
          const sorted = [...a.alerts].sort(
            (x, y) => STATE_META[asHmiState(y.state)].severity - STATE_META[asHmiState(x.state)].severity
          );
          const critical = sorted.filter((x) => STATE_META[asHmiState(x.state)].severity >= 3);
          const attention = sorted.filter((x) => STATE_META[asHmiState(x.state)].severity === 2);
          const info = sorted.filter((x) => STATE_META[asHmiState(x.state)].severity === 1);

          return (
            <div className="grid gap-4">
              {/* Executive Safety Severity Strip */}
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <Kpi
                  label="Critical Alerts (L3)"
                  value={critical.length}
                  note={critical.length > 0 ? "Immediate operator action" : "Zero critical safety halts"}
                />
                <Kpi
                  label="Attention Required (L2)"
                  value={attention.length}
                  note="Envelopes / fallbacks active"
                />
                <Kpi
                  label="Informational (L1)"
                  value={info.length}
                  note="Advisory operational notices"
                />
                <Kpi
                  label="Fleet Integrity"
                  value={critical.length === 0 ? "STABLE" : "ACTION REQUIRED"}
                  note={`Generated ${fmtTime(a.generated_at)}`}
                />
              </div>

              {/* LEVEL 3: Critical Conditions */}
              {critical.length > 0 && (
                <section aria-label="Critical conditions" className="grid gap-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                    <AlertOctagon className="size-4" /> Level 3 · Critical Operational Conditions
                  </div>
                  {critical.map((x, i) => {
                    const meta = STATE_META[asHmiState(x.state)];
                    return (
                      <div
                        key={i}
                        role="alert"
                        className="rounded-md border border-rose-600/60 bg-rose-950/20 p-4 shadow-sm"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rose-800/40 pb-2">
                          <div className="flex items-center gap-2">
                            <StateBadge state={x.state} size="lg" />
                            <span className="font-bold text-sm text-foreground">
                              {x.vessel_id ? `Vessel: ${x.vessel_id}` : "Fleet Dispatch Engine"}
                            </span>
                          </div>
                          <span className="num font-mono text-xs text-muted-foreground">{fmtTime(x.timestamp)}</span>
                        </div>

                        <div className="mt-3 grid gap-2 text-xs md:grid-cols-3">
                          <div>
                            <div className="text-[10px] uppercase font-semibold text-muted-foreground">What Happened</div>
                            <p className="mt-0.5 text-foreground font-medium">{x.reason ?? "Safety condition detected"}</p>
                          </div>
                          <div>
                            <div className="text-[10px] uppercase font-semibold text-muted-foreground">Why It Matters</div>
                            <p className="mt-0.5 text-rose-200">{meta.explanation}</p>
                          </div>
                          <div>
                            <div className="text-[10px] uppercase font-semibold text-muted-foreground">Required Operator Action</div>
                            <p className="mt-0.5 text-rose-300 font-semibold">{meta.action}</p>
                          </div>
                        </div>

                        {x.vessel_id && (
                          <div className="mt-3 pt-2 border-t border-rose-900/40 flex justify-end">
                            <LinkButton size="sm" variant="outline" href={`/vessel/${x.vessel_id}`}>
                              Inspect Vessel Performance →
                            </LinkButton>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </section>
              )}

              {/* LEVEL 2 & 1: Active Operational Queue */}
              <Panel
                title={`Operational Attention Queue (${attention.length + info.length})`}
                subtitle="Monitored conditions requiring review or advisory guidance"
              >
                {attention.length === 0 && info.length === 0 && critical.length === 0 ? (
                  <div className="py-8 text-center text-xs text-muted-foreground flex flex-col items-center gap-1.5">
                    <ShieldCheck className="size-8 text-emerald-400 opacity-80" />
                    <span className="font-semibold text-foreground text-sm">All Monitored Assets Nominal</span>
                    <span>No active warnings, fallbacks, or envelope excursions across the fleet.</span>
                  </div>
                ) : attention.length === 0 && info.length === 0 ? (
                  <p className="text-xs text-muted-foreground">Only the critical conditions shown above are active.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead className="text-left text-[10px] uppercase tracking-wider text-muted-foreground border-b border-panel-border/60">
                        <tr>
                          <th className="py-2 pr-2">Severity</th>
                          <th className="py-2 pr-2">Asset</th>
                          <th className="py-2 pr-2">Condition</th>
                          <th className="py-2 pr-2">Operator Guidance</th>
                          <th className="py-2 pr-2">Source</th>
                          <th className="py-2 text-right">Time</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-panel-border/30">
                        {[...attention, ...info].map((x, i) => (
                          <tr key={i} className="hover:bg-panel-2/40 transition-colors">
                            <td className="py-2 pr-2"><StateBadge state={x.state} size="sm" /></td>
                            <td className="pr-2 font-semibold font-mono text-[11px] text-foreground">{x.vessel_id ?? "Fleet"}</td>
                            <td className="pr-2 text-muted-foreground">{x.reason ?? "Operational advisory"}</td>
                            <td className="pr-2 font-medium text-foreground">{STATE_META[asHmiState(x.state)].action}</td>
                            <td className="pr-2 text-muted-foreground text-[11px]">{x.source}</td>
                            <td className="num text-right font-mono text-[11px] text-muted-foreground">{fmtTime(x.timestamp)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Panel>

              {/* Technical Details: Safety State Taxonomies */}
              <TechnicalDetails title="Maritime Operational State Reference & Protocols">
                <div className="grid gap-2.5 md:grid-cols-2 xl:grid-cols-4">
                  {(["OOD", "RUNTIME_FAILURE", "FALLBACK", "NORMAL"] as HmiState[]).map((s) => {
                    const m = STATE_META[s];
                    return (
                      <div key={s} className={cn("rounded-md border p-2.5 bg-panel-2/60", TONE_CLASS[m.tone].border)}>
                        <div className="flex items-center justify-between mb-1">
                          <StateBadge state={s} size="sm" />
                          <span className="text-[10px] text-muted-foreground font-mono">Sev {m.severity}</span>
                        </div>
                        <p className="text-[11px] text-muted-foreground leading-snug">{m.explanation}</p>
                        <p className={cn("mt-1.5 text-[11px] font-semibold", TONE_CLASS[m.tone].text)}>{m.action}</p>
                      </div>
                    );
                  })}
                </div>
              </TechnicalDetails>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
