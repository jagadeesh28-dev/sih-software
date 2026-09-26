"use client";

import { AlertOctagon, AlertTriangle, CheckCircle2, CircleSlash, FileWarning, Info, Loader2, RefreshCw, ShieldAlert, Unplug, Wrench } from "lucide-react";
import Link from "next/link";
import { Component, type ReactNode } from "react";
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

export function ErrorBox({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex items-start justify-between gap-3 rounded-md border border-st-ood bg-st-ood/10 p-3 text-sm">
      <div className="flex items-start gap-2">
        <Unplug className="mt-0.5 size-4 text-st-ood" aria-hidden />
        <div>
          <div className="font-semibold text-st-ood">BACKEND ERROR — no value shown</div>
          <div className="mt-0.5 break-words text-muted-foreground">{error}</div>
        </div>
      </div>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry}>
          <RefreshCw className="size-3.5" aria-hidden /> Retry
        </Button>
      )}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">{children}</div>;
}

/** Standard wrapper for any Loadable: loading → error → empty → content. */
export function DataState<T>({ state, empty, children }: {
  state: { data: T | undefined; error?: string; loading: boolean; reload: () => void };
  empty?: (d: T) => boolean;
  children: (d: T) => ReactNode;
}) {
  if (state.error) return <ErrorBox error={state.error} onRetry={state.reload} />;
  if (state.data === undefined) return <Loading />;
  if (empty?.(state.data)) return <Empty>No records returned by the backend.</Empty>;
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
