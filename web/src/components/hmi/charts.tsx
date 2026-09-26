"use client";

import {
  Area, Bar, BarChart, CartesianGrid, ComposedChart, LabelList, Legend, Line, ResponsiveContainer, Scatter,
  ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import type { ParetoPoint, TrendPoint } from "@/lib/api";
import { fmt, fmtUsd } from "@/lib/hmi";

const AXIS = { stroke: "var(--muted-foreground)", fontSize: 11 };
const GRID = <CartesianGrid stroke="var(--rule)" strokeDasharray="2 4" />;
const TOOLTIP = {
  contentStyle: { background: "var(--popover)", border: "1px solid var(--rule)", borderRadius: 4, fontSize: 12 },
  labelStyle: { color: "var(--muted-foreground)" },
};

export function TrendChart({ points }: { points: TrendPoint[] }) {
  const data = points.map((p) => ({
    t: p.timestamp.slice(5, 16).replace("T", " "),
    observed: p.observed_kg_h,
    predicted: p.predicted_kg_h,
    band: p.lower_kg_h != null && p.upper_kg_h != null ? [p.lower_kg_h, p.upper_kg_h] : null,
    stw: p.stw_kn,
  }));
  return (
    <div className="h-72 w-full" role="img" aria-label="Observed versus predicted fuel rate with 90% interval, and speed through water">
      <ResponsiveContainer>
        <ComposedChart data={data} margin={{ top: 8, right: 8, left: 4, bottom: 0 }}>
          {GRID}
          <XAxis dataKey="t" {...AXIS} minTickGap={48} />
          <YAxis yAxisId="fuel" {...AXIS} width={56} label={{ value: "kg/h", angle: -90, position: "insideLeft", fill: "var(--muted-foreground)", fontSize: 11 }} />
          <YAxis yAxisId="stw" orientation="right" {...AXIS} width={36} label={{ value: "kn", angle: 90, position: "insideRight", fill: "var(--muted-foreground)", fontSize: 11 }} />
          <Tooltip {...TOOLTIP} formatter={(v) => (Array.isArray(v) ? `${fmt(v[0] as number, 0)} – ${fmt(v[1] as number, 0)}` : fmt(v as number, 1))} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area yAxisId="fuel" dataKey="band" name="90% interval (kg/h)" stroke="none" fill="var(--chart-1)" fillOpacity={0.15} isAnimationActive={false} />
          <Line yAxisId="fuel" dataKey="observed" name="Observed fuel (kg/h)" stroke="var(--chart-3)" dot={false} strokeWidth={1.5} isAnimationActive={false} />
          <Line yAxisId="fuel" dataKey="predicted" name="Served prediction (kg/h)" stroke="var(--chart-1)" dot={false} strokeWidth={1.5} strokeDasharray="4 2" isAnimationActive={false} />
          <Line yAxisId="stw" dataKey="stw" name="STW (kn)" stroke="var(--chart-5)" dot={false} strokeWidth={1} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ParetoChart({ points, selected, onSelect }: {
  points: ParetoPoint[]; selected: string | null; onSelect: (id: string) => void;
}) {
  const data = points.map((p) => ({ ...p, x: p.cost_usd, y: p.ghg_tonnes }));
  return (
    <div className="h-80 w-full" role="img" aria-label="Operational cost versus lifecycle GHG for feasible stored solutions">
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 16, right: 24, left: 8, bottom: 16 }}>
          {GRID}
          <XAxis type="number" dataKey="x" name="OPEX" {...AXIS} domain={["auto", "auto"]} tickFormatter={(v) => fmtUsd(v)}
            label={{ value: "Operational cost (USD)", position: "insideBottom", offset: -8, fill: "var(--muted-foreground)", fontSize: 11 }} />
          <YAxis type="number" dataKey="y" name="WtW GHG" {...AXIS} domain={["auto", "auto"]} width={56}
            label={{ value: "Lifecycle WtW GHG (tCO2e)", angle: -90, position: "insideLeft", fill: "var(--muted-foreground)", fontSize: 11 }} />
          <ZAxis range={[120, 120]} />
          <Tooltip {...TOOLTIP} cursor={{ strokeDasharray: "3 3" }} formatter={(v, n) => (n === "OPEX" ? fmtUsd(v as number) : `${fmt(v as number, 2)} tCO2e`)} />
          <Scatter
            data={data}
            fill="var(--chart-1)"
            isAnimationActive={false}
            onClick={(d: unknown) => onSelect((d as { solution_id: string }).solution_id)}
            shape={(props: unknown) => {
              const { cx, cy, payload } = props as { cx: number; cy: number; payload: ParetoPoint };
              const on = payload.solution_id === selected;
              return (
                <g style={{ cursor: "pointer" }}>
                  <rect x={cx - 6} y={cy - 6} width={12} height={12} transform={`rotate(45 ${cx} ${cy})`}
                    fill={on ? "var(--chart-3)" : "var(--chart-1)"} stroke={on ? "var(--foreground)" : "none"} strokeWidth={2} />
                </g>
              );
            }}
          >
            <LabelList dataKey="solution_id" position="top" fill="var(--foreground)" fontSize={11} />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function HBarChart({ rows, unit, digits = 1, label }: {
  rows: { name: string; value: number; scenario: boolean }[]; unit: string; digits?: number; label: string;
}) {
  return (
    <div className="w-full" style={{ height: 36 + rows.length * 30 }} role="img" aria-label={label}>
      <ResponsiveContainer>
        <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 72, left: 8, bottom: 4 }}>
          {GRID}
          <XAxis type="number" {...AXIS} tickFormatter={(v) => fmt(v, 0)} />
          <YAxis type="category" dataKey="name" {...AXIS} width={200} />
          <Tooltip {...TOOLTIP} formatter={(v) => `${fmt(v as number, digits)} ${unit}`} />
          <Bar dataKey="value" isAnimationActive={false}
            shape={(props: unknown) => {
              const { x, y, width, height, payload } = props as { x: number; y: number; width: number; height: number; payload: { scenario: boolean } };
              return <rect x={x} y={y + 3} width={width} height={height - 6}
                fill={payload.scenario ? "url(#hatch)" : "var(--chart-1)"} stroke="var(--chart-1)" />;
            }}>
            <LabelList dataKey="value" position="right" fill="var(--foreground)" fontSize={11} formatter={(v: unknown) => `${fmt(v as number, digits)} ${unit}`} />
          </Bar>
          <defs>
            <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="6" height="6" fill="var(--panel-2)" />
              <line x1="0" y1="0" x2="0" y2="6" stroke="var(--chart-4)" strokeWidth="3" />
            </pattern>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
