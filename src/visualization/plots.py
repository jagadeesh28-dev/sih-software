"""
Publication Figure Generator for Phase 5.
Generates all 18 mandatory figures specified in Section 32 of Phase 5 protocol:
01_A0_vs_A1_feasibility.png
02_A0_vs_A2_repair.png
03_A2_vs_A3_discrete_search.png
04_A3_vs_A4_qbit_contribution.png
05_A4_vs_A5_multiobjective.png
06_all_algorithm_convergence.png
07_feasibility_rate.png
08_candidate_feasibility.png
09_constraint_failure_taxonomy.png
10_pareto_front.png
11_hypervolume_comparison.png
12_scalability.png
13_runtime_scalability.png
14_qpso_failure_seed_1005.png
15_qpso_failure_seed_1021.png
16_qpso_failure_seed_1025.png
17_qpso_failure_seed_1029.png
18_small_scale_optimality_gap.png
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_all_phase5_figures(
    benchmark_data: Dict[str, Any],
    fig_dir: Path,
) -> None:
    """Renders and saves all 18 figures to fig_dir."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    all_results = benchmark_data["all_results"]
    ablation_df = benchmark_data["ablation_df"]
    small_df = benchmark_data["small_df"]
    scale_df = benchmark_data["scale_df"]
    failure_df = benchmark_data["failure_df"]

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # -------------------------------------------------------------
    # 01_A0_vs_A1_feasibility.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)
    a0_runs = pd.DataFrame(all_results["A0_Plain_QPSO"])
    a1_runs = pd.DataFrame(all_results["A1_QPSO_Deb"])

    feas = [float(np.mean(a0_runs["is_feasible"]) * 100.0), float(np.mean(a1_runs["is_feasible"]) * 100.0)]
    ax[0].bar(["A0 (Plain QPSO)", "A1 (QPSO + Deb)"], feas, color=["#d9534f", "#5cb85c"], width=0.5)
    ax[0].set_ylabel("Feasibility Rate (%)")
    ax[0].set_ylim(0, 110)
    ax[0].set_title("Run Feasibility: A0 vs. A1", fontweight="bold")
    for i, v in enumerate(feas):
        ax[0].text(i, v + 2, f"{v:.1f}%", ha="center", fontweight="bold")

    pen = [float(np.mean(a0_runs["penalty"])), float(np.mean(a1_runs["penalty"]))]
    ax[1].bar(["A0 (Plain QPSO)", "A1 (QPSO + Deb)"], pen, color=["#d9534f", "#5cb85c"], width=0.5)
    ax[1].set_ylabel("Mean Penalty Value ($)")
    ax[1].set_title("Mean Penalty: A0 vs. A1", fontweight="bold")
    for i, v in enumerate(pen):
        ax[1].text(i, v + 200, f"${v:.1f}", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "01_A0_vs_A1_feasibility.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 02_A0_vs_A2_repair.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    a2_runs = pd.DataFrame(all_results["A2_QPSO_Decoder"])
    algos = ["A0 (No Repair)", "A2 (Deterministic Repair)"]
    f_rates = [float(np.mean(a0_runs["is_feasible"]) * 100.0), float(np.mean(a2_runs["is_feasible"]) * 100.0)]
    ax.bar(algos, f_rates, color=["#f0ad4e", "#0275d8"], width=0.5)
    ax.set_ylabel("Feasibility Rate (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Impact of Deterministic Repair Operator (A0 vs. A2)", fontweight="bold")
    for i, v in enumerate(f_rates):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "02_A0_vs_A2_repair.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 03_A2_vs_A3_discrete_search.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    a2_entropies = [r["categorical_entropy"] for r in all_results["A2_QPSO_Decoder"] if r["categorical_entropy"]]
    a3_entropies = [r["categorical_entropy"] for r in all_results["A3_Discrete_QPSO"] if r["categorical_entropy"]]
    if a2_entropies and a3_entropies:
        mean_e2 = np.mean(a2_entropies, axis=0)
        mean_e3 = np.mean(a3_entropies, axis=0)
        ax.plot(mean_e2, label="A2 (Continuous Float Rounding)", color="#d9534f", linestyle="--")
        ax.plot(mean_e3, label="A3 (Discrete Operators + Diversity)", color="#0275d8", linewidth=2)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Mean Categorical Entropy (bits)")
    ax.set_title("Population Categorical Entropy over Iterations", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "03_A2_vs_A3_discrete_search.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 04_A3_vs_A4_qbit_contribution.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    a4_runs = pd.DataFrame(all_results["A4_Heterogeneous_QI"])
    a3_runs = pd.DataFrame(all_results["A3_Discrete_QPSO"])
    objs = [float(np.mean(a3_runs["best_fitness"])), float(np.mean(a4_runs["best_fitness"]))]
    ax.bar(["A3 (Classical Discrete)", "A4 (Q-Bit Probabilistic)"], objs, color=["#5bc0de", "#6f42c1"], width=0.5)
    ax.set_ylabel("Mean Fitness Value ($)")
    ax.set_title("Standalone Q-Bit Representation Contribution (A3 vs A4)", fontweight="bold")
    for i, v in enumerate(objs):
        ax.text(i, v + 200, f"{v:.1f}", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "04_A3_vs_A4_qbit_contribution.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 05_A4_vs_A5_multiobjective.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    a5_runs = pd.DataFrame(all_results["A5_Complete_Hybrid_QI"])
    hvs = [float(np.mean(a4_runs["pareto_hypervolume"])), float(np.mean(a5_runs["pareto_hypervolume"]))]
    ax.bar(["A4 (Penalty Only)", "A5 (Deb + Pareto Archive)"], hvs, color=["#6f42c1", "#28a745"], width=0.5)
    ax.set_ylabel("Hypervolume ($10^6$)")
    ax.set_title("Hypervolume: Standalone QI (A4) vs. Full Framework (A5)", fontweight="bold")
    for i, v in enumerate(hvs):
        ax.text(i, v + 1e5, f"{v:,.0f}", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "05_A4_vs_A5_multiobjective.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 06_all_algorithm_convergence.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    colors = {"A0_Plain_QPSO": "#d9534f", "A1_QPSO_Deb": "#f0ad4e", "A5_Complete_Hybrid_QI": "#28a745", "DE": "#0275d8", "PSO": "#6c757d", "GA": "#17a2b8", "Random": "#343a40"}
    for name, c in colors.items():
        if name in all_results:
            trajs = [r["convergence_trajectory"] for r in all_results[name] if r["convergence_trajectory"]]
            if trajs:
                min_len = min(len(t) for t in trajs)
                mean_traj = np.mean([t[:min_len] for t in trajs], axis=0)
                evals = np.linspace(50, 2500, min_len)
                ax.plot(evals, mean_traj, label=name, color=c, linewidth=2)
    ax.set_xlabel("Objective Evaluations")
    ax.set_ylabel("Best Objective / Fitness ($)")
    ax.set_yscale("log")
    ax.set_title("All Algorithms Convergence (Matched 2,500 Evaluations)", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "06_all_algorithm_convergence.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 07_feasibility_rate.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    algos = ablation_df["algorithm"]
    feas_vals = ablation_df["feasibility"]
    ax.bar(algos, feas_vals, color="#0275d8", width=0.6)
    ax.set_ylabel("Run Feasibility Rate (%)")
    ax.set_ylim(0, 115)
    ax.set_xticklabels(algos, rotation=35, ha="right")
    ax.set_title("Run-Level Feasibility Rate Across All Algorithms (N=30)", fontweight="bold")
    for i, v in enumerate(feas_vals):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "07_feasibility_rate.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 08_candidate_feasibility.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    cand_feas = []
    for name in algos:
        runs = all_results[name]
        cf = np.mean([r["candidate_feasibility_rate"] for r in runs])
        cand_feas.append(cf)
    ax.bar(algos, cand_feas, color="#17a2b8", width=0.6)
    ax.set_ylabel("Candidate-Level Feasibility Rate (%)")
    ax.set_xticklabels(algos, rotation=35, ha="right")
    ax.set_title("Candidate-Level Feasibility Rate (% of 2,500 candidates)", fontweight="bold")
    for i, v in enumerate(cand_feas):
        ax.text(i, v + 0.5, f"{v:.2f}%", ha="center", fontsize=9)
    plt.tight_layout()
    fig.savefig(fig_dir / "08_candidate_feasibility.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 09_constraint_failure_taxonomy.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    fail_cols = [c for c in failure_df.columns if c not in ["algorithm", "total_runs", "failed_runs"]]
    failure_df.set_index("algorithm")[fail_cols].plot(kind="bar", stacked=True, ax=ax, colormap="tab10")
    ax.set_ylabel("Total Failure Count")
    ax.set_title("10-Class Failure Taxonomy Distribution Across Algorithms", fontweight="bold")
    ax.legend(loc="upper right")
    plt.tight_layout()
    fig.savefig(fig_dir / "09_constraint_failure_taxonomy.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 10_pareto_front.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    # Scatter plot of feasible points from A5 and DE
    for name, c, m in [("A5_Complete_Hybrid_QI", "#28a745", "o"), ("DE", "#0275d8", "s")]:
        runs = all_results[name]
        fuels = [r["physical_objective"] for r in runs if r["is_feasible"]]
        penalties = [r["penalty"] for r in runs if r["is_feasible"]]
        ax.scatter(fuels, penalties, label=name, color=c, marker=m, alpha=0.8, s=60)
    ax.set_xlabel("Physical Operational Objective ($)")
    ax.set_ylabel("Total Penalty ($)")
    ax.set_title("Feasible Objective Trade-offs: A5 vs. DE", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "10_pareto_front.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 11_hypervolume_comparison.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    mo_algos = ["A5_Complete_Hybrid_QI", "NSGA3"]
    hv_vals = [float(np.mean([r["pareto_hypervolume"] for r in all_results[a]])) for a in mo_algos]
    ax.bar(mo_algos, hv_vals, color=["#28a745", "#ffc107"], width=0.5)
    ax.set_ylabel("Mean Hypervolume ($10^6$)")
    ax.set_title("Pareto Hypervolume: A5 vs. NSGA-III", fontweight="bold")
    for i, v in enumerate(hv_vals):
        ax.text(i, v + 1e5, f"{v:,.0f}", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "11_hypervolume_comparison.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 12_scalability.png & 13_runtime_scalability.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    for opt, c in [("A5_Complete_Hybrid_QI", "#28a745"), ("DE", "#0275d8")]:
        sub = scale_df[scale_df["optimizer"] == opt]
        ax.plot(sub["dimension"], sub["mean_objective"], marker="o", label=opt, color=c, linewidth=2)
    ax.set_xlabel("Decision Dimension (D = 6 * Vessels)")
    ax.set_ylabel("Mean Objective Value")
    ax.set_title("Scalability: Objective Value vs. Dimension D", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "12_scalability.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    for opt, c in [("A5_Complete_Hybrid_QI", "#28a745"), ("DE", "#0275d8")]:
        sub = scale_df[scale_df["optimizer"] == opt]
        ax.plot(sub["dimension"], sub["evaluations_per_second"], marker="s", label=opt, color=c, linewidth=2)
    ax.set_xlabel("Decision Dimension (D = 6 * Vessels)")
    ax.set_ylabel("Evaluations Per Second")
    ax.set_title("Scalability: Computational Throughput (evals/sec)", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "13_runtime_scalability.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 14 to 17: QPSO Failure Trajectories for Seeds 1005, 1021, 1025, 1029
    # -------------------------------------------------------------
    failed_seeds = [1005, 1021, 1025, 1029]
    fig_names = [
        "14_qpso_failure_seed_1005.png",
        "15_qpso_failure_seed_1021.png",
        "16_qpso_failure_seed_1025.png",
        "17_qpso_failure_seed_1029.png",
    ]

    for s, f_name in zip(failed_seeds, fig_names):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
        # Find run for this seed in A0
        r_a0 = next((r for r in all_results["A0_Plain_QPSO"] if r["seed"] == s), None)
        r_a1 = next((r for r in all_results["A1_QPSO_Deb"] if r["seed"] == s), None)
        r_a5 = next((r for r in all_results["A5_Complete_Hybrid_QI"] if r["seed"] == s), None)

        if r_a0 and r_a1 and r_a5:
            ax.plot(r_a0["convergence_trajectory"], label="A0 (Plain QPSO - Trapped)", color="#d9534f", linestyle="--")
            ax.plot(r_a1["convergence_trajectory"], label="A1 (QPSO + Deb - Escaped)", color="#f0ad4e")
            ax.plot(r_a5["convergence_trajectory"], label="A5 (Hybrid QI - Optimal)", color="#28a745", linewidth=2)

        ax.set_xlabel("Generation Iteration")
        ax.set_ylabel("Fitness Score ($)")
        ax.set_yscale("log")
        ax.set_title(f"Forensic Trajectory Breakdown: Seed {s}", fontweight="bold")
        ax.legend()
        plt.tight_layout()
        fig.savefig(fig_dir / f_name)
        plt.close(fig)

    # -------------------------------------------------------------
    # 18_small_scale_optimality_gap.png
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    ax.bar(small_df["algorithm"], small_df["optimality_gap_pct"], color="#6f42c1", width=0.5)
    ax.set_ylabel("Optimality Gap to Exact J* (%)")
    ax.set_xticklabels(small_df["algorithm"], rotation=30, ha="right")
    ax.set_title("Small-Scale Exact Validation: Optimality Gap (%)", fontweight="bold")
    for i, v in enumerate(small_df["optimality_gap_pct"]):
        ax.text(i, v + 0.1, f"{v:.2f}%", ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "18_small_scale_optimality_gap.png")
    plt.close(fig)
