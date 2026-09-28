# Phase 3.1 — Sensitivity Analysis Audit

## Forensic Analysis of EXP-OPT-11 through EXP-OPT-14
- Fuel price sweep ($400 - $1200 / tonne): Optimal speed remained completely frozen at 18.59 knots.
- Carbon price sweep ($0 - $180 / tonne): Optimal speed remained completely frozen at 18.59 knots.
- Risk parameter $\lambda$ sweep (0.0 to 2.0): Optimal speed remained completely frozen at 18.59 knots.
- Wave height sweep (0.5m to 4.5m): Optimal speed varied slightly (18.08 to 19.51 kn) purely because involuntary weather speed loss changed the commanded speed calculation to maintain schedule.

## Audit Finding
Because the optimizer was pinned against the +115,000 penalty cliff, variations in economic parameters (fuel price, carbon price) produced zero change in optimal operational speed or fuel choice.
The sensitivity trends were completely suppressed by penalty dominance.
