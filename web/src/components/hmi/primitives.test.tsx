import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { STATE_META } from "@/lib/hmi";
import { DataState, PlanStatus, StateBadge } from "./primitives";

afterEach(cleanup);

describe("StateBadge", () => {
  it("always renders a text label (never colour alone)", () => {
    for (const state of Object.keys(STATE_META)) {
      cleanup();
      render(<StateBadge state={state} />);
      const el = screen.getByRole("status");
      expect(el.textContent).toBe(STATE_META[state as keyof typeof STATE_META].label);
      expect(el.querySelector("svg")).not.toBeNull();
    }
  });

  it("renders OOD differently from NORMAL", () => {
    render(<><StateBadge state="NORMAL" /><StateBadge state="OOD" /></>);
    const [normal, ood] = screen.getAllByRole("status");
    expect(ood.className).not.toBe(normal.className);
    expect(ood.textContent).toBe("OUT OF DOMAIN");
  });

  it("maps unknown states to RUNTIME FAILURE rather than NORMAL", () => {
    render(<StateBadge state="SOMETHING_NEW" />);
    expect(screen.getByRole("status").textContent).toBe("RUNTIME FAILURE");
  });
});

describe("DataState", () => {
  const base = { reload: () => {}, loading: false };
  it("shows an error and no value when the backend fails", () => {
    render(<DataState state={{ ...base, data: undefined, error: "503: warming" }}>{() => <span>VALUE</span>}</DataState>);
    expect(screen.getByRole("alert").textContent).toMatch(/503: warming/);
    expect(screen.queryByText("VALUE")).toBeNull();
  });
  it("shows loading before data arrives", () => {
    render(<DataState state={{ ...base, data: undefined, loading: true }}>{() => <span>VALUE</span>}</DataState>);
    expect(screen.getByRole("status").textContent).toMatch(/Loading/);
  });
  it("shows an empty state instead of a blank screen", () => {
    render(<DataState state={{ ...base, data: [] as number[] }} empty={(d) => d.length === 0}>{() => <span>VALUE</span>}</DataState>);
    expect(screen.getByText(/No records returned/)).toBeTruthy();
  });
});

describe("PlanStatus", () => {
  it("never calls a soft-penalised or infeasible plan penalty-free", () => {
    const { container, rerender } = render(<PlanStatus plan={{ feasible: true, penalty_free: true }} />);
    expect(container.textContent).toBe("FEASIBLE — PENALTY-FREE");
    rerender(<PlanStatus plan={{ feasible: true, penalty_free: false, soft_penalties: { schedule_delay: 500 } }} />);
    expect(container.textContent).toContain("SOFT PENALTIES");
    expect(container.textContent).not.toContain("PENALTY-FREE");
    rerender(<PlanStatus plan={{ feasible: false }} />);
    expect(container.textContent).not.toContain("FEASIBLE —");
  });
});
