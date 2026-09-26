"use client";

import { FlaskConical, Gauge } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect } from "react";
import { useHmi } from "@/components/hmi/app-shell";
import { TrendChart } from "@/components/hmi/charts";
import { CrossCheck, EnvelopeGauge, PredictionDetails, PredictionReadout, TrustBanner } from "@/components/hmi/prediction-view";
import { DataState, Field, LinkButton, PageHeader, Panel, ProvenanceTag, StateBadge } from "@/components/hmi/primitives";
import { api } from "@/lib/api";
import { fmt, fmtTime, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

const INPUT_UNITS: Record<string, string> = {
  stw_kn: UNITS.speed, sog_kn: UNITS.speed, draft_m: UNITS.length, displacement_t: UNITS.displacement,
  wind_speed_ms: UNITS.windSpeed, wave_height_m: UNITS.length, wave_period_s: "s", water_depth_m: UNITS.length,
  current_speed_ms: UNITS.windSpeed, wind_direction_deg: "°", wave_direction_deg: "°", current_direction_deg: "°",
};

export default function VesselPage() {
  const { id } = useParams<{ id: string }>();
  const { setActiveVessel, status } = useHmi();
  useEffect(() => { if (id) setActiveVessel(id); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps
  const detail = useApi(() => api.vessel(id), [id]);
  const vesselIds = status.data?.fleet_trust.map((t) => t.vessel_id) ?? [];

  return (
    <>
      <PageHeader
        title={`Vessel Detail — ${id}`}
        description="Identity, operating state, served prediction and trust for one vessel, plus a replay of its recorded telemetry."
        actions={
          <>
            <LinkButton variant="outline" href="/trust"><Gauge className="size-4" aria-hidden /> Prediction & Trust</LinkButton>
            <LinkButton href="/scenario"><FlaskConical className="size-4" aria-hidden /> Run Scenario</LinkButton>
          </>
        }
      />
      <nav aria-label="Select vessel" className="mb-3 flex gap-1">
        {vesselIds.map((v) => (
          <Link key={v} href={`/vessel/${v}`} aria-current={v === id ? "page" : undefined}
            className={cn("rounded-sm border px-2 py-1 text-xs", v === id ? "border-primary bg-accent font-semibold" : "text-muted-foreground hover:bg-accent")}>
            {v}
          </Link>
        ))}
      </nav>
      <DataState state={detail}>
        {(d) => {
          const v = d.vessel;
          const lr = d.latest_record;
          const primaryFeatures = d.model_features["QI-C1-vessel-type"] ?? [];
          return (
            <div className="grid gap-3 xl:grid-cols-3">
              <Panel title="Identity" subtitle={<>Fleet defaults <ProvenanceTag kind="ASSUMED" /></>}>
                <dl>
                  <Field label="Vessel ID" value={v.id} />
                  <Field label="Vessel type" value={humanize(v.vessel_type)} />
                  <Field label="Route" value={v.route} tag={<ProvenanceTag kind="ASSUMED" />} />
                  <Field label="Hotel load" value={fmt(v.hotel_load_kw, 0)} unit="kW" />
                  <Field label="Served by" value={d.prediction.result.model ?? "—"} />
                  <Field label="Model version" value={d.prediction.result.model_version ?? "—"} />
                  <Field label="Evaluated" value={fmtTime(d.prediction.result.timestamp)} />
                </dl>
              </Panel>

              <Panel title="Operating state" subtitle={<>Inputs sent to the model <ProvenanceTag kind="ASSUMED" title="common/fleet_defaults.py" /></>}>
                <dl>
                  <Field label="Speed through water (STW)" value={fmt(v.stw_kn, 1)} unit={UNITS.speed} />
                  <Field label="Speed over ground (SOG)" value={fmt(v.sog_kn, 1)} unit={UNITS.speed} />
                  <Field label="Draft" value={fmt(v.draft_m, 2)} unit={UNITS.length} />
                  <Field label="Displacement (loading)" value={fmt(v.displacement_t, 0)} unit={UNITS.displacement} />
                  <Field label="Wind speed" value={fmt(v.wind_speed_ms, 1)} unit={UNITS.windSpeed} />
                  <Field label="Significant wave height" value={fmt(v.wave_height_m, 1)} unit={UNITS.length} />
                  <Field label="Water depth" value={fmt(v.water_depth_m, 0)} unit={UNITS.length} />
                  <Field label="Fuel type" value={v.fuel_type.toUpperCase()} />
                </dl>
              </Panel>

              <Panel title="Prediction" subtitle={<>Production predictor <ProvenanceTag kind="MODEL" /></>} actions={<StateBadge state={d.prediction.trust.state} />}>
                <PredictionReadout prediction={d.prediction} />
                <div className="mt-3"><EnvelopeGauge trust={d.prediction.trust} /></div>
                <div className="mt-2"><PredictionDetails prediction={d.prediction} /></div>
              </Panel>

              <div className="xl:col-span-3"><TrustBanner prediction={d.prediction} /></div>

              <Panel className="xl:col-span-2" title="Fuel rate trend — dataset replay"
                subtitle={<><ProvenanceTag kind="HISTORICAL" /> {d.trend.provenance}. Last {d.trend.window_records} records, {d.trend.points.length} plotted.</>}>
                {d.trend.points.length ? <TrendChart points={d.trend.points} /> : <p className="text-sm text-muted-foreground">No recorded telemetry for this vessel.</p>}
              </Panel>

              <Panel title="Latest recorded measurement" subtitle={<><ProvenanceTag kind="MEASURED" /> {lr.provenance}</>}>
                <dl>
                  <Field label="Record timestamp" value={fmtTime(lr.timestamp)} />
                  <Field label="Observed fuel" value={fmt(lr.observed_fuel_kg_h, 1)} unit={UNITS.fuelRate} />
                  {Object.entries(lr.inputs).map(([k, val]) => (
                    <Field key={k} label={k} value={val == null ? "missing" : typeof val === "number" ? fmt(val, 2) : val} unit={val == null ? undefined : INPUT_UNITS[k]} />
                  ))}
                </dl>
              </Panel>

              <Panel className="xl:col-span-2" title="Model inputs & context" subtitle="Features actually consumed by the primary model (no feature importance is shown: none is published for these models).">
                <div className="flex flex-wrap gap-1.5">
                  {primaryFeatures.map((f) => {
                    const provided = d.prediction.input[f] !== undefined;
                    return (
                      <span key={f} className={cn("num rounded-sm border px-1.5 py-0.5 text-xs", provided ? "border-st-normal/60" : "border-st-warning/70 text-st-warning")}>
                        {f} = {provided ? String(d.prediction.input[f]) : "defaulted"}
                      </span>
                    );
                  })}
                </div>
              </Panel>
              <Panel title="Model cross-check" subtitle="All three boosters evaluated by the router">
                <CrossCheck prediction={d.prediction} />
              </Panel>
            </div>
          );
        }}
      </DataState>
    </>
  );
}
