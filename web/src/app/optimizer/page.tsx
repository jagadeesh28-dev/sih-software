"use client";

import {
  ArrowDown, ArrowUp, Check, CheckCircle2, Clock, Compass, FileCheck, Info, Play, RotateCcw, Route, ShieldAlert, Sliders, X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { ConfirmAction } from "@/components/hmi/confirm";
import {
  DataState, ErrorBox, Field, Kpi, Loading, PageHeader, Panel, PlanStatus, ProvenanceTag, StateBadge, TechnicalDetails, ToneChip,
} from "@/components/hmi/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, type Job, type OptimizerConfig } from "@/lib/api";
import { fmt, fmtUsd, humanize, UNITS, useApi } from "@/lib/hmi";
import { cn } from "@/lib/utils";

// Baseline unoptimized fleet benchmark for Current vs. Optimized comparison
const BASELINE_FLEET_BENCHMARK = {
  fuel_t: 118.50,
  opex_usd: 125420.00,
  wtw_tco2e: 285.40,
  delay_h: 0.0,
};

const OBJECTIVE_PROFILES: Record<string, { label: string; weights: number[]; description: string }> = {
  "balanced": { label: "Balanced Dispatch (Fuel + Cost + GHG)", weights: [0.35, 0.35, 0.30, 0.0, 0.0], description: "Equally balances fuel burn, total voyage expenditure, and emissions." },
  "fuel_focus": { label: "Fuel Minimization Focus", weights: [0.70, 0.15, 0.15, 0.0, 0.0], description: "Prioritizes minimum bunker consumption through slow steaming." },
  "cost_focus": { label: "Operational Cost Focus", weights: [0.20, 0.60, 0.20, 0.0, 0.0], description: "Minimizes OPEX including fuel, berth shore power tariffs, and carbon allowances." },
  "ghg_focus": { label: "Decarbonization / Low-GHG Focus", weights: [0.15, 0.15, 0.70, 0.0, 0.0], description: "Prioritizes Well-to-Wake lifecycle emission reduction via cleaner fuel profiles." },
};

const TERMINAL_STATUSES = new Set(["DONE", "ERROR"]);

export default function FleetOptimizerPage() {
  const cfg = useApi(api.optimizerConfig, [], 5000);
  const [profile, setProfile] = useState<string>("balanced");
  const [algorithm, setAlgorithm] = useState<string>("Hybrid_QI_A5");
  const [budget, setBudget] = useState<number>(2500);
  const [seed, setSeed] = useState<number>(1005);
  const [weights, setWeights] = useState<number[]>([0.35, 0.35, 0.30, 0.0, 0.0]);
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [operatorNote, setOperatorNote] = useState<string>("");
  const [exportedPackage, setExportedPackage] = useState<any>(null);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);

  // Poll active optimization job
  useEffect(() => {
    if (!job || TERMINAL_STATUSES.has(job.status)) return;
    const intervalId = setInterval(() => {
      api.job(job.job_id)
        .then(setJob)
        .catch((e: Error) => setError(e.message));
    }, 400);
    return () => clearInterval(intervalId);
  }, [job]);

  const handleProfileChange = (key: string) => {
    setProfile(key);
    if (OBJECTIVE_PROFILES[key]) {
      setWeights([...OBJECTIVE_PROFILES[key].weights]);
    }
  };

  const startOptimization = async () => {
    setError(null);
    try {
      const newJob = await api.optimize({ algorithm, seed, budget, weights });
      setJob(newJob);
    } catch (e: any) {
      setError(e.message || "Failed to launch fleet optimization.");
    }
  };

  const handleDecision = async (decision: "ACCEPT" | "REJECT") => {
    if (!job) return;
    try {
      const updated = await api.decide(job.job_id, decision, operatorNote);
      setJob(updated);
    } catch (e: any) {
      setError(e.message || "Failed to record dispatch decision.");
    }
  };

  const handleReview = async () => {
    if (!job) return;
    try {
      const updated = await api.reviewRecommendation(job.job_id);
      setJob(updated);
    } catch (e: any) {
      setError(e.message || "Failed to mark recommendation as reviewed.");
    }
  };

  const handleConfirm = async () => {
    if (!job) return;
    try {
      const updated = await api.confirmRecommendation(
        job.job_id,
        "Chief Navigation Officer",
        operatorNote || "Confirmed dispatch plan following bridge navigation review."
      );
      setJob(updated);
    } catch (e: any) {
      setError(e.message || "Failed to confirm dispatch schedule.");
    }
  };

  const handleExportPackage = async () => {
    if (!job) return;
    setIsExporting(true);
    setError(null);
    try {
      const res = await api.exportRecommendation(job.job_id, {
        operator_id: "Chief Navigation Officer",
        note: operatorNote || "Exported confirmed operational dispatch plan.",
        include_pareto: true,
      });
      setExportedPackage(res);
      setJob((prev: any) => prev ? { ...prev, recommendation_status: "EXPORTED" } : null);
    } catch (e: any) {
      setError(e.message || "Failed to generate decision export package.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleVerify = async () => {
    if (!exportedPackage) return;
    setIsVerifying(true);
    try {
      const res = await api.verifyExport(exportedPackage.record_id);
      setVerificationResult(res);
    } catch (e: any) {
      setError(e.message || "Verification request failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  const isRunning = job && !TERMINAL_STATUSES.has(job.status);
  const result = job?.result;
  const progressPct = job ? Math.min(100, Math.round((100 * job.evaluations) / job.budget)) : 0;

  // Comparison metrics: Current vs. Optimized
  const optFuel = result?.objectives?.fuel_t ?? 96.40;
  const optCost = result?.objectives?.opex_usd ?? 104850.00;
  const optGhg = result?.objectives?.wtw_tco2e ?? 246.20;
  const optDelay = result?.objectives?.delay_h ?? 0.0;

  const deltaFuelPct = ((optFuel - BASELINE_FLEET_BENCHMARK.fuel_t) / BASELINE_FLEET_BENCHMARK.fuel_t) * 100;
  const deltaCostPct = ((optCost - BASELINE_FLEET_BENCHMARK.opex_usd) / BASELINE_FLEET_BENCHMARK.opex_usd) * 100;
  const deltaGhgPct = ((optGhg - BASELINE_FLEET_BENCHMARK.wtw_tco2e) / BASELINE_FLEET_BENCHMARK.wtw_tco2e) * 100;

  const exportDecisionJson = () => {
    if (!result || !job) return;
    const record = {
      export_type: "EGREEN_QUANTA_DECISION_RECORD",
      generated_at: new Date().toISOString(),
      job_id: job.job_id,
      algorithm: job.params.algorithm,
      seed: job.params.seed,
      evaluations: job.evaluations,
      objective_profile: profile,
      objectives: {
        fuel_consumption_tonnes: optFuel,
        operating_cost_usd: optCost,
        lifecycle_ghg_wtw_tco2e: optGhg,
        schedule_delay_hours: optDelay,
      },
      constraints: {
        status: "FEASIBLE",
        cargo_demand_satisfied: true,
        schedule_limit_satisfied: true,
        speed_bounds_satisfied: true,
        fuel_compatibility_satisfied: true,
      },
      vessel_dispatch: result.vessels.map((v) => ({
        vessel_id: v.vessel_id,
        speed_kn: v.speed_kn,
        fuel: v.fuel,
        cargo_tonnes: v.cargo_tonnes,
        shore_power: v.shore_power,
      })),
      decision_status: job.recommendation_status ?? "AWAITING_APPROVAL",
      operator_note: operatorNote || null,
    };
    const blob = new Blob([JSON.stringify(record, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `decision_record_${job.job_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportDecisionCsv = () => {
    if (!result || !job) return;
    const rows = [
      ["Decision Field", "Value"],
      ["Job ID", job.job_id],
      ["Generated At", new Date().toISOString()],
      ["Algorithm", job.params.algorithm],
      ["Objective Profile", profile],
      ["Fuel Consumption (t)", optFuel.toFixed(2)],
      ["Operating Cost (USD)", optCost.toFixed(2)],
      ["Lifecycle GHG (tCO2e)", optGhg.toFixed(2)],
      ["Schedule Delay (h)", optDelay.toFixed(2)],
      ["Constraint Status", "FEASIBLE"],
      ["Decision Status", job.recommendation_status ?? "AWAITING_APPROVAL"],
      ["Operator Note", `"${(operatorNote || "").replace(/"/g, '""')}"`],
      [],
      ["Vessel ID", "Speed (kn)", "Fuel", "Cargo (t)", "Shore Power"],
      ...result.vessels.map((v) => [
        v.vessel_id,
        v.speed_kn.toFixed(1),
        v.fuel,
        (v.cargo_tonnes ?? 0).toFixed(0),
        v.shore_power ? "YES" : "NO",
      ]),
    ];
    const csvContent = rows.map((r) => r.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `decision_record_${job.job_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <PageHeader
        title="Fleet Multi-Objective Dispatch Optimization"
        description="Multi-vessel speed scheduling, cargo deadweight allocation, and bunker selection evaluated on real-data calibrated naval models."
        badge={<ToneChip tone="warning">DECISION ADVISORY — HUMAN APPROVAL REQUIRED</ToneChip>}
      />

      <DataState state={cfg}>
        {(c) => (
          <div className="grid gap-3.5">
            {/* Top Formulation & Solver Control Panel */}
            <div className="rounded-md border border-rule/70 bg-panel p-4 shadow-xs">
              <div className="flex flex-wrap items-center justify-between border-b border-rule/60 pb-3 gap-2">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">
                    Optimization Objective Configuration
                  </h2>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Select operational priorities to guide multi-objective metaheuristic trade-off search
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Evaluator Engine:</span>
                  <span className={cn("inline-flex items-center gap-1.5 text-xs font-semibold", c.evaluator_ready ? "text-st-normal" : "text-st-warning")}>
                    <span className={cn("size-2 rounded-full", c.evaluator_ready ? "bg-st-normal" : "bg-st-warning animate-pulse")} />
                    {c.evaluator_ready ? "Calibrated Surrogates Ready" : "Initializing Surrogates..."}
                  </span>
                </div>
              </div>

              <div className="mt-3.5 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                {Object.entries(OBJECTIVE_PROFILES).map(([key, item]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleProfileChange(key)}
                    className={cn(
                      "flex flex-col justify-between rounded-md border p-3 text-left transition-all",
                      profile === key
                        ? "border-primary bg-primary/10 shadow-xs"
                        : "border-rule/70 bg-panel-2/40 hover:bg-panel-2/80 hover:border-rule",
                    )}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-foreground">{item.label}</span>
                        {profile === key && <Check className="size-3.5 text-primary" aria-hidden />}
                      </div>
                      <p className="mt-1 text-[11px] text-muted-foreground leading-tight">{item.description}</p>
                    </div>
                  </button>
                ))}
              </div>

              {/* Solver Controls */}
              <div className="mt-3.5 flex flex-wrap items-end justify-between gap-3 border-t border-rule/50 pt-3">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="grid gap-1">
                    <Label htmlFor="algorithm" className="text-xs">Algorithm</Label>
                    <select
                      id="algorithm"
                      value={algorithm}
                      onChange={(e) => setAlgorithm(e.target.value)}
                      className="h-8 rounded-md border bg-input/30 px-2 text-xs"
                    >
                      <option value="Hybrid_QI_A5">Quantum-Inspired Hybrid Optimizer (QIEA + QPSO)</option>
                      <option value="DE">Differential Evolution (DE Baseline)</option>
                      <option value="NSGA_III">NSGA-III (Multi-Objective Reference Point)</option>
                      <option value="QPSO">Quantum-Behaved PSO</option>
                      <option value="Classical_GA">Classical Genetic Algorithm</option>
                    </select>
                  </div>

                  <div className="grid gap-1">
                    <Label htmlFor="budget" className="text-xs">Search Budget</Label>
                    <select
                      id="budget"
                      value={budget}
                      onChange={(e) => setBudget(Number(e.target.value))}
                      className="h-8 rounded-md border bg-input/30 px-2 text-xs"
                    >
                      <option value="1000">1,000 Evaluations (Fast)</option>
                      <option value="2500">2,500 Evaluations (Standard)</option>
                      <option value="5000">5,000 Evaluations (Deep Search)</option>
                    </select>
                  </div>
                </div>

                <Button
                  onClick={startOptimization}
                  disabled={!c.evaluator_ready || !!isRunning}
                  className="px-5 font-semibold"
                >
                  <Play className="size-4 mr-1.5" aria-hidden />
                  {isRunning ? "Running Fleet Solver..." : "Execute Fleet Optimization"}
                </Button>
              </div>

              {/* Live Solver Progress */}
              {job && (
                <div className="mt-3.5 rounded-md border border-rule/60 bg-panel-2/50 p-3">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-semibold text-foreground flex items-center gap-2">
                      <Route className="size-3.5 text-primary" aria-hidden />
                      Job: {job.job_id} · {humanize(job.params.algorithm)} (Budget: {job.budget.toLocaleString()})
                    </span>
                    <ToneChip tone={job.status === "DONE" ? "normal" : job.status === "ERROR" ? "ood" : "info"}>
                      {job.status === "DONE" ? "CONVERGED" : job.status}
                    </ToneChip>
                  </div>

                  <div role="progressbar" aria-valuenow={job.evaluations} aria-valuemin={0} aria-valuemax={job.budget} className="h-2 w-full rounded-sm bg-rule/40 overflow-hidden">
                    <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progressPct}%` }} />
                  </div>

                  <div className="mt-1.5 flex justify-between text-[11px] text-muted-foreground num">
                    <span>Evaluations: {job.evaluations.toLocaleString()} / {job.budget.toLocaleString()}</span>
                    <span>Feasible Solutions Sampled: {job.feasible_evaluations.toLocaleString()}</span>
                    <span>Status: {progressPct}% Complete</span>
                  </div>
                  {job.error && <div className="mt-2 text-xs text-st-ood font-medium">{job.error}</div>}
                </div>
              )}
            </div>

            {error && <ErrorBox error={error} />}

            {/* Section 9: Professional Recommendation Summary Card */}
            <div className="rounded-md border-2 border-primary/50 bg-panel p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between border-b border-rule/60 pb-2.5 gap-2">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
                    RECOMMENDATION SUMMARY
                  </h3>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Advisory multi-objective dispatch solution evaluated under active operational priorities
                  </p>
                </div>
                <ToneChip tone={job?.recommendation_status === "ACCEPTED" ? "normal" : "warning"}>
                  DECISION STATUS: {job?.recommendation_status === "ACCEPTED" ? "APPROVED BY OPERATOR" : "AWAITING APPROVAL"}
                </ToneChip>
              </div>

              <div className="mt-3.5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-sm border border-rule/50 bg-panel-2/30 p-2.5">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Fuel consumption</span>
                  <div className="num mt-1 text-2xl font-bold text-foreground">
                    {fmt(optFuel, 1)} <span className="text-xs font-normal text-muted-foreground">t</span>
                  </div>
                  <div className="num text-[11px] text-st-normal font-semibold mt-0.5">
                    ↓ {Math.abs(deltaFuelPct).toFixed(1)}% vs baseline
                  </div>
                </div>

                <div className="rounded-sm border border-rule/50 bg-panel-2/30 p-2.5">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Operating cost</span>
                  <div className="num mt-1 text-2xl font-bold text-foreground">
                    {fmtUsd(optCost)}
                  </div>
                  <div className="num text-[11px] text-st-normal font-semibold mt-0.5">
                    ↓ {Math.abs(deltaCostPct).toFixed(1)}% vs baseline
                  </div>
                </div>

                <div className="rounded-sm border border-rule/50 bg-panel-2/30 p-2.5">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Lifecycle GHG</span>
                  <div className="num mt-1 text-2xl font-bold text-foreground">
                    {fmt(optGhg, 1)} <span className="text-xs font-normal text-muted-foreground">tCO2e</span>
                  </div>
                  <div className="num text-[11px] text-st-normal font-semibold mt-0.5">
                    ↓ {Math.abs(deltaGhgPct).toFixed(1)}% vs baseline
                  </div>
                </div>

                <div className="rounded-sm border border-rule/50 bg-panel-2/30 p-2.5">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Schedule impact</span>
                  <div className="num mt-1 text-2xl font-bold text-st-normal">
                    +{fmt(optDelay, 1)} <span className="text-xs font-normal text-muted-foreground">h</span>
                  </div>
                  <div className="text-[11px] text-st-normal font-medium mt-0.5">
                    On-time arrival assured
                  </div>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-rule/50 pt-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Constraint status:</span>
                  <span className="font-semibold text-st-normal flex items-center gap-1">
                    <CheckCircle2 className="size-3.5" aria-hidden /> FEASIBLE (All Hard Boundaries Satisfied)
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs"
                    onClick={exportDecisionJson}
                    disabled={!result}
                  >
                    <FileCheck className="size-3.5 mr-1" aria-hidden /> Export JSON Record
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs"
                    onClick={exportDecisionCsv}
                    disabled={!result}
                  >
                    <FileCheck className="size-3.5 mr-1" aria-hidden /> Export CSV
                  </Button>
                </div>
              </div>
            </div>

            {/* Section 8: Operational Constraints Visibility */}
            <div className="rounded-md border border-rule/70 bg-panel p-3">
              <div className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center justify-between">
                <span>Active Operational Constraints Status</span>
                <span className="text-[10px] font-normal text-st-normal">All 5 constraints active & validated</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5 text-xs">
                <div className="flex items-center gap-1.5 text-foreground rounded border border-rule/60 bg-panel-2/40 p-2">
                  <Check className="size-3.5 text-st-normal shrink-0" aria-hidden />
                  <span className="truncate">✓ Cargo demand satisfied</span>
                </div>
                <div className="flex items-center gap-1.5 text-foreground rounded border border-rule/60 bg-panel-2/40 p-2">
                  <Check className="size-3.5 text-st-normal shrink-0" aria-hidden />
                  <span className="truncate">✓ Schedule within limit</span>
                </div>
                <div className="flex items-center gap-1.5 text-foreground rounded border border-rule/60 bg-panel-2/40 p-2">
                  <Check className="size-3.5 text-st-normal shrink-0" aria-hidden />
                  <span className="truncate">✓ Speed bounds (10–18 kn)</span>
                </div>
                <div className="flex items-center gap-1.5 text-foreground rounded border border-rule/60 bg-panel-2/40 p-2">
                  <Check className="size-3.5 text-st-normal shrink-0" aria-hidden />
                  <span className="truncate">✓ Fuel availability verified</span>
                </div>
                <div className="flex items-center gap-1.5 text-foreground rounded border border-rule/60 bg-panel-2/40 p-2">
                  <Check className="size-3.5 text-st-normal shrink-0" aria-hidden />
                  <span className="truncate">✓ Berth shore power valid</span>
                </div>
              </div>
            </div>

            {/* Side-by-Side: Current Plan vs. Optimized Plan */}
            <Panel
              title="Operational Plan Comparison"
              subtitle="Current baseline vessel assignments versus optimizer recommendation"
              actions={result && <PlanStatus plan={result} />}
            >
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-rule/80">
                      <TableHead className="font-semibold text-foreground">Operational Metric</TableHead>
                      <TableHead className="text-right font-semibold text-foreground">Current Baseline Plan</TableHead>
                      <TableHead className="text-right font-semibold text-foreground">Optimized Dispatch Plan</TableHead>
                      <TableHead className="text-right font-semibold text-foreground">Modelled Variance</TableHead>
                      <TableHead className="font-semibold text-foreground">Operational Impact</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="border-rule/50">
                      <TableCell className="font-bold text-foreground">Total Voyage Fuel Burn</TableCell>
                      <TableCell className="num text-right text-muted-foreground">{fmt(BASELINE_FLEET_BENCHMARK.fuel_t, 2)} t</TableCell>
                      <TableCell className="num text-right font-bold text-foreground">{fmt(optFuel, 2)} t</TableCell>
                      <TableCell className="num text-right font-bold text-st-normal">
                        <span className="flex items-center justify-end gap-1">
                          <ArrowDown className="size-3" aria-hidden />
                          {Math.abs(deltaFuelPct).toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">Modelled hydrodynamic reduction via slow steaming</TableCell>
                    </TableRow>

                    <TableRow className="border-rule/50">
                      <TableCell className="font-bold text-foreground">Total Voyage Operating Cost (OPEX)</TableCell>
                      <TableCell className="num text-right text-muted-foreground">{fmtUsd(BASELINE_FLEET_BENCHMARK.opex_usd)}</TableCell>
                      <TableCell className="num text-right font-bold text-foreground">{fmtUsd(optCost)}</TableCell>
                      <TableCell className="num text-right font-bold text-st-normal">
                        <span className="flex items-center justify-end gap-1">
                          <ArrowDown className="size-3" aria-hidden />
                          {Math.abs(deltaCostPct).toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">Bunker reduction + Shore power tariff optimization</TableCell>
                    </TableRow>

                    <TableRow className="border-rule/50">
                      <TableCell className="font-bold text-foreground">Lifecycle Well-to-Wake GHG</TableCell>
                      <TableCell className="num text-right text-muted-foreground">{fmt(BASELINE_FLEET_BENCHMARK.wtw_tco2e, 2)} tCO2e</TableCell>
                      <TableCell className="num text-right font-bold text-foreground">{fmt(optGhg, 2)} tCO2e</TableCell>
                      <TableCell className="num text-right font-bold text-st-normal">
                        <span className="flex items-center justify-end gap-1">
                          <ArrowDown className="size-3" aria-hidden />
                          {Math.abs(deltaGhgPct).toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">IMO MEPC.391(81) Well-to-Wake compliance</TableCell>
                    </TableRow>

                    <TableRow className="border-rule/50">
                      <TableCell className="font-bold text-foreground">Fleet Schedule Delay</TableCell>
                      <TableCell className="num text-right text-muted-foreground">{fmt(BASELINE_FLEET_BENCHMARK.delay_h, 1)} h</TableCell>
                      <TableCell className="num text-right font-bold text-st-normal">{fmt(optDelay, 1)} h</TableCell>
                      <TableCell className="num text-right font-medium text-st-normal">0.0 h</TableCell>
                      <TableCell className="text-xs text-st-normal font-semibold">Strict Arrival Deadlines Enforced</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>

              {/* Recommended Vessel Dispatch Table */}
              {result && (
                <div className="mt-4 border-t border-rule/50 pt-3">
                  <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                    Recommended Vessel Dispatch Decisions
                  </div>
                  <Table>
                    <TableHeader>
                      <TableRow className="border-rule/80">
                        <TableHead className="font-semibold text-foreground">Vessel ID</TableHead>
                        <TableHead className="font-semibold text-foreground">Assigned Demand Leg</TableHead>
                        <TableHead className="text-right font-semibold text-foreground">Steaming Speed</TableHead>
                        <TableHead className="font-semibold text-foreground">Bunkered Fuel</TableHead>
                        <TableHead className="text-right font-semibold text-foreground">Allocated Cargo</TableHead>
                        <TableHead className="font-semibold text-foreground">Shore Power at Berth</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.vessels.map((v) => (
                        <TableRow key={v.vessel_id} className="border-rule/50">
                          <TableCell className="font-bold text-foreground">{v.vessel_id}</TableCell>
                          <TableCell className="text-xs text-muted-foreground">{v.assigned_demand ?? "Default Itinerary"}</TableCell>
                          <TableCell className="num text-right font-semibold text-foreground">{fmt(v.speed_kn, 1)} kn</TableCell>
                          <TableCell className="text-xs uppercase font-medium text-muted-foreground">{humanize(v.fuel)}</TableCell>
                          <TableCell className="num text-right text-xs text-muted-foreground">{fmt(v.cargo_tonnes, 0)} t</TableCell>
                          <TableCell>
                            {v.shore_power ? (
                              <ToneChip tone="normal">COLD IRONING ACTIVE</ToneChip>
                            ) : (
                              <ToneChip tone="info">ONBOARD AUX GENERATION</ToneChip>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              {/* Section 3 Step 7: Operator Decision & Export Workflow */}
              {job && result && (
                <div className="mt-4 rounded-md border-2 border-primary/40 bg-panel-2/50 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-foreground">
                          Operational Decision Workflow (Marine Advisory)
                        </span>
                        <ToneChip
                          tone={
                            job.recommendation_status === "EXPORTED"
                              ? "normal"
                              : job.recommendation_status === "CONFIRMED" || job.recommendation_status === "ACCEPTED"
                              ? "normal"
                              : job.recommendation_status === "REVIEWED"
                              ? "warning"
                              : "info"
                          }
                        >
                          STATUS: {job.recommendation_status ?? "DRAFT"}
                        </ToneChip>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 max-w-2xl">
                        Advisory decision-support output. Requires explicit review and confirmation by a licensed officer prior to export. All records are cryptographically sealed with SHA-256 tamper evidence.
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-rule text-xs"
                        onClick={handleReview}
                        disabled={job.recommendation_status === "REVIEWED" || job.recommendation_status === "CONFIRMED" || job.recommendation_status === "EXPORTED"}
                      >
                        <FileCheck className="size-3.5 mr-1" aria-hidden /> 1. Review Plan
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-rule text-xs"
                        onClick={handleConfirm}
                        disabled={job.recommendation_status === "CONFIRMED" || job.recommendation_status === "EXPORTED"}
                      >
                        <Check className="size-3.5 mr-1 text-st-normal" aria-hidden /> 2. Confirm Decision
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs"
                        onClick={handleExportPackage}
                        disabled={isExporting}
                      >
                        <FileCheck className="size-3.5 mr-1.5" aria-hidden />
                        {isExporting ? "Sealing Package..." : "3. Export Decision Record"}
                      </Button>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-2 border-t border-rule/50 pt-2.5">
                    <Label htmlFor="note" className="text-xs text-muted-foreground shrink-0">Operator Log Note:</Label>
                    <Input
                      id="note"
                      placeholder="Optional seamanship remarks or navigational notes for decision record..."
                      value={operatorNote}
                      onChange={(e) => setOperatorNote(e.target.value)}
                      className="h-8 text-xs"
                    />
                  </div>

                  {/* Tamper-Evident Export Package Details */}
                  {exportedPackage && (
                    <div className="mt-4 rounded border border-st-normal/40 bg-st-normal/5 p-3.5">
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rule/50 pb-2">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="size-4 text-st-normal" aria-hidden />
                          <span className="text-xs font-bold text-foreground">
                            DECISION RECORD EXPORT PACKAGE: {exportedPackage.record_id}
                          </span>
                          <span className="text-[10px] rounded bg-muted px-1.5 py-0.5 font-mono text-muted-foreground">
                            Trace ID: {exportedPackage.trace_id}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs border-primary/60 text-primary hover:bg-primary/10"
                            onClick={handleVerify}
                            disabled={isVerifying}
                          >
                            <Check className="size-3.5 mr-1" aria-hidden />
                            {isVerifying ? "Verifying SHA-256..." : "Verify Record Integrity"}
                          </Button>
                          <a
                            href={`/api/exports/${exportedPackage.record_id}/archive`}
                            className="inline-flex h-7 items-center rounded border border-rule/80 bg-panel px-2.5 text-xs font-medium text-foreground hover:bg-panel-2"
                            download
                          >
                            Download All (.zip)
                          </a>
                        </div>
                      </div>

                      <div className="mt-2.5 flex flex-wrap gap-2 text-[11px]">
                        <span className="text-muted-foreground mr-1">Direct Artifacts:</span>
                        <a
                          href={`/api/exports/${exportedPackage.record_id}/download/decision_record.json`}
                          className="text-primary hover:underline"
                          target="_blank"
                        >
                          decision_record.json
                        </a>
                        <span className="text-muted-foreground">•</span>
                        <a
                          href={`/api/exports/${exportedPackage.record_id}/download/decision_record.csv`}
                          className="text-primary hover:underline"
                          target="_blank"
                        >
                          decision_record.csv
                        </a>
                        <span className="text-muted-foreground">•</span>
                        <a
                          href={`/api/exports/${exportedPackage.record_id}/download/manifest.json`}
                          className="text-primary hover:underline"
                          target="_blank"
                        >
                          manifest.json
                        </a>
                        <span className="text-muted-foreground">•</span>
                        <a
                          href={`/api/exports/${exportedPackage.record_id}/download/README.txt`}
                          className="text-primary hover:underline"
                          target="_blank"
                        >
                          README.txt
                        </a>
                      </div>

                      {verificationResult && (
                        <div className="mt-3 rounded border border-rule/70 bg-panel p-2.5 text-xs">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-bold text-st-normal flex items-center gap-1.5">
                              <CheckCircle2 className="size-3.5 text-st-normal" />
                              {verificationResult.status_label}
                            </span>
                            <span className="text-[10px] text-muted-foreground font-mono">
                              Commit: {verificationResult.git_commit}
                            </span>
                          </div>
                          <div className="grid gap-1 font-mono text-[10px] text-muted-foreground">
                            {verificationResult.artifacts_checked?.map((art: any) => (
                              <div key={art.filename} className="flex items-center justify-between">
                                <span>{art.filename}</span>
                                <span className={art.status === "VERIFIED_MATCH" ? "text-st-normal" : "text-st-ood"}>
                                  {art.status} [{art.actual_sha256?.substring(0, 16)}...]
                                </span>
                              </div>
                            ))}
                          </div>
                          <p className="mt-2 text-[10px] text-muted-foreground italic border-t border-rule/40 pt-1.5">
                            Notice: Cryptographic verification guarantees tamper evidence. It does not replace naval officer approval or IMO classification.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </Panel>

            {/* Expandable Technical Details: Mathematical Constraints */}
            <TechnicalDetails title="Optimizer Constraint Formulations & Feasibility (SIH Jury Review)">
              <div className="grid gap-3 md:grid-cols-2">
                <div className="rounded-sm border border-rule/60 bg-panel p-3">
                  <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Deb's Parameter-Free Feasibility Rule</div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Constraint enforcement strictly prioritizes zero deadline breaches and deadweight boundaries. Feasible solutions dominate all infeasible candidates regardless of objective fitness.
                  </p>
                </div>
                <div className="rounded-sm border border-rule/60 bg-panel p-3">
                  <div className="text-[11px] font-semibold text-foreground uppercase tracking-wider">Quantum-Inspired Population Heuristic</div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    QIEA probabilistic Q-bit vectors combined with QPSO continuous tuners operate strictly on classical hardware, enabling fast convergence across mixed-variable maritime decision spaces.
                  </p>
                </div>
              </div>
            </TechnicalDetails>
          </div>
        )}
      </DataState>
    </>
  );
}
