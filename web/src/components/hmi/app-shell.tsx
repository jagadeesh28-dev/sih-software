"use client";

import {
  Activity, Anchor, BellRing, ClipboardList, FlaskConical, Fuel, Gauge, LayoutGrid, PlayCircle, Route, ScatterChart, Ship,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { FreshnessIndicator } from "@/components/hmi/primitives";
import { api, type Status } from "@/lib/api";
import { fmtTime, useApi, type Loadable } from "@/lib/hmi";
import { cn } from "@/lib/utils";

// ------------------------------------------------------------------ context

export type UserRole = "OPERATOR" | "ENGINEER" | "ADMIN";

interface HmiCtx {
  status: Loadable<Status>;
  activeVessel: string;
  setActiveVessel: (id: string) => void;
  scenarioId: string | null;
  setScenarioId: (id: string | null) => void;
  userRole: UserRole;
  setUserRole: (role: UserRole) => void;
}

const Ctx = createContext<HmiCtx | null>(null);

export function useHmi(): HmiCtx {
  const c = useContext(Ctx);
  if (!c) throw new Error("useHmi must be used inside <AppShell>");
  return c;
}

// ------------------------------------------------------------------ navigation

const WORKFLOW_NAV = [
  { href: "/fleet", label: "Fleet Overview", step: "01", icon: LayoutGrid },
  { href: "/vessel", label: "Vessel Performance", step: "02", icon: Ship },
  { href: "/trust", label: "Fuel Prediction", step: "03", icon: Gauge },
  { href: "/optimizer", label: "Fleet Optimization", step: "04", icon: Route },
  { href: "/pareto", label: "Decision Space", step: "05", icon: ScatterChart },
  { href: "/scenario", label: "Scenario Analysis", step: "06", icon: FlaskConical },
  { href: "/fuels", label: "Alternative Fuels", step: "07", icon: Fuel },
  { href: "/audit", label: "Operations Reports", step: "08", icon: ClipboardList },
];

const SECONDARY_NAV = [
  { href: "/alerts", label: "Operations Alerts", icon: BellRing },
  { href: "/health", label: "System Health & Diagnostics", icon: Activity },
  { href: "/demo", label: "Demonstration Suite", icon: PlayCircle },
];

function SideNav({ activeVessel }: { activeVessel: string }) {
  const path = usePathname();
  return (
    <nav aria-label="Marine operations console navigation" className="flex flex-col border-r border-rule/60 bg-sidebar p-2 text-xs">
      <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/70">
        Operator Workflow
      </div>
      <div className="flex flex-col gap-0.5">
        {WORKFLOW_NAV.map(({ href, label, step, icon: Icon }) => {
          const target = href === "/vessel" ? `/vessel/${activeVessel}` : href;
          const active = path === href || path.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={target}
              aria-current={active ? "page" : undefined}
              className={cn(
                "group flex items-center justify-between rounded-sm border-l-2 px-2 py-1.5 text-[13px] text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors",
                active ? "border-primary bg-sidebar-accent font-semibold text-sidebar-foreground" : "border-transparent text-muted-foreground",
              )}
            >
              <div className="flex items-center gap-2 truncate">
                <Icon className={cn("size-4 shrink-0", active ? "text-primary" : "text-muted-foreground/70")} aria-hidden />
                <span className="truncate">{label}</span>
              </div>
              <span className={cn("num text-[10px] opacity-40 group-hover:opacity-100", active && "opacity-80 text-primary")}>
                {step}
              </span>
            </Link>
          );
        })}
      </div>

      <div className="mt-4 px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/70">
        System & Verification
      </div>
      <div className="flex flex-col gap-0.5">
        {SECONDARY_NAV.map(({ href, label, icon: Icon }) => {
          const active = path === href || path.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex items-center gap-2 rounded-sm border-l-2 px-2 py-1.5 text-[12px] text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors",
                active ? "border-primary bg-sidebar-accent font-semibold text-sidebar-foreground" : "border-transparent text-muted-foreground",
              )}
            >
              <Icon className="size-4 shrink-0 text-muted-foreground/70" aria-hidden />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto rounded-sm border border-rule/50 bg-panel-2/30 p-2 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-1.5 font-medium text-foreground/80">
          <span className="size-1.5 rounded-full bg-st-normal" />
          <span>Active Vessel:</span>
        </div>
        <div className="num mt-1 truncate font-semibold text-primary">
          {activeVessel}
        </div>
      </div>
    </nav>
  );
}

// ------------------------------------------------------------------ top bar

function TopBar({ ctx, demo }: { ctx: HmiCtx; demo: boolean }) {
  const s = ctx.status.data;
  const nonNormalCount = s?.fleet_trust.filter((t) => t.state !== "NORMAL").length ?? 0;
  const isHealthy = s && nonNormalCount === 0;

  return (
    <header className={cn("flex h-12 items-center justify-between border-b border-rule/70 bg-sidebar px-3 select-none", demo && "border-b-2 border-st-demo")}>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 pr-3 border-r border-rule/60">
          <Anchor className="size-5 text-primary" aria-hidden />
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold tracking-[0.16em] text-foreground">EGREEN QUANTA</span>
            <span className="text-[10px] text-muted-foreground tracking-wider uppercase font-medium">Green Fleet Decision Support</span>
          </div>
        </div>

        {/* Operational Status Indicators */}
        <div className="hidden items-center gap-4 text-[11px] sm:flex">
          <div className="flex items-center gap-1.5 font-medium">
            <span className={cn("size-2 rounded-full", isHealthy ? "bg-st-normal" : "bg-st-warning animate-pulse")} />
            <span className="text-muted-foreground">FLEET:</span>
            <span className="font-semibold text-foreground">{isHealthy ? "OPERATIONAL" : `${nonNormalCount} ATTENTION`}</span>
          </div>

          {/* Compact Data Freshness State */}
          <FreshnessIndicator
            freshness={ctx.status.freshness}
            lastValidTimestamp={ctx.status.lastValidTimestamp ?? s?.server_time}
          />

          <div className="flex items-center gap-1.5 font-medium">
            <span className={cn("size-2 rounded-full", s?.evaluator_ready ? "bg-st-normal" : "bg-st-warning")} />
            <span className="text-muted-foreground">ENGINE:</span>
            <span className="font-semibold text-foreground">{s?.evaluator_ready ? "OPTIMIZER READY" : "INITIALIZING"}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Prototype Access Control Role Switcher */}
        <div className="flex items-center gap-1.5 border-r border-rule/60 pr-3">
          <div className="hidden flex-col text-right sm:flex">
            <span className="text-[9px] uppercase font-bold text-muted-foreground tracking-wider">Access Control</span>
            <span className="text-[9px] text-muted-foreground/70">Prototype simulation</span>
          </div>
          <select
            value={ctx.userRole}
            onChange={(e) => ctx.setUserRole(e.target.value as UserRole)}
            className="h-7 rounded border border-rule/70 bg-panel px-2 text-[11px] font-semibold text-foreground tracking-wide cursor-pointer focus:outline-hidden"
            aria-label="Active operator role (prototype simulation)"
          >
            <option value="OPERATOR">OPERATOR</option>
            <option value="ENGINEER">ENGINEER</option>
            <option value="ADMIN">ADMIN</option>
          </select>
        </div>

        {demo && (
          <span className="rounded-sm border border-st-demo bg-st-demo/15 px-2 py-0.5 text-[10px] font-bold tracking-wider text-st-demo uppercase">
            SIMULATION SUITE
          </span>
        )}
        <div className="text-right">
          <div className="num text-[11px] font-medium text-foreground">
            {s ? fmtTime(s.server_time).replace(" UTC", "Z") : "OFFLINE"}
          </div>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">UTC OPERATIONAL CLOCK</div>
        </div>
      </div>
    </header>
  );
}

// ------------------------------------------------------------------ status bar

function StatusBar({ status }: { status: Loadable<Status> }) {
  const s = status.data;
  return (
    <footer className="flex h-7 items-center justify-between border-t border-rule/60 bg-sidebar px-3 text-[11px] text-muted-foreground" aria-label="System status">
      <div className="flex items-center gap-4">
        <span>Fleet Dispatch: <strong className="text-foreground">{s ? `${s.fleet_count} Vessels Monitored` : "Connecting..."}</strong></span>
        <span className="hidden md:inline">Safety Envelope: <strong className="text-foreground">Continuous Boundary Validation</strong></span>
        <span className="hidden lg:inline">Decision Support: <strong className="text-foreground">Human-in-the-Loop Active</strong></span>
      </div>
      <div>
        <span>System Version: <span className="num text-foreground/80">1.1.0-marine-console</span></span>
      </div>
    </footer>
  );
}

// ------------------------------------------------------------------ shell

export function AppShell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const status = useApi(api.status, [], 10000);
  const [activeVessel, setActive] = useState("CPS_Poseidon");
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<UserRole>("OPERATOR");

  useEffect(() => {
    try {
      const v = localStorage.getItem("eq.activeVessel");
      if (v) setActive(v);
      const r = localStorage.getItem("eq.userRole");
      if (r === "OPERATOR" || r === "ENGINEER" || r === "ADMIN") setUserRole(r);
    } catch { /* storage unavailable */ }
  }, []);

  const setActiveVessel = (id: string) => {
    setActive(id);
    try { localStorage.setItem("eq.activeVessel", id); } catch { /* ignore */ }
  };

  const handleSetUserRole = (r: UserRole) => {
    setUserRole(r);
    try { localStorage.setItem("eq.userRole", r); } catch { /* ignore */ }
  };

  const ctx: HmiCtx = {
    status,
    activeVessel,
    setActiveVessel,
    scenarioId,
    setScenarioId,
    userRole,
    setUserRole: handleSetUserRole,
  };
  const demo = path.startsWith("/demo");

  return (
    <Ctx.Provider value={ctx}>
      <div className="grid h-screen grid-cols-[220px_1fr] grid-rows-[48px_1fr_28px]">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-primary focus:p-2 focus:text-primary-foreground">Skip to content</a>
        <div className="col-span-2"><TopBar ctx={ctx} demo={demo} /></div>
        <SideNav activeVessel={activeVessel} />
        <main id="main" className={cn("hmi-grid overflow-y-auto p-4", demo && "outline outline-1 -outline-offset-1 outline-st-demo/40")}>
          {children}
        </main>
        <div className="col-span-2"><StatusBar status={status} /></div>
      </div>
    </Ctx.Provider>
  );
}
