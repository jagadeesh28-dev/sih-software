"use client";

import { AlertOctagon, AlertTriangle, CheckCircle2, CircleSlash, FileWarning, Info, Loader2, RefreshCw, ShieldAlert, Unplug, Wrench } from "lucide-react";
import Link from "next/link";
import { Component, useEffect, useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { STATE_META, TONE_CLASS, asHmiState, fmt, humanize, type HmiState, type Tone } from "@/lib/hmi";

const STATE_ICON: Record<HmiState, typeof Info> = {
  NORMAL: CheckCircle2,
  WARNING: AlertTriangle,
  MISSING_FACTOR: FileWarning,
  FALLBACK: Wrench,
  CONSTRAINT_FAILURE: CircleSlash,
  INVALID_INPUT: ShieldAlert,
  RUNTIME_FAILURE: Unplug,
  OOD: AlertOctagon,
};

/** Navigation styled as a button (anchor semantics for keyboard/screen readers). */
export function LinkButton({ href, children, variant = "default", size = "default" }: {
  href: string; children: ReactNode; variant?: "default" | "outline" | "ghost" | "secondary"; size?: "default" | "sm";
}) {
  return <Button nativeButton={false} render={<Link href={href} />} variant={variant} size={size}>{children}</Button>;
}

/** Status chip: icon + text + colour — never colour alone. */
export function StateBadge({ state, size = "sm", className }: { state: string; size?: "sm" | "lg"; className?: string }) {
  const s = asHmiState(state);
  const meta = STATE_META[s];
  const Icon = STATE_ICON[s];
  const tone = TONE_CLASS[meta.tone];
  const critical = meta.severity >= 3;
  return (
    <span
      role="status"
      aria-label={`State: ${meta.label}`}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border font-semibold uppercase tracking-wide whitespace-nowrap",
        size === "lg" ? "px-2.5 py-1 text-sm" : "px-1.5 py-0.5 text-[11px]",
        critical ? tone.solid + " border-transparent" : `${tone.text} ${tone.border} ${tone.bg}`,
        className,
      )}
    >
      <Icon className={size === "lg" ? "size-4" : "size-3.5"} aria-hidden />
      {meta.label}
    </span>
  );
}

/** Plan feasibility exactly as the evaluator reports it: hard violation, soft penalties, or penalty-free. */
export function PlanStatus({ plan }: { plan: { feasible: boolean; penalty_free?: boolean; soft_penalties?: Record<string, number> } }) {
  if (!plan.feasible) return <StateBadge state="CONSTRAINT_FAILURE" />;
  if (plan.penalty_free) return <ToneChip tone="normal">FEASIBLE — PENALTY-FREE</ToneChip>;
  const soft = Object.keys(plan.soft_penalties ?? {}).map(humanize).join(", ");
  return <ToneChip tone="warning">FEASIBLE WITH SOFT PENALTIES{soft ? ` — ${soft}` : ""}</ToneChip>;
}

export function ToneChip({ tone, children, className }: { tone: Tone; children: ReactNode; className?: string }) {
  const t = TONE_CLASS[tone];
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide", t.text, t.border, t.bg, className)}>
      {children}
    </span>
  );
}

export type ProvenanceKind = "MEASURED" | "ASSUMED" | "SCENARIO" | "ESTIMATE" | "MODEL" | "HISTORICAL" | "DEMO" | "STORED";

const PROV: Record<ProvenanceKind, { label: string; tone: Tone }> = {
  MEASURED: { label: "MEASURED", tone: "normal" },
  ASSUMED: { label: "ASSUMED", tone: "warning" },
  SCENARIO: { label: "SCENARIO INPUT", tone: "info" },
  ESTIMATE: { label: "SCENARIO ESTIMATE", tone: "demo" },
  MODEL: { label: "MODEL OUTPUT", tone: "info" },
  HISTORICAL: { label: "HISTORICAL EVIDENCE", tone: "demo" },
  DEMO: { label: "DEMO / SIMULATION", tone: "demo" },
  STORED: { label: "STORED ARTIFACT", tone: "demo" },
};

export function ProvenanceTag({ kind, title }: { kind: ProvenanceKind; title?: string }) {
  const p = PROV[kind];
  return (
    <span title={title} className={cn("inline-flex rounded-[3px] border px-1 text-[10px] font-semibold tracking-wider", TONE_CLASS[p.tone].text, TONE_CLASS[p.tone].border)}>
      {p.label}
    </span>
  );
}

/** Map a backend provenance string (e.g. "MEASURED (historical record …)") to a tag kind. */
export function provenanceKind(text: string): ProvenanceKind {
  if (text.startsWith("MEASURED")) return "MEASURED";
  if (text.startsWith("SCENARIO")) return "SCENARIO";
  if (text.startsWith("ASSUMED")) return "ASSUMED";
  return "MODEL";
}

export function Panel({ title, subtitle, actions, children, className, tone }: {
  title?: ReactNode; subtitle?: ReactNode; actions?: ReactNode; children: ReactNode; className?: string; tone?: Tone;
}) {
  return (
    <section className={cn("min-w-0 rounded-md border bg-panel", tone && TONE_CLASS[tone].border, className)}>
      {(title || actions) && (
        <header className="flex items-start justify-between gap-3 border-b px-3 py-2">
          <div className="min-w-0">
            {title && <h2 className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-xs text-muted-foreground/80">{subtitle}</p>}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </header>
      )}
      <div className="p-3">{children}</div>
    </section>
  );
}

export function Kpi({ label, value, unit, digits = 1, note, tag, emphasis }: {
  label: string; value: number | null | undefined | string; unit?: string; digits?: number;
  note?: ReactNode; tag?: ReactNode; emphasis?: boolean;
}) {
  const text = typeof value === "string" ? value : fmt(value, digits);
  return (
    <div className="min-w-0">
      <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        {label}
        {tag}
      </div>
      <div className={cn("num mt-0.5 leading-none", emphasis ? "text-3xl font-semibold" : "text-xl font-medium")}>
        {text}
        {unit && text !== "—" && <span className="ml-1 text-xs font-normal text-muted-foreground">{unit}</span>}
      </div>
      {note && <div className="mt-1 text-[11px] text-muted-foreground">{note}</div>}
    </div>
  );
}

export function Field({ label, value, unit, tag }: { label: string; value: ReactNode; unit?: string; tag?: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-rule/60 py-1 last:border-b-0">
      <dt className="flex items-center gap-1.5 text-xs text-muted-foreground">{label}{tag}</dt>
      <dd className="num text-right text-sm">
        {value}
        {unit && <span className="ml-1 text-[11px] text-muted-foreground">{unit}</span>}
      </dd>
    </div>
  );
}

export function Loading({ label = "Loading from backend…" }: { label?: string }) {
  return (
    <div role="status" className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
      <Loader2 className="size-4 animate-spin" aria-hidden /> {label}
    </div>
  );
}

export function FreshnessIndicator({
  freshness,
  lastValidTimestamp,
  className,
}: {
  freshness?: "CURRENT" | "STALE" | "UNAVAILABLE";
  lastValidTimestamp?: string;
  className?: string;
}) {
  const [age, setAge] = useState<string>(() => {
    if (!lastValidTimestamp) return "unavailable";
    const diff = Math.max(0, Math.round((Date.now() - new Date(lastValidTimestamp).getTime()) / 1000));
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  });

  useEffect(() => {
    if (!lastValidTimestamp) return;
    const update = () => {
      const diff = Math.max(0, Math.round((Date.now() - new Date(lastValidTimestamp).getTime()) / 1000));
      if (diff < 60) setAge(`${diff}s ago`);
      else if (diff < 3600) setAge(`${Math.floor(diff / 60)}m ago`);
      else setAge(`${Math.floor(diff / 3600)}h ago`);
    };
    update();
    const id = setInterval(update, 5000);
    return () => clearInterval(id);
  }, [lastValidTimestamp]);

  const f = freshness ?? (lastValidTimestamp ? "CURRENT" : "UNAVAILABLE");
  const dotColor =
    f === "CURRENT" ? "bg-st-normal" : f === "STALE" ? "bg-st-warning animate-pulse" : "bg-st-ood";

  return (
    <div className={cn("inline-flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground", className)}>
      <span className={cn("size-2 rounded-full shrink-0", dotColor)} />
      <span>DATA</span>
      <span className="font-semibold text-foreground">
        ● {f === "CURRENT" ? `Current — ${age}` : f === "STALE" ? `Stale — ${age}` : "Unavailable"}
      </span>
    </div>
  );
}

export function ErrorBox({
  error,
  onRetry,
  lastValidTimestamp,
  cachedDataNotice,
}: {
  error: string;
  onRetry?: () => void;
  lastValidTimestamp?: string;
  cachedDataNotice?: boolean;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start justify-between gap-3 rounded-md border p-3 text-sm",
        cachedDataNotice
          ? "border-st-warning/60 bg-st-warning/10"
          : "border-st-ood bg-st-ood/10",
      )}
    >
      <div className="flex items-start gap-2">
        <Unplug
          className={cn("mt-0.5 size-4 shrink-0", cachedDataNotice ? "text-st-warning" : "text-st-ood")}
          aria-hidden
        />
        <div>
          <div className={cn("font-semibold uppercase tracking-wider", cachedDataNotice ? "text-st-warning" : "text-st-ood")}>
            {cachedDataNotice
              ? `CONNECTION LOST — LAST VALID RESULT: ${lastValidTimestamp ? new Date(lastValidTimestamp).toLocaleTimeString() : "CACHED"}`
              : "CONNECTION LOST — BACKEND UNAVAILABLE"}
          </div>
          <div className="mt-0.5 break-words text-xs text-muted-foreground">{error}</div>
          {cachedDataNotice && (
            <div className="mt-1 text-[11px] font-medium text-st-warning">
              Operating with last valid cached result. Never treated as live telemetry.
            </div>
          )}
        </div>
      </div>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry} className="shrink-0 h-7 text-xs">
          <RefreshCw className="size-3 mr-1" aria-hidden /> Retry
        </Button>
      )}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">{children}</div>;
}

/** Standard wrapper for any Loadable: loading → error → empty → content. Gracefully handles stale results. */
export function DataState<T>({
  state,
  empty,
  children,
}: {
  state: {
    data: T | undefined;
    error?: string;
    loading: boolean;
    reload: () => void;
    lastValidTimestamp?: string;
    isStale?: boolean;
    freshness?: "CURRENT" | "STALE" | "UNAVAILABLE";
  };
  empty?: (d: T) => boolean;
  children: (d: T) => ReactNode;
}) {
  // If we have an error BUT we also have previous data, retain display with warning header (LAST VALID RESULT)
  if (state.error && state.data !== undefined) {
    return (
      <div className="grid gap-3">
        <ErrorBox
          error={state.error}
          onRetry={state.reload}
          lastValidTimestamp={state.lastValidTimestamp}
          cachedDataNotice={true}
        />
        {children(state.data)}
      </div>
    );
  }

  if (state.error) {
    return <ErrorBox error={state.error} onRetry={state.reload} />;
  }

  if (state.data === undefined) {
    return <Loading />;
  }

  if (empty?.(state.data)) {
    return <Empty>No records returned by the backend.</Empty>;
  }

  return <>{children(state.data)}</>;
}

export function PageHeader({ title, description, actions, badge }: { title: string; description?: ReactNode; actions?: ReactNode; badge?: ReactNode }) {
  return (
    <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
          {badge}
        </div>
        {description && <p className="mt-0.5 max-w-4xl text-xs text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Notice({ tone = "info", title, children }: { tone?: Tone; title: string; children?: ReactNode }) {
  const t = TONE_CLASS[tone];
  return (
    <div className={cn("flex items-start gap-2 rounded-md border px-3 py-2 text-xs", t.border, t.bg)}>
      <Info className={cn("mt-0.5 size-3.5 shrink-0", t.text)} aria-hidden />
      <div>
        <span className={cn("font-semibold uppercase tracking-wide", t.text)}>{title}</span>
        {children && <span className="ml-1 text-muted-foreground">{children}</span>}
      </div>
    </div>
  );
}

export function OperationalStatusBadge({ status }: { status: "ON_SCHEDULE" | "OPTIMIZATION_AVAILABLE" | "ATTENTION" | "DEGRADED" | "FALLBACK" | string }) {
  switch (status) {
    case "ON_SCHEDULE":
    case "ON SCHEDULE":
      return <ToneChip tone="normal">ON SCHEDULE</ToneChip>;
    case "OPTIMIZATION_AVAILABLE":
    case "OPTIMIZATION AVAILABLE":
      return <ToneChip tone="info">OPTIMIZATION AVAILABLE</ToneChip>;
    case "ATTENTION":
    case "ATTENTION REQUIRED":
      return <ToneChip tone="warning">ATTENTION REQUIRED</ToneChip>;
    case "FALLBACK":
      return <ToneChip tone="fallback">REFERENCE MODEL</ToneChip>;
    case "DEGRADED":
    case "CRITICAL":
      return <ToneChip tone="ood">DEGRADED / OOD</ToneChip>;
    default:
      return <ToneChip tone="info">{status.replace(/_/g, " ")}</ToneChip>;
  }
}

export function TechnicalDetails({ title = "Technical & Model Details", children, defaultOpen = false }: {
  title?: string;
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="mt-3 rounded-md border border-rule/70 bg-panel-2/50 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground hover:bg-accent/40 transition-colors"
      >
        <span className="flex items-center gap-2">
          <Info className="size-3.5 text-primary" aria-hidden />
          {title}
        </span>
        <span className="text-[11px] font-normal text-primary">
          {open ? "▲ Hide Technical Details" : "▼ View Technical Details"}
        </span>
      </button>
      {open && (
        <div className="border-t border-rule/60 p-3 text-xs">
          {children}
        </div>
      )}
    </div>
  );
}


/** Catches render-time failures (e.g. a payload failing schema validation) and shows them explicitly. */
export class ErrorBoundary extends Component<{ children: ReactNode; resetKey?: unknown }, { error?: Error }> {
  state: { error?: Error } = {};
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidUpdate(prev: { resetKey?: unknown }) {
    if (prev.resetKey !== this.props.resetKey && this.state.error) this.setState({ error: undefined });
  }
  render() {
    return this.state.error ? <ErrorBox error={`Render failed: ${this.state.error.message}`} /> : this.props.children;
  }
}

export function ConfidenceBand({
  lower,
  upper,
  value,
  confidence,
  unit = "kg/h",
}: {
  lower?: number | null;
  upper?: number | null;
  value?: number | null;
  confidence?: number;
  unit?: string;
}) {
  if (lower == null || upper == null || value == null) return null;
  const spread = upper - lower;
  const pct = Math.max(0, Math.min(100, spread > 0 ? ((value - lower) / spread) * 100 : 50));

  return (
    <div className="rounded-md border border-panel-border/80 bg-panel-2/40 p-2.5 text-xs">
      <div className="flex items-center justify-between text-[11px] text-muted-foreground font-medium mb-1.5">
        <span>Expected Conformal Range ({confidence ? `${Math.round(confidence * 100)}%` : "90%"})</span>
        <span className="font-mono text-cyan-300 font-semibold">{fmt(value, 0)} {unit}</span>
      </div>
      <div className="relative h-2 rounded-full bg-panel-2 border border-panel-border overflow-hidden">
        <div className="absolute inset-y-0 bg-cyan-500/30 w-full" />
        <div
          className="absolute inset-y-0 w-2 -ml-1 bg-cyan-400 rounded-full shadow-sm"
          style={{ left: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between font-mono text-[10px] text-muted-foreground mt-1">
        <span>Low: {fmt(lower, 0)}</span>
        <span>High: {fmt(upper, 0)} {unit}</span>
      </div>
    </div>
  );
}

