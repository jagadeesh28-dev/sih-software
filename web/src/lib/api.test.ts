import { afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./api";

const trust = {
  state: "OOD", fallback: false, fallback_label: null, ood_band: "OOD", envelope_distance: 2.1,
  thresholds: { warning: 1, ood: 1.5, reject: 3 }, reason: "outside envelope", missing_factors: [],
  input_completeness_pct: 100, missing_factor_note: "n",
};
const prediction = {
  input: { stw_kn: 30 },
  result: { fuel_prediction: null, prediction_source: "REJECT", confidence: "LOW", routing_status: "REJECT" },
  trust,
};

function mockFetch(status: number, body: unknown) {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(body), { status })));
}

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("parses a valid prediction contract", async () => {
    mockFetch(200, prediction);
    const p = await api.predict({ stw_kn: 30 });
    expect(p.trust.state).toBe("OOD");
    expect(p.result.fuel_prediction).toBeNull();
  });

  it("rejects a response that violates the contract instead of rendering it", async () => {
    mockFetch(200, { ...prediction, trust: { ...trust, state: "TOTALLY_FINE" } });
    await expect(api.predict({})).rejects.toThrow(/contract violation/);
  });

  it("surfaces backend error detail", async () => {
    mockFetch(409, { detail: "Recommendation is ACCEPTED, not PENDING_REVIEW" });
    await expect(api.decide("OPT-1", "ACCEPT", "")).rejects.toThrow(/409: Recommendation is ACCEPTED/);
  });

  it("reports an unreachable backend explicitly", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("fetch failed"); }));
    const err = await api.status().catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.message).toMatch(/Backend unreachable/);
  });
});
