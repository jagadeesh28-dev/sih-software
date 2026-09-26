"use client";

import { RefreshCw } from "lucide-react";
import { DataState, LinkButton, Notice, PageHeader, Panel, StateBadge } from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { STATE_META, TONE_CLASS, asHmiState, fmtTime, useApi, type HmiState } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const ORDER: HmiState[] = ["OOD", "RUNTIME_FAILURE", "INVALID_INPUT", "FALLBACK", "CONSTRAINT_FAILURE", "WARNING", "MISSING_FACTOR", "NORMAL"];

export default function AlertsPage() {
  const alerts = useApi(api.alerts, [], 15000);
  return (
    <>
      <PageHeader title="Alerts & Safety"
        description="Abnormal conditions from the current fleet evaluation and from this session's predictions, scenarios and optimizer runs. Nothing here is converted into a normal recommendation."
        actions={<Button variant="outline" onClick={alerts.reload}><RefreshCw className="size-4" aria-hidden /> Refresh</Button>} />
      <DataState state={alerts}>
        {(a) => {
          const sorted = [...a.alerts].sort((x, y) => STATE_META[asHmiState(y.state)].severity - STATE_META[asHmiState(x.state)].severity);
          const critical = sorted.filter((x) => STATE_META[asHmiState(x.state)].severity >= 3);
          const rest = sorted.filter((x) => STATE_META[asHmiState(x.state)].severity < 3);
          const counts = Object.fromEntries(ORDER.map((s) => [s, a.alerts.filter((x) => asHmiState(x.state) === s).length]));
          return (
            <div className="grid gap-3">
              {critical.length > 0 && (
                <section aria-label="Critical conditions" className="grid gap-2">
                  {critical.map((x, i) => {
                    const meta = STATE_META[asHmiState(x.state)];
                    return (
                      <div key={i} role="alert" className="rounded-md border-2 border-st-ood bg-st-ood/15 p-3">
                        <div className="flex flex-wrap items-center gap-3">
                          <StateBadge state={x.state} size="lg" />
                          <span className="font-semibold">{x.vessel_id ?? (x.source?.includes("optimiz") ? "fleet optimizer" : "no vessel specified")}</span>
                          <span className="num ml-auto text-xs text-muted-foreground">{fmtTime(x.timestamp)}</span>
                        </div>
                        <p className="mt-2 text-sm"><span className="font-semibold">Reason:</span> {x.reason ?? "—"}</p>
                        <p className="text-sm font-medium text-st-ood">Operator action: {meta.action}</p>
                        <p className="text-xs text-muted-foreground">Source: {x.source}</p>
                      </div>
                    );
                  })}
                </section>
              )}
              <Panel title={`Active conditions (${sorted.length})`} subtitle={`Generated ${fmtTime(a.generated_at)}`}>
                {rest.length === 0 && critical.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No abnormal conditions: every vessel evaluates NORMAL and no session event raised a warning.</p>
                ) : rest.length === 0 ? (
                  <p className="text-sm text-muted-foreground">Only the critical conditions shown above.</p>
                ) : (
                  <table className="w-full text-sm">
                    <thead className="text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                      <tr><th className="py-1">State</th><th>Vessel</th><th>Reason</th><th>Operator action</th><th>Source</th><th>Time</th></tr>
                    </thead>
                    <tbody>
                      {rest.map((x, i) => (
                        <tr key={i} className="border-t align-top">
                          <td className="py-1.5 pr-2"><StateBadge state={x.state} /></td>
                          <td className="pr-2 font-medium">{x.vessel_id ?? "—"}</td>
                          <td className="pr-2 text-xs">{x.reason ?? "—"}</td>
                          <td className="pr-2 text-xs">{STATE_META[asHmiState(x.state)].action}</td>
                          <td className="pr-2 text-xs text-muted-foreground">{x.source}</td>
                          <td className="num text-xs text-muted-foreground">{fmtTime(x.timestamp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </Panel>
              <Panel title="State reference" subtitle="Meaning and required operator response for every trust state">
                <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
                  {ORDER.map((s) => {
                    const m = STATE_META[s];
                    return (
                      <div key={s} className={cn("rounded-md border p-2", TONE_CLASS[m.tone].border, m.severity >= 3 && "border-2")}>
                        <div className="flex items-center justify-between"><StateBadge state={s} /><span className="num text-xs text-muted-foreground">{counts[s]} active</span></div>
                        <p className="mt-1.5 text-xs">{m.explanation}</p>
                        <p className={cn("mt-1 text-xs font-medium", TONE_CLASS[m.tone].text)}>{m.action}</p>
                      </div>
                    );
                  })}
                </div>
              </Panel>
              <Notice title="Reproduce abnormal states">
                Use Prediction & Trust to submit invalid or extreme inputs, and Demo Mode scenes 5–6 for the verified OOD storm and runtime-failure cases.{" "}
                <LinkButton size="sm" variant="ghost" href="/trust">Open Prediction & Trust →</LinkButton>
              </Notice>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
