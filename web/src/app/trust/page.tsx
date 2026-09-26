"use client";

import { Play } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { CrossCheck, EnvelopeGauge, PredictionReadout, TrustBanner } from "@/components/hmi/prediction-view";
import { ErrorBox, Field, Loading, Notice, PageHeader, Panel, ProvenanceTag, StateBadge, ToneChip } from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type Prediction } from "@/lib/api";
import { fmt, fmtTime, humanize, STATE_META, asHmiState, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const NUMERIC: { key: string; label: string; unit: string }[] = [
  { key: "stw_kn", label: "STW", unit: UNITS.speed },
  { key: "sog_kn", label: "SOG", unit: UNITS.speed },
  { key: "draft_m", label: "Draft", unit: UNITS.length },
  { key: "displacement_t", label: "Displacement", unit: UNITS.displacement },
  { key: "wind_speed_ms", label: "Wind speed", unit: UNITS.windSpeed },
  { key: "wave_height_m", label: "Wave height (Hs)", unit: UNITS.length },
  { key: "wave_period_s", label: "Wave period", unit: "s" },
  { key: "water_depth_m", label: "Water depth", unit: UNITS.length },
];
const REQUIRED = new Set(["stw_kn", "draft_m", "displacement_t"]);
const VESSEL_TYPES = ["passenger_cruise", "passenger_cruise_small", "offshore_supply"];

type Form = Record<string, string>;
type Source = { label: string; kind: "ASSUMED" | "MEASURED" | "SCENARIO" };

export default function TrustPage() {
  const { activeVessel } = useHmi();
  const fleet = useApi(api.fleet, []);
  const [form, setForm] = useState<Form>({ vessel_type: "passenger_cruise", fuel_type: "vlsfo", coverage: "0.9" });
  const [source, setSource] = useState<Source>({ label: "Manual entry", kind: "SCENARIO" });
  const [result, setResult] = useState<Prediction>();
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);

  const load = (values: Record<string, unknown>, src: Source) => {
    const f: Form = { coverage: form.coverage };
    for (const k of [...NUMERIC.map((n) => n.key), "vessel_type", "fuel_type", "vessel_id"]) {
      if (values[k] != null) f[k] = String(values[k]);
    }
    setForm(f);
    setSource(src);
  };

  const loadMeasured = async (id: string) => {
    try {
      const d = await api.vessel(id);
      load({ ...d.latest_record.inputs, vessel_id: id }, { label: `${id} recorded ${fmtTime(d.latest_record.timestamp)}`, kind: "MEASURED" });
    } catch (e) { setError((e as Error).message); }
  };

  const submit = async () => {
    setBusy(true); setError(undefined);
    const body: Record<string, unknown> = { coverage: Number(form.coverage) };
    for (const [k, v] of Object.entries(form)) {
      if (k === "coverage" || v === "") continue;
      body[k] = NUMERIC.some((n) => n.key === k) ? Number(v) : v;
    }
    try { setResult(await api.predict(body)); } catch (e) { setError((e as Error).message); setResult(undefined); }
    finally { setBusy(false); }
  };

  const set = (k: string, v: string) => { setForm((f) => ({ ...f, [k]: v })); setSource({ label: "Edited by operator", kind: "SCENARIO" }); };
  const severity = result ? STATE_META[asHmiState(result.trust.state)].severity : 0;

  return (
    <>
      <PageHeader title="Prediction & Trust" description="Submit an operating point to the production predictor and inspect exactly how far the result can be trusted. Every value is returned by the backend router." />
      <div className="grid gap-3 xl:grid-cols-[380px_minmax(0,1fr)]">
        <Panel title="Operating point" subtitle={<>Source: {source.label} <ProvenanceTag kind={source.kind} /></>}>
          <div className="mb-3 grid gap-1.5">
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">Load preset</span>
            <div className="flex flex-wrap gap-1.5">
              {fleet.data?.vessels.map((r) => (
                <Button key={r.vessel.id} size="sm" variant="outline"
                  onClick={() => load({ ...r.prediction.input }, { label: `${r.vessel.id} fleet default`, kind: "ASSUMED" })}>
                  {r.vessel.id} default
                </Button>
              ))}
              <Button size="sm" variant="outline" onClick={() => loadMeasured(activeVessel)}>{activeVessel} latest measured</Button>
            </div>
            {fleet.error && <p className="text-xs text-st-ood">Presets unavailable: {fleet.error}</p>}
          </div>
          <form className="grid grid-cols-2 gap-2" onSubmit={(e) => { e.preventDefault(); submit(); }}>
            {NUMERIC.map((n) => (
              <div key={n.key} className="grid gap-1">
                <Label htmlFor={n.key} className="text-xs">
                  {n.label} ({n.unit}){REQUIRED.has(n.key) && <span className="text-st-warning"> *</span>}
                </Label>
                <Input id={n.key} inputMode="decimal" value={form[n.key] ?? ""} placeholder="not provided"
                  onChange={(e) => set(n.key, e.target.value)} className="num h-8" />
              </div>
            ))}
            <div className="grid gap-1">
              <Label htmlFor="vessel_type" className="text-xs">Vessel type</Label>
              <select id="vessel_type" value={form.vessel_type ?? ""} onChange={(e) => set("vessel_type", e.target.value)}
                className="h-8 w-full rounded-md border bg-input/30 px-2 text-sm">
                {VESSEL_TYPES.map((v) => <option key={v} value={v}>{humanize(v)}</option>)}
                <option value="bulk_carrier">bulk carrier (unsupported — tests fallback)</option>
              </select>
            </div>
            <div className="grid gap-1">
              <Label htmlFor="fuel_type" className="text-xs">Fuel type</Label>
              <select id="fuel_type" value={form.fuel_type ?? ""} onChange={(e) => set("fuel_type", e.target.value)}
                className="h-8 w-full rounded-md border bg-input/30 px-2 text-sm">
                <option value="vlsfo">VLSFO</option>
                <option value="mgo">MGO</option>
              </select>
            </div>
            <div className="grid gap-1">
              <Label htmlFor="coverage" className="text-xs">Interval coverage</Label>
              <select id="coverage" value={form.coverage} onChange={(e) => { const coverage = e.target.value; setForm((f) => ({ ...f, coverage })); }}
                className="h-8 w-full rounded-md border bg-input/30 px-2 text-sm">
                <option value="0.9">90 %</option>
                <option value="0.95">95 %</option>
              </select>
            </div>
            <div className="col-span-2 mt-1 flex items-center justify-between">
              <span className="text-[11px] text-muted-foreground"><span className="text-st-warning">*</span> required by the serving contract</span>
              <Button type="submit" disabled={busy}><Play className="size-4" aria-hidden /> {busy ? "Evaluating…" : "Evaluate"}</Button>
            </div>
          </form>
        </Panel>

        <div className="grid content-start gap-3">
          {error && <ErrorBox error={error} />}
          {busy && <Loading label="Evaluating on the production predictor…" />}
          {!result && !busy && !error && (
            <Notice title="Awaiting input">Load a preset or enter an operating point, then press Evaluate. Leave optional fields blank to test missing-factor handling.</Notice>
          )}
          {result && (
            <>
              <TrustBanner prediction={result} />
              <div className={cn("grid gap-3 lg:grid-cols-3", severity >= 3 && "rounded-md ring-2 ring-st-ood/60")}>
                <Panel title="Model ID" className="lg:col-span-1">
                  <div className="num text-lg font-semibold">{result.result.model ?? "none"}</div>
                  <div className="mt-1 text-xs text-muted-foreground">version {result.result.model_version ?? "—"} · source {humanize(result.result.prediction_source)}</div>
                </Panel>
                <Panel title="Prediction" className="lg:col-span-2" actions={<StateBadge state={result.trust.state} />}>
                  <PredictionReadout prediction={result} />
                </Panel>
                <Panel title="Confidence">
                  <div className="text-lg font-semibold">{result.result.confidence}</div>
                  <div className="text-xs text-muted-foreground">as assigned by the serving router</div>
                </Panel>
                <Panel title="Prediction interval">
                  {result.result.uncertainty ? (
                    <dl>
                      <Field label="Lower bound" value={fmt(result.result.uncertainty.lower_bound_kg_h, 1)} unit={UNITS.fuelRate} />
                      <Field label="Upper bound" value={fmt(result.result.uncertainty.upper_bound_kg_h, 1)} unit={UNITS.fuelRate} />
                      <Field label="Width" value={fmt(result.result.uncertainty.interval_width_kg_h, 1)} unit={UNITS.fuelRate} />
                      <Field label="High uncertainty flag" value={result.result.uncertainty.is_high_uncertainty ? "YES" : "NO"} />
                    </dl>
                  ) : <p className="text-sm text-muted-foreground">No interval — no prediction was produced.</p>}
                </Panel>
                <Panel title="Fallback state">
                  {result.trust.fallback
                    ? <ToneChip tone="fallback" className="text-sm">{result.trust.fallback_label}</ToneChip>
                    : <span className="text-sm">{result.result.routing_status === "REJECT" ? "NONE — request rejected, no model served" : "NONE — primary model path"}</span>}
                  <p className="mt-2 text-xs text-muted-foreground">Router status: {humanize(result.result.routing_status)}</p>
                </Panel>
                <Panel title="OOD state" className="lg:col-span-2">
                  <EnvelopeGauge trust={result.trust} />
                  <p className="mt-2 text-sm"><span className="font-semibold">OOD reason:</span> {result.trust.reason ?? "none reported"}</p>
                </Panel>
                <Panel title="Data validity & completeness">
                  <dl>
                    <Field label="Validity" value={result.trust.state === "INVALID_INPUT" ? "REJECTED" : "PASSED CONTRACT"} />
                    <Field label="Input completeness" value={`${fmt(result.trust.input_completeness_pct, 1)} %`} />
                    <Field label="Missing factors" value={result.trust.missing_factors.length || "0"} />
                  </dl>
                  {result.trust.missing_factors.length > 0 && (
                    <p className="mt-2 text-xs text-st-warning">{result.trust.missing_factors.join(", ")} — {result.trust.missing_factor_note}</p>
                  )}
                </Panel>
                <Panel title="Model cross-check" className="lg:col-span-2"><CrossCheck prediction={result} /></Panel>
                <Panel title="Timestamp"><div className="num text-sm">{fmtTime(result.result.timestamp)}</div></Panel>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
