"use client";

import { AlertOctagon, Wrench } from "lucide-react";
import type { Prediction, Trust } from "@/lib/api";
import { STATE_META, TONE_CLASS, asHmiState, fmt, fmtTime, humanize, UNITS } from "@/lib/hmi";
import { cn } from "@/lib/utils";
import { Field, StateBadge, ToneChip } from "./primitives";

const BAND_TONE = { IN_DOMAIN: "normal", NEAR_BOUNDARY: "warning", OOD: "ood", REJECT: "ood", CATEGORICAL: "ood", NOT_EVALUATED: "info" } as const;

/** Envelope distance against the router's own thresholds (all values from the backend). */
export function EnvelopeGauge({ trust }: { trust: Trust }) {
  // The router reports a sentinel distance for rejected inputs; show nothing rather than a fake number.
  const d = trust.ood_band === "NOT_EVALUATED" || trust.ood_band === "CATEGORICAL" ? null : trust.envelope_distance;
  const { warning, ood, reject } = trust.thresholds;
  const max = reject * 1.25;
  const pct = (v: number) => `${Math.min(100, (v / max) * 100)}%`;
  const band = trust.ood_band as keyof typeof BAND_TONE;
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] text-muted-foreground">
        <span>Training-envelope distance</span>
        <ToneChip tone={BAND_TONE[band] ?? "info"}>{humanize(trust.ood_band)}</ToneChip>
      </div>
      <div className="relative h-3 overflow-hidden rounded-sm border bg-panel-2" aria-hidden>
        <div className="absolute inset-y-0 bg-st-warning/25" style={{ left: pct(warning), width: `calc(${pct(ood)} - ${pct(warning)})` }} />
        <div className="absolute inset-y-0 bg-st-ood/35" style={{ left: pct(ood), right: 0 }} />
        {d != null && <div className="absolute inset-y-[-2px] w-1 bg-foreground" style={{ left: pct(d) }} />}
      </div>
      <div className="num relative mt-1 h-4 text-[10px] text-muted-foreground">
        <span className="absolute" style={{ left: 0 }}>0</span>
        <span className="absolute -translate-x-1/2" style={{ left: pct(warning) }}>warn {warning}</span>
        <span className="absolute -translate-x-1/2" style={{ left: pct(ood) }}>OOD {ood}</span>
        <span className="absolute -translate-x-1/2" style={{ left: pct(reject) }}>reject {reject}</span>
      </div>
      <div className="num text-xs">d = {d == null ? "not evaluated" : fmt(d, 3)}</div>
    </div>
  );
}

/** Large, unmistakable trust banner. OOD / invalid / failure never look like normal operation. */
export function TrustBanner({ prediction }: { prediction: Prediction }) {
  const { trust, result } = prediction;
  const meta = STATE_META[asHmiState(trust.state)];
  const tone = TONE_CLASS[meta.tone];
  const critical = meta.severity >= 3;
  return (
    <div className={cn("rounded-md border-2 p-3", tone.border, critical ? "bg-st-ood/20" : tone.bg)}>
      <div className="flex flex-wrap items-center gap-2">
        {critical && <AlertOctagon className="size-6 text-st-ood" aria-hidden />}
        <StateBadge state={trust.state} size="lg" />
        {trust.fallback && (
          <span className="inline-flex items-center gap-1.5 rounded-sm border-2 border-st-fallback px-2 py-0.5 text-sm font-bold uppercase text-st-fallback">
            <Wrench className="size-4" aria-hidden /> {trust.fallback_label}
          </span>
        )}
        <span className="text-xs text-muted-foreground">Router: {humanize(result.routing_status)} · Source: {humanize(result.prediction_source)}</span>
      </div>
      <p className="mt-2 text-sm">{meta.explanation}</p>
      {trust.reason && <p className="mt-1 text-sm"><span className="font-semibold">Reason:</span> {trust.reason}</p>}
      <p className={cn("mt-1 text-sm font-medium", tone.text)}>Operator action: {meta.action}</p>
    </div>
  );
}

/** Prediction value with interval, confidence and model; value withheld when the router produced none. */
export function PredictionReadout({ prediction, compact = false }: { prediction: Prediction; compact?: boolean }) {
  const r = prediction.result;
  const u = r.uncertainty;
  const critical = STATE_META[asHmiState(prediction.trust.state)].severity >= 3;
  if (r.fuel_prediction == null) {
    return (
      <div className="text-sm font-semibold text-st-ood">
        NO PREDICTION — {humanize(prediction.trust.state)}
      </div>
    );
  }
  return (
    <div className={cn(critical && "opacity-80")}>
      {prediction.trust.state === "OOD" && (
        <div className="mb-1 text-xs font-bold uppercase tracking-wide text-st-ood">
          Physics emergency estimate — not a recommendation
        </div>
      )}
      <div className={cn("num leading-none", compact ? "text-lg font-medium" : "text-4xl font-semibold")}>
        {fmt(r.fuel_prediction, 1)}
        <span className="ml-1 text-sm font-normal text-muted-foreground">{UNITS.fuelRate}</span>
      </div>
      {u && (
        <div className="num mt-1 text-xs text-muted-foreground">
          {Math.round(u.coverage * 100)}% interval [{fmt(u.lower_bound_kg_h, 0)} – {fmt(u.upper_bound_kg_h, 0)}] {UNITS.fuelRate}
          {!compact && <> · width {fmt(u.interval_width_kg_h, 0)} {UNITS.fuelRate}</>}
        </div>
      )}
    </div>
  );
}

export function PredictionDetails({ prediction }: { prediction: Prediction }) {
  const r = prediction.result;
  const t = prediction.trust;
  return (
    <dl>
      <Field label="Model ID" value={r.model ?? "—"} />
      <Field label="Model version" value={r.model_version ?? "—"} />
      <Field label="Confidence" value={r.confidence} />
      <Field label="In training domain" value={r.in_domain == null ? "—" : r.in_domain ? "YES" : "NO"} />
      <Field label="Input completeness" value={`${fmt(t.input_completeness_pct, 1)} %`} />
      <Field label="Missing factors" value={t.missing_factors.length ? t.missing_factors.join(", ") : "none"} />
      <Field label="Prediction timestamp" value={fmtTime(r.timestamp)} />
    </dl>
  );
}

export function CrossCheck({ prediction }: { prediction: Prediction }) {
  const c = prediction.result.cross_check;
  if (!c) return <p className="text-xs text-muted-foreground">No cross-check (request did not reach model evaluation).</p>;
  const rows: [string, number | null | undefined][] = [
    ["QI-C1-vessel-type", c.qi_c1_vessel_type_pred_kg_h],
    ["QI-C1", c.qi_c1_pred_kg_h],
    ["MODEL-REAL-04 (reference)", c.model_real_04_pred_kg_h],
    ["|primary − reference|", c.delta_kg_h],
  ];
  return (
    <dl>
      {rows.map(([k, v]) => <Field key={k} label={k} value={v == null ? "not evaluated" : fmt(v, 1)} unit={v == null ? undefined : UNITS.fuelRate} />)}
    </dl>
  );
}
