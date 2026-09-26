"use client";

import { useCallback, useEffect, useState } from "react";

// ------------------------------------------------------------------ data hook

export interface Loadable<T> {
  data: T | undefined;
  error: string | undefined;
  loading: boolean;
  reload: () => void;
}

/** Fetch on mount/deps change; optional polling. Errors are kept, never replaced with fake data. */
export function useApi<T>(fn: () => Promise<T>, deps: unknown[], pollMs?: number): Loadable<T> {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({ loading: true });
  const [tick, setTick] = useState(0);
  const key = JSON.stringify(deps);

  useEffect(() => {
    let live = true;
    const run = () => fn()
      .then((d) => { if (live) setState({ data: d, error: undefined, loading: false }); })
      .catch((e: Error) => { if (live) setState((s) => ({ ...s, error: e.message, loading: false })); });
    run();
    const id = pollMs ? setInterval(run, pollMs) : undefined;
    return () => { live = false; if (id) clearInterval(id); };
    // `fn` is re-created every render; `key` captures the inputs it closes over.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, tick, pollMs]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { data: state.data, error: state.error, loading: state.loading, reload };
}

// ------------------------------------------------------------------ units + formatting

export const UNITS = {
  fuelRate: "kg/h",
  speed: "kn",
  mass: "t",
  ghg: "tCO2e",
  energy: "MJ/h",
  currency: "USD",
  hours: "h",
  length: "m",
  distance: "nm",
  windSpeed: "m/s",
  displacement: "t",
} as const;

export function fmt(v: number | null | undefined, digits = 1): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function fmtUsd(v: number | null | undefined, digits = 0): string {
  return v === null || v === undefined ? "—" : `$${fmt(v, digits)}`;
}

export function fmtTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : `${d.toISOString().slice(0, 19).replace("T", " ")} UTC`;
}

export function humanize(s: string | null | undefined): string {
  return (s ?? "—").replace(/_/g, " ");
}

// ------------------------------------------------------------------ operator state catalogue

export type HmiState =
  | "NORMAL" | "WARNING" | "OOD" | "FALLBACK" | "INVALID_INPUT"
  | "MISSING_FACTOR" | "CONSTRAINT_FAILURE" | "RUNTIME_FAILURE";

export type Tone = "normal" | "warning" | "ood" | "fallback" | "info" | "demo";

export const STATE_META: Record<HmiState, { label: string; tone: Tone; severity: number; explanation: string; action: string }> = {
  NORMAL: {
    label: "NORMAL", tone: "normal", severity: 0,
    explanation: "Input inside the training envelope; primary model served the prediction.",
    action: "No action required. Review the prediction interval before use.",
  },
  WARNING: {
    label: "WARNING", tone: "warning", severity: 1,
    explanation: "Prediction served, but the router flagged elevated uncertainty or an operating state near the training envelope.",
    action: "Use with caution; widen operational margins and check inputs.",
  },
  MISSING_FACTOR: {
    label: "MISSING FACTOR", tone: "warning", severity: 1,
    explanation: "One or more optional model inputs were absent and filled with serving-contract defaults.",
    action: "Supply the missing measurements if available and re-run.",
  },
  FALLBACK: {
    label: "FALLBACK", tone: "fallback", severity: 2,
    explanation: "The primary model was bypassed; the reference model (MODEL-REAL-04) or physics served the value.",
    action: "Treat as reduced-confidence advisory; investigate the reason shown.",
  },
  CONSTRAINT_FAILURE: {
    label: "CONSTRAINT FAILURE", tone: "fallback", severity: 2,
    explanation: "The optimizer's best plan violates at least one hard constraint.",
    action: "Do not dispatch. Adjust weights, budget or demands and re-run.",
  },
  INVALID_INPUT: {
    label: "INVALID INPUT", tone: "ood", severity: 3,
    explanation: "Input failed the production feature contract (missing required fields or physically impossible values).",
    action: "Correct the input. No prediction is produced.",
  },
  RUNTIME_FAILURE: {
    label: "RUNTIME FAILURE", tone: "ood", severity: 3,
    explanation: "A model or physics component raised an error during inference or optimization.",
    action: "Rely on the stated fallback only; report the error to engineering.",
  },
  OOD: {
    label: "OUT OF DOMAIN", tone: "ood", severity: 4,
    explanation: "Operating state lies outside the training envelope; ML output is not trusted.",
    action: "Do not act on the ML value. Use physics-based judgement and seamanship.",
  },
};

export function asHmiState(s: string): HmiState {
  return (s in STATE_META ? s : "RUNTIME_FAILURE") as HmiState;
}

export const TONE_CLASS: Record<Tone, { text: string; border: string; bg: string; solid: string }> = {
  normal: { text: "text-st-normal", border: "border-st-normal/60", bg: "bg-st-normal/10", solid: "bg-st-normal text-background" },
  warning: { text: "text-st-warning", border: "border-st-warning/70", bg: "bg-st-warning/10", solid: "bg-st-warning text-background" },
  ood: { text: "text-st-ood", border: "border-st-ood", bg: "bg-st-ood/15", solid: "bg-st-ood text-white" },
  fallback: { text: "text-st-fallback", border: "border-st-fallback/70", bg: "bg-st-fallback/10", solid: "bg-st-fallback text-background" },
  info: { text: "text-st-info", border: "border-st-info/60", bg: "bg-st-info/10", solid: "bg-st-info text-background" },
  demo: { text: "text-st-demo", border: "border-st-demo/70", bg: "bg-st-demo/10", solid: "bg-st-demo text-background" },
};
