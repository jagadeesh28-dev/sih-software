"use client";

import {
  Anchor, BellRing, ClipboardList, FlaskConical, Fuel, Gauge, LayoutGrid, PlayCircle, Route, ScatterChart, Ship,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Status } from "@/lib/api";
import { STATE_META, asHmiState, fmtTime, humanize, useApi, type Loadable } from "@/lib/hmi";
import { cn } from "@/lib/utils";
import { StateBadge, ToneChip } from "./primitives";

// ------------------------------------------------------------------ context

interface HmiCtx {
  status: Loadable<Status>;
  activeVessel: string;
  setActiveVessel: (id: string) => void;
  scenarioId: string | null;
  setScenarioId: (id: string | null) => void;
}

const Ctx = createContext<HmiCtx | null>(null);

export function useHmi(): HmiCtx {
  const c = useContext(Ctx);
  if (!c) throw new Error("useHmi must be used inside <AppShell>");
  return c;
}

// ------------------------------------------------------------------ navigation

const NAV = [
  { href: "/fleet", label: "Fleet Overview", icon: LayoutGrid },
  { href: "/vessel", label: "Vessel Detail", icon: Ship },
  { href: "/trust", label: "Prediction & Trust", icon: Gauge },
  { href: "/scenario", label: "Scenario Lab", icon: FlaskConical },
  { href: "/optimizer", label: "Fleet Optimizer", icon: Route },
  { href: "/pareto", label: "Pareto / Trade-offs", icon: ScatterChart },
  { href: "/fuels", label: "Alternative Fuels", icon: Fuel },
  { href: "/alerts", label: "Alerts & Safety", icon: BellRing },
  { href: "/audit", label: "Audit / Reports", icon: ClipboardList },
  { href: "/demo", label: "Demo Mode", icon: PlayCircle },
];

function SideNav({ activeVessel }: { activeVessel: string }) {
  const path = usePathname();
  return (
    <nav aria-label="Operator workspace" className="flex flex-col gap-0.5 border-r bg-sidebar p-2">
      {NAV.map(({ href, label, icon: Icon }) => {
        const target = href === "/vessel" ? `/vessel/${activeVessel}` : href;
        const active = path === href || path.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={target}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-2 rounded-sm border-l-2 px-2 py-1.5 text-[13px] text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-foreground",
              active ? "border-primary bg-sidebar-accent font-semibold text-sidebar-foreground" : "border-transparent",
              href === "/demo" && "mt-auto",
            )}
          >
            <Icon className="size-4 shrink-0" aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

// ------------------------------------------------------------------ top bar

function ModeSwitch({ demo, live }: { demo: boolean; live: boolean }) {
  const modes = [
    { key: "LIVE", enabled: live, title: live ? "Live telemetry feed" : "No live telemetry feed is connected" },
    { key: "SIMULATION", enabled: true, title: "Fleet defaults and model evaluation (no live feed)" },
    { key: "DEMO", enabled: true, title: "Deterministic demonstration scenes" },
  ];
  const current = demo ? "DEMO" : live ? "LIVE" : "SIMULATION";
  return (
    <div role="group" aria-label="Operating mode" className="flex overflow-hidden rounded-sm border text-[11px] font-semibold">
      {modes.map((m) => (
        <span
          key={m.key}
          title={m.title}
          aria-current={current === m.key ? "true" : undefined}
          className={cn(
            "px-2 py-0.5 tracking-wider",
            current === m.key && m.key === "DEMO" && "bg-st-demo text-background",
            current === m.key && m.key !== "DEMO" && "bg-primary text-primary-foreground",
            current !== m.key && "text-muted-foreground",
            !m.enabled && "line-through opacity-50",
          )}
        >
          {current === m.key ? "● " : ""}{m.key}
        </span>
      ))}
    </div>
  );
}

function TopItem({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 flex-col leading-tight">
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
      <span className="num truncate text-xs">{children}</span>
    </div>
  );
}

function TopBar({ ctx, demo }: { ctx: HmiCtx; demo: boolean }) {
  const s = ctx.status.data;
  return (
    <header className={cn("flex items-center gap-5 border-b bg-sidebar px-3", demo && "border-b-2 border-st-demo")}>
      <div className="flex items-center gap-2 pr-2">
        <Anchor className="size-5 text-primary" aria-hidden />
        <span className="text-sm font-bold tracking-[0.18em]">EGREEN QUANTA</span>
      </div>
      <ModeSwitch demo={demo} live={s?.live_feed_connected ?? false} />
      {demo && <ToneChip tone="demo">DEMO MODE · SIMULATION — NOT LIVE TELEMETRY</ToneChip>}
      <div className="ml-auto flex items-center gap-5">
        <TopItem label="Fleet">{s ? `${s.fleet_count} vessels` : "—"}</TopItem>
        <TopItem label="Active vessel">{ctx.activeVessel}</TopItem>
        <TopItem label="Model">{s ? `${s.model.primary} · ${s.model.serving_version}` : "—"}</TopItem>
        <TopItem label="Scenario">{ctx.scenarioId ?? "none"}</TopItem>
        <TopItem label="Server time">{s ? fmtTime(s.server_time) : ctx.status.error ? "backend offline" : "—"}</TopItem>
      </div>
    </header>
  );
}

// ------------------------------------------------------------------ status bar

function StatusCell({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 items-center gap-1.5 border-r px-3 last:border-r-0">
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
      <span className="flex min-w-0 items-center gap-1 truncate text-[11px]">{children}</span>
    </div>
  );
}

function StatusBar({ status }: { status: Loadable<Status> }) {
  if (status.error) {
    return (
      <footer className="flex items-center border-t bg-sidebar px-3 text-[11px]">
        <StateBadge state="RUNTIME_FAILURE" /> <span className="ml-2 truncate">Backend unreachable: {status.error}</span>
      </footer>
    );
  }
  const s = status.data;
  const worst = s?.fleet_trust.reduce<string>((acc, t) =>
    STATE_META[asHmiState(t.state)].severity > STATE_META[asHmiState(acc)].severity ? t.state : acc, "NORMAL");
  const oodCount = s?.fleet_trust.filter((t) => t.ood_band === "OOD" || t.ood_band === "REJECT").length ?? 0;
  const fallbacks = s?.fleet_trust.filter((t) => t.fallback).length ?? 0;
  const freshest = s ? Object.values(s.data_freshness).sort().at(-1) : undefined;
  const rec = s?.last_recommendation;
  return (
    <footer className="flex items-stretch overflow-hidden border-t bg-sidebar py-1" aria-label="System status">
      <StatusCell label="Data">
        {s ? (<><ToneChip tone="warning">NO LIVE FEED</ToneChip><span title={s.data_freshness_note}>dataset to {fmtTime(freshest)}</span></>) : "—"}
      </StatusCell>
      <StatusCell label="Model">
        {s ? <>{s.model.primary} loaded · optimizer {s.evaluator_ready ? "ready" : s.evaluator_error ? "FAILED" : "warming"}</> : "—"}
      </StatusCell>
      <StatusCell label="Fleet trust">{worst ? <StateBadge state={worst} /> : "—"}</StatusCell>
      <StatusCell label="OOD">{s ? (oodCount ? <StateBadge state="OOD" /> : `none of ${s.fleet_count}`) : "—"}</StatusCell>
      <StatusCell label="Fallback">{s ? (fallbacks ? `${fallbacks} vessel(s) on fallback` : "none") : "—"}</StatusCell>
      <StatusCell label="Last recommendation">
        {rec ? `${String(rec.recommendation_id ?? rec.event_id)} · ${humanize(String(rec.decision ?? rec.recommendation_status ?? rec.kind))}` : "none this session"}
      </StatusCell>
    </footer>
  );
}

// ------------------------------------------------------------------ shell

export function AppShell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const status = useApi(api.status, [], 10000);
  const [activeVessel, setActive] = useState("CPS_Poseidon");
  const [scenarioId, setScenarioId] = useState<string | null>(null);

  useEffect(() => {
    try {
      const v = localStorage.getItem("eq.activeVessel");
      // Read after mount (not during render) to avoid a server/client hydration mismatch.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (v) setActive(v);
    } catch { /* storage unavailable: keep default */ }
  }, []);

  const setActiveVessel = (id: string) => {
    setActive(id);
    try { localStorage.setItem("eq.activeVessel", id); } catch { /* ignore */ }
  };

  const ctx: HmiCtx = { status, activeVessel, setActiveVessel, scenarioId, setScenarioId };
  const demo = path.startsWith("/demo");
  return (
    <Ctx.Provider value={ctx}>
      <div className="grid h-screen grid-cols-[208px_1fr] grid-rows-[48px_1fr_auto]">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-primary focus:p-2 focus:text-primary-foreground">Skip to content</a>
        <div className="col-span-2"><TopBar ctx={ctx} demo={demo} /></div>
        <SideNav activeVessel={activeVessel} />
        <main id="main" className={cn("hmi-grid overflow-y-auto p-4", demo && "outline outline-2 -outline-offset-2 outline-st-demo/60")}>
          {children}
        </main>
        <div className="col-span-2"><StatusBar status={status} /></div>
      </div>
    </Ctx.Provider>
  );
}
