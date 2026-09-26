/**
 * Typed, runtime-validated client for the Egreen Quanta API (api/main.py).
 * Every response is parsed with zod; a contract mismatch is surfaced as an error,
 * never silently rendered. No scientific values are computed in the frontend.
 */
import { z } from "zod";

const num = z.number();
const nnum = z.number().nullable();

export const TrustStateSchema = z.enum([
  "NORMAL", "WARNING", "OOD", "FALLBACK", "INVALID_INPUT", "RUNTIME_FAILURE",
]);
export type TrustState = z.infer<typeof TrustStateSchema>;

const Uncertainty = z.looseObject({
  lower_bound_kg_h: num,
  upper_bound_kg_h: num,
  interval_width_kg_h: num,
  coverage: num,
  is_high_uncertainty: z.boolean().optional(),
});

export const ServingResultSchema = z.looseObject({
  fuel_prediction: nnum,
  prediction_source: z.string(),
  confidence: z.string(),
  uncertainty: Uncertainty.nullable().optional(),
  model: z.string().optional(),
  model_version: z.string().optional(),
  routing_status: z.string(),
  in_domain: z.boolean().optional(),
  envelope_distance: nnum.optional(),
  cross_check: z.record(z.string(), z.number().nullable()).nullable().optional(),
  warning: z.string().nullable().optional(),
  timestamp: z.string().optional(),
});

export const TrustSchema = z.looseObject({
  state: TrustStateSchema,
  fallback: z.boolean(),
  fallback_label: z.string().nullable(),
  ood_band: z.string(),
  envelope_distance: nnum.optional(),
  thresholds: z.object({ warning: num, ood: num, reject: num }),
  reason: z.string().nullable(),
  missing_factors: z.array(z.string()),
  input_completeness_pct: num,
  missing_factor_note: z.string(),
});
export type Trust = z.infer<typeof TrustSchema>;

export const PredictionSchema = z.object({
  input: z.record(z.string(), z.unknown()),
  result: ServingResultSchema,
  trust: TrustSchema,
});
export type Prediction = z.infer<typeof PredictionSchema>;

const VesselSchema = z.looseObject({
  id: z.string(),
  name: z.string(),
  vessel_type: z.string(),
  fuel_type: z.string(),
  stw_kn: num,
  sog_kn: num,
  draft_m: num,
  displacement_t: num,
  wind_speed_ms: num,
  wave_height_m: num,
  water_depth_m: num,
  hotel_load_kw: num,
  route: z.string(),
});
export type Vessel = z.infer<typeof VesselSchema>;

const FleetTrust = z.object({
  vessel_id: z.string(),
  state: TrustStateSchema,
  fallback: z.boolean(),
  fallback_label: z.string().nullable(),
  ood_band: z.string(),
});

const EventSchema = z.looseObject({ event_id: z.string(), timestamp: z.string(), kind: z.string() });
export type AuditEvent = z.infer<typeof EventSchema>;

export const StatusSchema = z.object({
  server_time: z.string(),
  data_mode: z.string(),
  live_feed_connected: z.boolean(),
  data_freshness: z.record(z.string(), z.string()),
  data_freshness_note: z.string(),
  fleet_count: num,
  model: z.looseObject({
    primary: z.string(),
    reference_anchor: z.string(),
    serving_version: z.string(),
    models: z.record(z.string(), z.looseObject({ version: z.string().nullable().optional() })),
  }),
  evaluator_ready: z.boolean(),
  evaluator_error: z.string().nullable(),
  session_events: num,
  fleet_trust: z.array(FleetTrust),
  last_recommendation: EventSchema.nullable(),
  last_trust: TrustSchema.nullable(),
});
export type Status = z.infer<typeof StatusSchema>;

export const FleetSchema = z.object({
  generated_at: z.string(),
  kpis: z.object({
    vessels: num,
    vessels_with_prediction: num,
    predicted_fuel_kg_h: num,
    cost_usd_per_h: num,
    wtw_tco2e_per_h: num,
    non_normal: num,
  }),
  vessels: z.array(z.object({
    vessel: VesselSchema,
    provenance: z.string(),
    prediction: PredictionSchema,
    economics: z.object({ cost_usd_per_h: num, wtw_tco2e_per_h: num, basis: z.string() }).nullable(),
    schedule: z.null(),
    schedule_note: z.string(),
  })),
});
export type Fleet = z.infer<typeof FleetSchema>;

const TrendPoint = z.object({
  timestamp: z.string(),
  stw_kn: nnum,
  observed_kg_h: nnum,
  predicted_kg_h: nnum,
  lower_kg_h: nnum,
  upper_kg_h: nnum,
  source: z.string().nullable(),
  routing: z.string().nullable(),
});
export type TrendPoint = z.infer<typeof TrendPoint>;

const LatestRecord = z.object({
  timestamp: z.string(),
  inputs: z.record(z.string(), z.union([z.number(), z.string(), z.null()])),
  observed_fuel_kg_h: nnum,
  provenance: z.string(),
});

export const VesselDetailSchema = z.object({
  vessel: VesselSchema,
  prediction: PredictionSchema,
  latest_record: LatestRecord,
  trend: z.object({ provenance: z.string(), window_records: num, points: z.array(TrendPoint) }),
  model_features: z.record(z.string(), z.array(z.string())),
  physical_bounds: z.record(z.string(), z.tuple([num, num])),
});
export type VesselDetail = z.infer<typeof VesselDetailSchema>;

export const VoyageSchema = z.object({
  fuel_type: z.string(),
  voyage_hours: num,
  fuel_t: num,
  fuel_rate_kg_h: num,
  berth: z.lazy(() => BerthSchema),
  cost: z.object({
    total_usd: num, fuel_usd: num, carbon_usd: num, shore_power_usd: num,
    schedule_penalty_usd: num, fueleu_penalty_usd: num,
  }),
  ghg: z.object({ wtw_tco2e: num, wtt_tco2e: num, ttw_tco2e: num, methane_slip_tco2e: num }),
  schedule: z.object({ delay_h: num, deadline_h: num }),
  feasible: z.boolean(),
});
export type Voyage = z.infer<typeof VoyageSchema>;

/** Berth phase as computed by the backend: shore electricity OR onboard generation, never both. */
const BerthSchema = z.object({
  source: z.enum(["SHORE POWER", "ONBOARD GENERATION", "NONE"]),
  hours: num,
  hotel_load_kw: num,
  energy_kwh: num,
  fuel_t: num,
  cost_usd: num,
  ghg_tco2e: num,
});
export type Berth = z.infer<typeof BerthSchema>;

const FuelAssumptions = z.looseObject({
  name: z.string(),
  lhv_mj_kg: num,
  price_usd_per_tonne: num,
  wtt_ghg_g_co2e_mj: nnum.optional(),
  ttw_co2_g_per_g_fuel: nnum.optional(),
  methane_slip_fraction: nnum.optional(),
  source: z.string().nullable().optional(),
  confidence: z.string().nullable().optional(),
});
export type FuelAssumptions = z.infer<typeof FuelAssumptions>;

const ConfigMeta = z.looseObject({
  fuels_config: z.string(),
  fuels_config_sha256: z.string(),
  carbon_price_usd_per_tco2: num,
  demurrage_usd_per_h: num,
  shore_power_tariff_usd_per_kwh: num,
  shore_power_grid_factor_g_co2e_per_kwh: num,
  berth_sfoc_kg_per_kwh: num,
  berth_sfoc_provenance: z.string(),
});
export type ConfigMeta = z.infer<typeof ConfigMeta>;

export const ScenarioSchema = z.object({
  scenario_id: z.string(),
  prediction: PredictionSchema,
  voyage: VoyageSchema.nullable(),
  provenance: z.record(z.string(), z.string()),
  basis: z.string(),
  unsupported_inputs: z.array(z.string()),
  assumptions: ConfigMeta.extend({ fuel: FuelAssumptions, hotel_load_kw: num, hotel_load_provenance: z.string() }),
});
export type Scenario = z.infer<typeof ScenarioSchema>;

export const FuelsSchema = z.object({
  vessel_id: z.string(),
  speed_kn: num,
  distance_nm: num,
  port_hours: num,
  prediction: PredictionSchema,
  rows: z.array(z.object({
    key: z.string(),
    label: z.string(),
    fuel: z.string(),
    shore_power: z.boolean(),
    basis: z.enum(["MODEL PREDICTION", "SCENARIO ESTIMATE"]),
    measured_telemetry: z.literal(false),
    result: VoyageSchema.extend({ energy_mj_h: num }),
    assumptions: FuelAssumptions,
  })),
  shore_comparison: z.array(z.object({
    fuel: z.string(),
    label: z.string(),
    onboard_berth: BerthSchema,
    shore_berth: BerthSchema,
    delta_cost_usd: num,
    delta_wtw_tco2e: num,
    ghg_effect: z.enum(["REDUCES GHG", "INCREASES GHG", "NO GHG CHANGE"]),
    cost_effect: z.enum(["CHEAPER", "MORE EXPENSIVE", "SAME COST"]),
    basis: z.literal("SCENARIO ESTIMATE"),
  })),
  config: ConfigMeta.extend({ hotel_load_kw: num }),
});
export type Fuels = z.infer<typeof FuelsSchema>;

const PlanVessel = z.object({
  vessel_id: z.string(),
  assigned_demand: z.string().nullable(),
  cargo_tonnes: nnum,
  speed_kn: num,
  fuel: z.string().nullable(),
  shore_power: z.boolean().nullable(),
});
export type PlanVessel = z.infer<typeof PlanVessel>;

export const SolutionSchema = z.looseObject({
  feasible: z.boolean(),
  penalty_free: z.boolean().optional(),
  soft_penalties: z.record(z.string(), num).optional(),
  objectives: z.object({ fuel_t: num, opex_usd: num, wtw_tco2e: num, delay_h: num, risk_cvar_excess: num }).nullable(),
  hard_violations: z.array(z.string()),
  vessels: z.array(PlanVessel),
  evaluations: num.optional(),
  runtime_s: num.optional(),
});
export type Solution = z.infer<typeof SolutionSchema>;

export const OptimizerConfigSchema = z.looseObject({
  evaluator_ready: z.boolean(),
  evaluator_error: z.string().nullable(),
  algorithms: z.array(z.string()),
  budgets: z.array(num),
  objective_names: z.array(z.string()),
  formulations: z.record(z.string(), z.array(num)),
  decision_variables_per_vessel: z.array(z.string()),
  vessels: z.array(z.looseObject({
    vessel_id: z.string(), name: z.string(), class_family: z.string(), deadweight_tonnes: num,
    min_speed_knots: num, max_speed_knots: num, compatible_fuels: z.array(z.string()),
  })),
  demands: z.array(z.looseObject({
    demand_id: z.string(), name: z.string(), origin: z.string(), destination: z.string(),
    distance_nm: num, cargo_quantity_tonnes: num, deadline_hours: num, required_vessel_family: z.string(),
    source_provenance: z.string(),
  })),
  constraints_doc: z.string().nullable(),
});
export type OptimizerConfig = z.infer<typeof OptimizerConfigSchema>;

export const JobSchema = z.looseObject({
  job_id: z.string(),
  status: z.enum(["QUEUED", "WARMING_EVALUATOR", "RUNNING", "DONE", "ERROR"]),
  params: z.object({ algorithm: z.string(), seed: num, budget: num, weights: z.array(num) }),
  evaluations: num,
  feasible_evaluations: num,
  budget: num,
  result: SolutionSchema.nullable(),
  error: z.string().nullable(),
  recommendation_status: z.enum(["PENDING_REVIEW", "ACCEPTED", "REJECTED", "NOT_RECOMMENDABLE"]).nullable(),
  advisory: z.string(),
});
export type Job = z.infer<typeof JobSchema>;

const ParetoPoint = z.looseObject({
  solution_id: z.string(),
  formulation: z.string(),
  seed: num,
  algorithm: z.string(),
  fuel_tonnes: num,
  cost_usd: num,
  ghg_tonnes: num,
  delay_hours: num,
  evaluations: num,
});
export type ParetoPoint = z.infer<typeof ParetoPoint>;

export const ParetoSchema = z.object({
  source: z.string(),
  provenance: z.string(),
  archived_rows: num,
  points: z.array(ParetoPoint),
  summary: z.string(),
  note: z.string(),
});
export type Pareto = z.infer<typeof ParetoSchema>;

export const ResolveSchema = z.object({
  solution: ParetoPoint,
  rerun: SolutionSchema,
  reproduced: z.boolean(),
  note: z.string(),
});
export type Resolve = z.infer<typeof ResolveSchema>;

export const AlertsSchema = z.object({
  generated_at: z.string(),
  alerts: z.array(z.object({
    timestamp: z.string().nullable(),
    vessel_id: z.string().nullable(),
    state: z.string(),
    reason: z.string().nullable(),
    source: z.string().nullable(),
  })),
});
export type Alerts = z.infer<typeof AlertsSchema>;

export const AuditSchema = z.object({
  session: z.object({ label: z.string(), session_id: z.string(), events: z.array(EventSchema) }),
  persisted: z.object({
    label: z.string(), database: z.string(), total_events: num, total_sessions: num, events: z.array(EventSchema),
  }),
  historical: z.looseObject({
    label: z.string(),
    release_gate: z.looseObject({
      timestamp_utc: z.string().nullable(),
      classification: z.string().nullable(),
      gates_passed: nnum,
      gates_evaluated: nnum,
      gates: z.array(z.object({
        id: z.string(), name: z.string().nullable(), status: z.string().nullable(), evidence: z.string().nullable(),
      })),
    }).nullable(),
    claims: z.object({ prohibited: z.array(z.string()), verified_count: num }).nullable(),
    artifacts: z.array(z.object({ path: z.string(), sha256: z.string() })),
  }),
});
export type Audit = z.infer<typeof AuditSchema>;

export const DemoScenesSchema = z.object({
  source: z.string(),
  mode: z.string(),
  scenes: z.array(z.object({ id: num, title: z.string() })),
});

export const DemoRunSchema = z.object({
  scene_id: num,
  title: z.string(),
  mode: z.string(),
  data: z.record(z.string(), z.unknown()),
});
export type DemoRun = z.infer<typeof DemoRunSchema>;

// ------------------------------------------------------------------ transport

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function call<S extends z.ZodType>(path: string, schema: S, init?: RequestInit): Promise<z.infer<S>> {
  let res: Response;
  try {
    res = await fetch(`/api${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      cache: "no-store",
    });
  } catch (e) {
    throw new ApiError(0, `Backend unreachable (${(e as Error).message}). Is the API running on port 8000?`);
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    if (body === null) {
      throw new ApiError(res.status, `Backend unreachable or failed without a JSON error (HTTP ${res.status}). Is the API running on port 8000?`);
    }
    const detail = body?.detail;
    const msg = typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : res.statusText;
    throw new ApiError(res.status, `${res.status}: ${msg}`);
  }
  const parsed = schema.safeParse(body);
  if (!parsed.success) {
    const issue = parsed.error.issues[0];
    throw new ApiError(res.status, `API contract violation at ${path}: ${issue.path.join(".")} — ${issue.message}`);
  }
  return parsed.data;
}

const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

export const api = {
  status: () => call("/status", StatusSchema),
  fleet: () => call("/fleet", FleetSchema),
  vessel: (id: string) => call(`/vessels/${encodeURIComponent(id)}`, VesselDetailSchema),
  predict: (input: Record<string, unknown>) => call("/predict", PredictionSchema, post(input)),
  scenario: (req: Record<string, unknown>) => call("/scenario", ScenarioSchema, post(req)),
  fuels: (q: { vessel_id: string; speed_kn: number; distance_nm: number; port_hours: number }) =>
    call(`/fuels?${new URLSearchParams(Object.entries(q).map(([k, v]) => [k, String(v)]))}`, FuelsSchema),
  optimizerConfig: () => call("/optimizer/config", OptimizerConfigSchema),
  optimize: (req: { algorithm: string; seed: number; budget: number; weights: number[] }) =>
    call("/optimize", JobSchema, post(req)),
  job: (id: string) => call(`/optimize/${id}`, JobSchema),
  decide: (id: string, decision: "ACCEPT" | "REJECT", note: string) =>
    call(`/recommendations/${id}/decision`, JobSchema, post({ decision, note })),
  pareto: () => call("/pareto", ParetoSchema),
  resolvePareto: (id: string) => call(`/pareto/${id}/resolve`, ResolveSchema, { method: "POST" }),
  alerts: () => call("/alerts", AlertsSchema),
  audit: () => call("/audit", AuditSchema),
  demoScenes: () => call("/demo/scenes", DemoScenesSchema),
  runDemo: (id: number) => call(`/demo/scenes/${id}`, DemoRunSchema, { method: "POST" }),
};
