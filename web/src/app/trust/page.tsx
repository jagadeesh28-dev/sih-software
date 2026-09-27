"use client";

import { CheckCircle2, ChevronRight, Compass, Gauge, Info, Play, RotateCcw, ShieldAlert, Sliders, Waves, Wind } from "lucide-react";
import { useState } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { CrossCheck, EnvelopeGauge, PredictionDetails } from "@/components/hmi/prediction-view";
import {
  ErrorBox, Field, Kpi, Loading, PageHeader, Panel, ProvenanceTag, StateBadge, TechnicalDetails, ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type Prediction } from "@/lib/api";
import { fmt, fmtTime, humanize, STATE_META, asHmiState, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const VESSEL_PRESETS: Record<string, { label: string; values: Record<string, any> }> = {
  "CPS_Poseidon": {
    label: "CPS Poseidon (Cruise 35,000 t)",
    values: { vessel_id: "CPS_Poseidon", vessel_type: "passenger_cruise", fuel_type: "vlsfo", stw_kn: 14.5, sog_kn: 14.5, draft_m: 7.5, displacement_t: 35000, wave_height_m: 1.0, wind_speed_ms: 5.0, water_depth_m: 50.0, coverage: "0.9" },
  },
  "CPS_Triton": {
    label: "CPS Triton (Small Cruise 12,000 t)",
    values: { vessel_id: "CPS_Triton", vessel_type: "passenger_cruise_small", fuel_type: "vlsfo", stw_kn: 14.0, sog_kn: 14.0, draft_m: 5.2, displacement_t: 12000, wave_height_m: 1.2, wind_speed_ms: 6.0, water_depth_m: 45.0, coverage: "0.9" },
  },
  "OSS_Ceto": {
    label: "OSS Ceto (Supply 4,500 t)",
    values: { vessel_id: "OSS_Ceto", vessel_type: "offshore_supply", fuel_type: "mgo", stw_kn: 12.5, sog_kn: 12.5, draft_m: 4.8, displacement_t: 4500, wave_height_m: 1.5, wind_speed_ms: 8.0, water_depth_m: 35.0, coverage: "0.9" },
  },
};

export default function PredictionPage() {
  const { activeVessel } = useHmi();
  const [selectedPreset, setSelectedPreset] = useState<string>("CPS_Poseidon");
  const [form, setForm] = useState<Record<string, any>>(VESSEL_PRESETS["CPS_Poseidon"].values);
  const [result, setResult] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (key: string) => {
    setSelectedPreset(key);
    setForm({ ...VESSEL_PRESETS[key].values });
    setResult(null);
    setError(null);
  };

  const handleInputChange = (field: string, val: string) => {
    setForm((prev) => ({ ...prev, [field]: val }));
  };

  const evaluatePrediction = async () => {
    setBusy(true);
    setError(null);
    try {
      const payload: Record<string, any> = {
        vessel_id: form.vessel_id,
        vessel_type: form.vessel_type,
        fuel_type: form.fuel_type,
        stw_kn: Number(form.stw_kn),
        sog_kn: Number(form.sog_kn || form.stw_kn),
        draft_m: Number(form.draft_m),
        displacement_t: Number(form.displacement_t),
        wave_height_m: Number(form.wave_height_m || 1.0),
        wind_speed_ms: Number(form.wind_speed_ms || 5.0),
        water_depth_m: Number(form.water_depth_m || 50.0),
        coverage: Number(form.coverage || 0.9),
      };
      const res = await api.predict(payload);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to evaluate fuel prediction.");
      setResult(null);
    } finally {
      setBusy(false);
    }
  };

  // Run initial prediction if not yet evaluated
  useState(() => {
    evaluatePrediction();
  });

  const pred = result?.result;
  const trust = result?.trust;
  const uncertainty = pred?.uncertainty;
  const fuelRate = pred?.fuel_prediction;

  return (
    <>
      <PageHeader
        title="Fuel Consumption Prediction"
        description="First-principles naval hydrodynamics combined with empirical machine-learning residual models and split conformal uncertainty calibration."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => applyPreset(selectedPreset)}>
              <RotateCcw className="size-3.5" aria-hidden /> Reset to Preset
            </Button>
          </div>
        }
      />

      {/* Preset Fast-Loader */}
      <div className="mb-3.5 flex flex-wrap items-center gap-2 border-b border-rule/60 pb-2.5">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mr-1">
          Vessel Presets:
        </span>
        {Object.entries(VESSEL_PRESETS).map(([key, item]) => (
          <button
            key={key}
            type="button"
            onClick={() => applyPreset(key)}
            className={cn(
              "rounded-sm border px-2.5 py-1 text-xs font-semibold transition-all",
              selectedPreset === key
                ? "border-primary bg-primary/10 text-foreground"
                : "border-rule/70 bg-panel text-muted-foreground hover:bg-panel-2 hover:text-foreground",
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3.5 xl:grid-cols-[380px_minmax(0,1fr)]">
        {/* Left Form: Operating Setpoints */}
        <Panel
          title="Operating Parameters"
          subtitle="Hydrodynamic dimensions & environmental conditions"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              evaluatePrediction();
            }}
            className="grid gap-2.5"
          >
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1">
                <Label htmlFor="stw_kn" className="text-xs">Speed (STW kn) *</Label>
                <Input
                  id="stw_kn"
                  type="number"
                  step="0.1"
                  value={form.stw_kn ?? ""}
                  onChange={(e) => handleInputChange("stw_kn", e.target.value)}
                  className="num h-8"
                  required
                />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="draft_m" className="text-xs">Draft (m) *</Label>
                <Input
                  id="draft_m"
                  type="number"
                  step="0.1"
                  value={form.draft_m ?? ""}
                  onChange={(e) => handleInputChange("draft_m", e.target.value)}
                  className="num h-8"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1">
                <Label htmlFor="displacement_t" className="text-xs">Displacement (t) *</Label>
                <Input
                  id="displacement_t"
                  type="number"
                  step="100"
                  value={form.displacement_t ?? ""}
                  onChange={(e) => handleInputChange("displacement_t", e.target.value)}
                  className="num h-8"
                  required
                />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="fuel_type" className="text-xs">Fuel Grade</Label>
                <select
                  id="fuel_type"
                  value={form.fuel_type ?? "vlsfo"}
                  onChange={(e) => handleInputChange("fuel_type", e.target.value)}
                  className="h-8 rounded-md border bg-input/30 px-2 text-xs"
                >
                  <option value="vlsfo">VLSFO Conventional</option>
                  <option value="mgo">MGO Marine Gas Oil</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1">
                <Label htmlFor="wave_height_m" className="text-xs">Wave Height Hs (m)</Label>
                <Input
                  id="wave_height_m"
                  type="number"
                  step="0.1"
                  value={form.wave_height_m ?? ""}
                  onChange={(e) => handleInputChange("wave_height_m", e.target.value)}
                  className="num h-8"
                />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="wind_speed_ms" className="text-xs">Wind Speed (m/s)</Label>
                <Input
                  id="wind_speed_ms"
                  type="number"
                  step="0.5"
                  value={form.wind_speed_ms ?? ""}
                  onChange={(e) => handleInputChange("wind_speed_ms", e.target.value)}
                  className="num h-8"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1">
                <Label htmlFor="vessel_type" className="text-xs">Naval Type</Label>
                <select
                  id="vessel_type"
                  value={form.vessel_type ?? "passenger_cruise"}
                  onChange={(e) => handleInputChange("vessel_type", e.target.value)}
                  className="h-8 rounded-md border bg-input/30 px-2 text-xs"
                >
                  <option value="passenger_cruise">Passenger Cruise</option>
                  <option value="passenger_cruise_small">Passenger Cruise (Small)</option>
                  <option value="offshore_supply">Offshore Supply</option>
                </select>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="coverage" className="text-xs">Confidence Band</Label>
                <select
                  id="coverage"
                  value={form.coverage ?? "0.9"}
                  onChange={(e) => handleInputChange("coverage", e.target.value)}
                  className="h-8 rounded-md border bg-input/30 px-2 text-xs"
                >
                  <option value="0.9">90% Nominal</option>
                  <option value="0.95">95% Conservative</option>
                </select>
              </div>
            </div>

            <Button type="submit" disabled={busy} className="mt-2 w-full">
              <Play className="size-4 mr-1.5" aria-hidden />
              {busy ? "Calculating Hydrodynamics..." : "Calculate Fuel Prediction"}
            </Button>
          </form>
        </Panel>

        {/* Right Panel: Output & Confidence Range */}
        <div className="grid content-start gap-3.5">
          {error && <ErrorBox error={error} />}
          {busy && <Loading label="Evaluating physics resistance and ML residual booster..." />}

          {result && !busy && (
            <>
              {/* Section 6: Fallback Notice if active */}
              {trust?.fallback && (
                <div role="status" className="rounded-md border border-st-fallback/70 bg-st-fallback/10 p-3.5 text-xs">
                  <div className="flex items-center justify-between border-b border-st-fallback/30 pb-2">
                    <span className="font-bold text-st-fallback uppercase tracking-wide">
                      Prediction Source: Reference Model ({trust.fallback_label ?? "MODEL-REAL-04"})
                    </span>
                    <ToneChip tone="fallback">FALLBACK ACTIVE</ToneChip>
                  </div>
                  <div className="mt-2 grid gap-1.5 sm:grid-cols-2 text-muted-foreground">
                    <div>
                      <span className="font-medium text-foreground">Status:</span> Fallback Model Served
                    </div>
                    <div>
                      <span className="font-medium text-foreground">Action:</span> Review recommended before dispatch commitment
                    </div>
                    <div className="sm:col-span-2">
                      <span className="font-medium text-foreground">Reason:</span> Input outside primary model operating envelope; routed to calibrated reference anchor.
                    </div>
                  </div>
                </div>
              )}

              {/* Primary Operator Result Card */}
              <div className="rounded-md border border-rule/70 bg-panel p-4 shadow-xs">
                <div className="flex items-center justify-between border-b border-rule/60 pb-3">
                  <div>
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Predicted Fuel Consumption Rate
                    </span>
                    <div className="num mt-1 flex items-baseline gap-2">
                      <span className="text-4xl font-bold tracking-tight text-foreground">
                        {fuelRate != null ? fmt(fuelRate, 1) : "—"}
                      </span>
                      <span className="text-sm font-medium text-muted-foreground">
                        {UNITS.fuelRate}
                      </span>
                      {fuelRate != null && (
                        <span className="num ml-3 text-xs text-primary font-semibold">
                          ≈ {fmt((fuelRate * 24) / 1000, 1)} tonnes/day
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
                      Operating Envelope
                    </span>
                    <StateBadge state={trust?.state ?? "NORMAL"} size="lg" />
                  </div>
                </div>

                {/* Expected Range (Section 3 Step 3) */}
                {uncertainty && (
                  <div className="mt-4 rounded-md border border-rule/50 bg-panel-2/40 p-3">
                    <div className="flex items-center justify-between text-xs font-medium">
                      <span className="text-muted-foreground">
                        Expected Range ({Math.round(uncertainty.coverage * 100)}% Finite-Sample Conformal Interval)
                      </span>
                      <span className="num font-bold text-foreground">
                        [{fmt(uncertainty.lower_bound_kg_h, 0)} — {fmt(uncertainty.upper_bound_kg_h, 0)}] {UNITS.fuelRate}
                      </span>
                    </div>

                    {/* Visual Range Indicator Bar */}
                    <div className="relative mt-2.5 h-3 w-full rounded-sm bg-rule/40 overflow-hidden">
                      <div
                        className="absolute inset-y-0 rounded-sm bg-primary/70"
                        style={{
                          left: "25%",
                          width: "50%",
                        }}
                      />
                      <div
                        className="absolute inset-y-[-2px] w-1.5 rounded-full bg-foreground shadow-xs"
                        style={{ left: "50%" }}
                      />
                    </div>
                    <div className="mt-1.5 flex justify-between text-[10px] text-muted-foreground num">
                      <span>Lower Bound: {fmt(uncertainty.lower_bound_kg_h, 0)}</span>
                      <span className="text-primary font-medium">Point Estimate: {fuelRate ? fmt(fuelRate, 0) : "—"}</span>
                      <span>Upper Bound: {fmt(uncertainty.upper_bound_kg_h, 0)}</span>
                    </div>
                  </div>
                )}

                {/* Section 3 Step 3: Operational Status Badges */}
                <div className="mt-3.5 grid grid-cols-2 gap-2 text-xs text-muted-foreground sm:grid-cols-4 border-t border-rule/50 pt-3">
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="size-3.5 text-st-normal" aria-hidden />
                    <span>Method: <strong className="text-foreground">Physics + ML Residual</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="size-3.5 text-st-normal" aria-hidden />
                    <span>Confidence: <strong className={cn(
                      trust?.state === "NORMAL" ? "text-st-normal" : trust?.state === "WARNING" ? "text-st-warning" : "text-st-fallback"
                    )}>
                      {trust?.state === "NORMAL" ? "Normal" : trust?.state === "WARNING" ? "Review" : "Limited"}
                    </strong></span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="size-3.5 text-st-normal" aria-hidden />
                    <span>Data Status: <strong className="text-foreground">{result ? "Current" : "Unavailable"}</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="size-3.5 text-st-normal" aria-hidden />
                    <span>Naval Scaling: <strong className="text-foreground">Hydrodynamic Basis</strong></span>
                  </div>
                </div>
              </div>

              {/* Progressive Disclosure: Scientific & Mathematical Transparency */}
              <TechnicalDetails title="Scientific Transparency & Diagnostics (SIH Jury / Researcher Inspection)">
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-sm border border-rule/60 bg-panel p-3">
                    <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Multi-Model Cross-Check</div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Authoritative evaluation across Primary Naval Booster, Base Booster, and Full Anchor:
                    </p>
                    <div className="mt-2">
                      <CrossCheck prediction={result} />
                    </div>
                  </div>

                  <div className="rounded-sm border border-rule/60 bg-panel p-3">
                    <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Operational Envelope Distance</div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Convex envelope metric (d_env) against sea-trial training bounds:
                    </p>
                    <div className="mt-2">
                      {trust && <EnvelopeGauge trust={trust} />}
                    </div>
                  </div>
                </div>

                <div className="mt-3 rounded-sm border border-rule/60 bg-panel p-3">
                  <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider mb-2">Model Features & Contract Verifications</div>
                  <PredictionDetails prediction={result} />
                </div>
              </TechnicalDetails>
            </>
          )}
        </div>
      </div>
    </>
  );
}
