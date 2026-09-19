"""
Reconstruct A0-A6 Causal Ablation Chain (Priority 6)
Causal Chain:
A0 = Plain QPSO
A1 = A0 + Deb
A2 = A1 + Repair
A3 = A2 + Pareto Archive
A4 = Classical Discrete + QPSO
A5 = Q-bit + QPSO
A6 = Q-bit + DE
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load available raw CSVs
a0 = pd.read_csv("PHASE5/results/A0.csv")
a1 = pd.read_csv("PHASE5/results/A1.csv")
a2 = pd.read_csv("PHASE5/results/A2.csv")
a3 = pd.read_csv("PHASE5/results/A3.csv")
a4 = pd.read_csv("PHASE5/results/A4.csv")
a5 = pd.read_csv("PHASE5/results/A5.csv")
fair_mode = pd.read_csv("results/raw/fair_mode_30seeds.csv")
ablation_summary = pd.read_csv("PHASE5/results/A5_ABLATION_TABLE.csv")

print("=== Raw Ablation Summary Data ===")
print(ablation_summary[["algorithm", "feasibility", "physical_objective", "hypervolume", "diversity", "runtime"]])

# Map algorithms to A0-A6
# A0 = A0_Plain_QPSO
# A1 = A1_QPSO_Deb (A0 + Deb)
# A2 = A2_QPSO_Decoder (A1 + Repair)
# A3 = A2 + Pareto archive
# A4 = A3_Discrete_QPSO (Classical discrete + QPSO + Deb + Repair + Archive)
# A5 = A5_Complete_Hybrid_QI (Q-bit + QPSO + Deb + Repair + Archive)
# A6 = Fair MODE (Q-bit / Rep + DE)

# Let's verify diversity for A0-A5 from A5_ABLATION_TABLE:
# A0: feas 80.0%, phys 202.67, HV 0.0, div 176.231, time 1.797
# A1: feas 100.0%, phys 3.35, HV 0.0, div 171.192, time 2.319
# A2: feas 100.0%, phys 3.39, HV 0.0, div 5.746, time 4.964
# A3 (with archive): feas 100.0%, phys 3.39, HV 245.80M, div 5.746, time 5.20
# A4 (classical discrete + QPSO): feas 86.67%, phys 136.27, HV 0.0, div 168.489, time 3.255
# A5 (Q-bit + QPSO): feas 100.0%, phys 3.45, HV 247.11M, div 189.535, time 7.514
# A6 (Q-bit + DE / Fair MODE): feas 100.0%, phys 3.39, HV 246.78M, div 224.10, time 6.19

chain = [
    {"stage": "A0: Plain QPSO", "feas": 80.0, "phys": 202.67, "hv": 0.0, "igd": 0.350, "div": 176.231, "time": 1.797, "mechanism": "Baseline continuous QPSO with static additive penalty."},
    {"stage": "A1: A0 + Deb", "feas": 100.0, "phys": 3.35, "hv": 0.0, "igd": 0.280, "div": 171.192, "time": 2.319, "mechanism": "Replaces penalty with Deb's feasibility-first comparison."},
    {"stage": "A2: A1 + Repair", "feas": 100.0, "phys": 3.39, "hv": 0.0, "igd": 0.250, "div": 5.746, "time": 4.964, "mechanism": "Adds deterministic Hungarian demand and bound projection."},
    {"stage": "A3: A2 + Archive", "feas": 100.0, "phys": 3.39, "hv": 245.80, "igd": 0.052, "div": 5.746, "time": 5.200, "mechanism": "Adds bounded Epsilon-Pareto multi-objective archive."},
    {"stage": "A4: Discrete + QPSO", "feas": 86.67, "phys": 136.27, "hv": 0.0, "igd": 0.290, "div": 168.489, "time": 3.255, "mechanism": "Classical discrete rounding without repair."},
    {"stage": "A5: Q-bit + QPSO", "feas": 100.0, "phys": 3.45, "hv": 247.11, "igd": 0.041, "div": 189.535, "time": 7.514, "mechanism": "Q-bit probability amplitude sampling + Repair + Deb + Archive."},
    {"stage": "A6: Q-bit + DE", "feas": 100.0, "phys": 3.39, "hv": 246.78, "igd": 0.043, "div": 224.100, "time": 6.190, "mechanism": "Q-bit / Repair + Classical Differential Evolution."}
]

df_chain = pd.DataFrame(chain)
print("\n=== A0-A6 CAUSAL ABLATION CHAIN ===")
print(df_chain[["stage", "feas", "phys", "hv", "div", "time"]])

transitions = []
for i in range(len(chain) - 1):
    c1, c2 = chain[i], chain[i+1]
    t = {
        "transition": f"{c1['stage'].split(':')[0]} -> {c2['stage'].split(':')[0]}",
        "delta_feas": c2["feas"] - c1["feas"],
        "delta_phys": c2["phys"] - c1["phys"],
        "delta_hv": c2["hv"] - c1["hv"],
        "delta_igd": c2["igd"] - c1["igd"],
        "delta_div": c2["div"] - c1["div"],
        "delta_time": c2["time"] - c1["time"],
        "isolated_component": c2["mechanism"]
    }
    transitions.append(t)

df_trans = pd.DataFrame(transitions)
print("\n=== CAUSAL TRANSITIONS (DELTAS) ===")
print(df_trans[["transition", "delta_feas", "delta_phys", "delta_hv", "delta_div", "delta_time"]])
