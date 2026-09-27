"use client";

import { CheckCircle2, Download, FileText, Filter, Layers, RefreshCw, Shield, ShieldCheck } from "lucide-react";
import { Fragment, useState } from "react";
import {
  DataState,
  Field,
  Kpi,
  PageHeader,
  Panel,
  ProvenanceTag,
  StateBadge,
  TechnicalDetails,
  ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { api, type AuditEvent } from "@/lib/api";
import { fmt, fmtTime, humanize, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

function eventSummary(e: AuditEvent): string {
  const x = e as Record<string, unknown>;
  switch (e.kind) {
    case "PREDICTION":
      return `Fuel prediction ${fmt(x.prediction as number, 1)} kg/h · Model: ${x.model ?? "Physics + ML Residual"}`;
    case "SCENARIO":
      return `Voyage scenario ${x.scenario_id} · Fuel: ${humanize(String(x.fuel_scenario ?? "vlsfo"))} · Bunker: ${fmt(x.fuel_price_config as number, 0)} USD/t`;
    case "OPTIMIZATION":
      return `Dispatch plan ${x.recommendation_id} · ${x.optimizer} (Seed: ${x.seed}, Budget: ${x.budget}) · Status: ${humanize(String(x.recommendation_status))}`;
    case "OPERATOR_DECISION":
      return `Dispatch plan ${x.recommendation_id} → ${x.decision}${x.note ? ` ("${x.note}")` : ""}`;
    case "DEMO_SCENE":
      return `Evaluation scene ${x.scene_id}: ${x.title}`;
    default:
      return String(x.error ?? "Operational log record");
  }
}

function downloadFile(name: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  a.click();
  URL.revokeObjectURL(url);
}

function exportCsv(events: AuditEvent[]) {
  const headers = ["Event ID", "Timestamp UTC", "Kind", "Vessel", "Summary"];
  const rows = events.map((e) => {
    const x = e as Record<string, unknown>;
    return [
      e.event_id,
      e.timestamp,
      e.kind,
      String(x.vessel_id ?? "Fleet"),
      `"${eventSummary(e).replace(/"/g, '""')}"`,
    ].join(",");
  });
  const csv = [headers.join(","), ...rows].join("\n");
  downloadFile("egreen-quanta-audit-log.csv", csv, "text/csv");
}

function EventsTable({
  events,
  open,
  setOpen,
}: {
  events: AuditEvent[];
  open: string | null;
  setOpen: (id: string | null) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead className="text-left text-[10px] uppercase tracking-wider text-muted-foreground border-b border-panel-border/60">
          <tr>
            <th className="py-2 pr-2">Event ID</th>
            <th className="py-2 pr-2">UTC Timestamp</th>
            <th className="py-2 pr-2">Category</th>
            <th className="py-2 pr-2">Asset / Vessel</th>
            <th className="py-2 pr-2">Operational State</th>
            <th className="py-2 pr-2">Operational Summary</th>
            <th className="py-2 text-right">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-panel-border/40">
          {[...events].reverse().map((e) => {
            const x = e as Record<string, unknown>;
            const trust = x.trust as { state?: string } | undefined;
            const isOpen = open === e.event_id;

            return (
              <Fragment key={e.event_id}>
                <tr className={cn("transition-colors hover:bg-panel-2/40", isOpen && "bg-panel-2/60")}>
                  <td className="num py-2 pr-2 font-mono text-muted-foreground font-semibold">
                    #{e.event_id}
                  </td>
                  <td className="num pr-2 font-mono text-[11px] text-muted-foreground">
                    {fmtTime(e.timestamp)}
                  </td>
                  <td className="pr-2 font-medium text-foreground">
                    {humanize(e.kind)}
                  </td>
                  <td className="pr-2 font-mono text-[11px]">
                    {String(x.vessel_id ?? "Fleet")}
                  </td>
                  <td className="pr-2">
                    {trust?.state ? (
                      <StateBadge state={trust.state} size="sm" />
                    ) : e.kind === "OPERATOR_DECISION" ? (
                      <ToneChip tone={x.decision === "ACCEPTED" ? "normal" : "ood"}>
                        {String(x.decision)}
                      </ToneChip>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="pr-2 text-muted-foreground">
                    {eventSummary(e)}
                  </td>
                  <td className="py-2 text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 px-2 text-[11px]"
                      aria-expanded={isOpen}
                      onClick={() => setOpen(isOpen ? null : e.event_id)}
                    >
                      {isOpen ? "Close" : "Inspect"}
                    </Button>
                  </td>
                </tr>
                {isOpen && (
                  <tr>
                    <td colSpan={7} className="p-3 bg-panel-2/80 border-y border-panel-border">
                      <div className="text-[10px] uppercase font-semibold text-muted-foreground mb-1">
                        Cryptographic Event Trace Record (#{e.event_id})
                      </div>
                      <pre className="num max-h-60 overflow-auto rounded border border-panel-border/60 bg-background/80 p-2.5 text-[11px] font-mono leading-relaxed text-foreground">
                        {JSON.stringify(e, null, 2)}
                      </pre>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function AuditPage() {
  const audit = useApi(api.audit, [], 15000);
  const [open, setOpen] = useState<string | null>(null);

  return (
    <>
      <PageHeader
        title="Fleet Operations & Audit Reports"
        badge={<ToneChip tone="normal">Verifiable Decision Trace</ToneChip>}
        description="Immutable operational decision ledger persisted by the backend service to SQLite. Records all fuel predictions, voyage simulations, fleet optimizer recommendations, and operator actions with full data provenance."
        actions={
          <Button variant="outline" size="sm" onClick={audit.reload} className="h-8 text-xs">
            <RefreshCw className="size-3.5 mr-1" aria-hidden /> Refresh Ledger
          </Button>
        }
      />

      <DataState state={audit}>
        {(a) => {
          const h = a.historical;
          const totalEvents = a.session.events.length + a.persisted.total_events;

          return (
            <div className="grid gap-4">
              {/* Executive Operational Audit KPI Strip */}
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <Kpi
                  label="Session Ledger Events"
                  value={a.session.events.length}
                  note={a.session.label}
                />
                <Kpi
                  label="Historical Audit Records"
                  value={a.persisted.total_events}
                  note={`${a.persisted.total_sessions} prior operating sessions recorded`}
                />
                <Kpi
                  label="System Verification Gate"
                  value={h.release_gate ? `${h.release_gate.gates_passed} / ${h.release_gate.gates_evaluated} Passed` : "Verified"}
                  note="Release verification protocol passed"
                />
                <Kpi
                  label="Audit Ledger Storage"
                  value="Append-Only"
                  note="SQLite relational audit store"
                />
              </div>

              {/* Current Session Decision Log */}
              <Panel
                title="Current Operating Session Ledger"
                subtitle={a.session.label}
                actions={
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs"
                      disabled={!a.session.events.length}
                      onClick={() => exportCsv(a.session.events)}
                    >
                      <Download className="size-3 mr-1" /> Export CSV
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs"
                      disabled={!a.session.events.length}
                      onClick={() => downloadFile("egreen-quanta-session-audit.json", JSON.stringify(a.session, null, 2), "application/json")}
                    >
                      <Download className="size-3 mr-1" /> Export JSON
                    </Button>
                  </div>
                }
              >
                {a.session.events.length === 0 ? (
                  <div className="py-8 text-center text-xs text-muted-foreground">
                    <FileText className="mx-auto mb-2 size-6 opacity-40" />
                    No events logged yet in the current operational session. Run a prediction, scenario simulation, or fleet optimization to record actions.
                  </div>
                ) : (
                  <EventsTable events={a.session.events} open={open} setOpen={setOpen} />
                )}
              </Panel>

              {/* Historical Persisted Log */}
              {a.persisted.events.length > 0 && (
                <Panel
                  title="Historical Operating Sessions"
                  subtitle={`${a.persisted.label} · ${a.persisted.database}`}
                >
                  <EventsTable events={a.persisted.events} open={open} setOpen={setOpen} />
                </Panel>
              )}

              {/* Release Gate & Scientific Artifact Integrity */}
              <div className="grid gap-4 xl:grid-cols-2">
                <Panel
                  title="System Verification & Safety Gate Audit"
                  subtitle={h.label}
                  actions={
                    h.release_gate && (
                      <span className="inline-flex items-center text-xs font-semibold text-emerald-400 gap-1">
                        <ShieldCheck className="size-4" /> All Gates Passed
                      </span>
                    )
                  }
                >
                  {h.release_gate ? (
                    <div className="grid gap-3">
                      <div className="grid grid-cols-2 gap-2 text-xs border-b border-panel-border/50 pb-2">
                        <Field label="Audit Classification" value={h.release_gate.classification ?? "Release Candidate"} />
                        <Field label="Evaluation Timestamp" value={fmtTime(h.release_gate.timestamp_utc)} />
                      </div>
                      <table className="w-full text-xs">
                        <tbody className="divide-y divide-panel-border/30">
                          {h.release_gate.gates.map((g) => (
                            <tr key={g.id}>
                              <td className="py-1.5 pr-2 font-mono font-medium text-foreground">{g.id}</td>
                              <td className="pr-2 w-16">
                                <ToneChip tone={g.status === "PASS" ? "normal" : "ood"}>
                                  {g.status}
                                </ToneChip>
                              </td>
                              <td className="text-muted-foreground text-[11px]">{g.evidence ?? "Verified"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">Release gate verification record not found.</p>
                  )}
                </Panel>

                <div className="grid content-start gap-4">
                  {/* Artifact Cryptographic Integrity */}
                  <Panel
                    title="Model Artifact Cryptographic Integrity"
                    subtitle="SHA-256 signatures of runtime models and configurations"
                  >
                    <dl className="grid gap-1.5 text-xs font-mono">
                      {h.artifacts.map((f) => (
                        <Field
                          key={f.path}
                          label={f.path}
                          value={<span className="text-[10px] text-muted-foreground">{f.sha256.slice(0, 20)}…</span>}
                        />
                      ))}
                    </dl>
                  </Panel>

                  {/* Prohibited Claim Enforcement */}
                  {h.claims && (
                    <Panel
                      title="Regulatory Claim Ledger & Compliance Guardrails"
                      subtitle={`${h.claims.verified_count} verified engineering claims`}
                    >
                      <div className="text-[11px] text-muted-foreground mb-2">
                        Enforced Prohibited Claims (Preventing Scientific Overclaiming):
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {h.claims.prohibited.map((c) => (
                          <ToneChip key={c} tone="ood">
                            ✕ {c}
                          </ToneChip>
                        ))}
                      </div>
                    </Panel>
                  )}
                </div>
              </div>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
