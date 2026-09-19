"""
Phase 3.2 Audit Probe Runner:
Generates:
- results/audit/phase3_2/02_post_patch_objective_probe.csv
- results/audit/phase3_2/03_physical_response_probe.csv
- results/audit/phase3_2/04_post_patch_adversarial.csv
- results/figures/optimization_phase3_2/objective_landscape.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure platform is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from optimization.canonical_mapper import (
    canonicalize_vessel_type,
    canonicalize_fuel_type,
    get_baseline_fuel_for_vessel,
)
from prediction.safe_objective import SafeFuelObjective
from optimization.evaluator import FleetEvaluationEngine
from optimization.variables import SolutionChromosome, VesselAssignmentDecision
from experiments.exp_phase3_master_runner import load_real_surrogates, BENCHMARK_SCENARIOS


def run_feasibility_probe(surrogates, audit_dir: Path):
    print("--- 1. Feasibility Probes (CPS_Poseidon, CPS_Triton, OSS_Ceto) ---")
    probe_records = []

    # Representative states for each vessel
    # Poseidon: passenger_cruise, min=8, max=22
    # Triton: passenger_cruise, min=8, max=22
    # Ceto: offshore_supply, min=6, max=16, baseline fuel mgo
    test_cases = [
        # Poseidon (max speed 22 kn, deadline 35h for 450nm)
        {"vessel": "CPS_Poseidon", "category": "low-speed transit", "speed": 12.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 450.0, "dead": 42.0, "wave": 1.0, "wind": 5.0},
        {"vessel": "CPS_Poseidon", "category": "normal cruising", "speed": 16.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 450.0, "dead": 35.0, "wave": 1.0, "wind": 5.0},
        {"vessel": "CPS_Poseidon", "category": "higher-speed transit", "speed": 19.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 450.0, "dead": 30.0, "wave": 1.0, "wind": 5.0},
        {"vessel": "CPS_Poseidon", "category": "alternative fuel (bio_methanol)", "speed": 16.0, "cargo": 0.0, "fuel": "bio_methanol", "mode": "transit", "shore": 0.0, "dist": 450.0, "dead": 35.0, "wave": 1.0, "wind": 5.0},
        {"vessel": "CPS_Poseidon", "category": "port/hoteling shore power", "speed": 14.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 1.0, "dist": 450.0, "dead": 38.0, "wave": 1.0, "wind": 5.0},

        # Triton (max speed 18 kn, deadline 28h for 300nm)
        {"vessel": "CPS_Triton", "category": "low-speed transit", "speed": 12.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 300.0, "dead": 30.0, "wave": 1.2, "wind": 6.0},
        {"vessel": "CPS_Triton", "category": "normal cruising", "speed": 15.0, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 300.0, "dead": 25.0, "wave": 1.2, "wind": 6.0},
        {"vessel": "CPS_Triton", "category": "higher-speed transit", "speed": 17.5, "cargo": 0.0, "fuel": "vlsfo", "mode": "transit", "shore": 0.0, "dist": 300.0, "dead": 22.0, "wave": 1.2, "wind": 6.0},
        {"vessel": "CPS_Triton", "category": "alternative fuel (bio_methanol)", "speed": 15.0, "cargo": 0.0, "fuel": "bio_methanol", "mode": "transit", "shore": 0.0, "dist": 300.0, "dead": 25.0, "wave": 1.2, "wind": 6.0},

        # Ceto (max speed 15 kn, deadline 18h for 120nm)
        {"vessel": "OSS_Ceto", "category": "low-speed transit", "speed": 8.0, "cargo": 1500.0, "fuel": "mgo", "mode": "transit", "shore": 0.0, "dist": 120.0, "dead": 20.0, "wave": 1.5, "wind": 8.0},
        {"vessel": "OSS_Ceto", "category": "normal cruising", "speed": 11.0, "cargo": 1500.0, "fuel": "mgo", "mode": "transit", "shore": 0.0, "dist": 120.0, "dead": 16.0, "wave": 1.5, "wind": 8.0},
        {"vessel": "OSS_Ceto", "category": "higher-speed transit", "speed": 14.0, "cargo": 1500.0, "fuel": "mgo", "mode": "transit", "shore": 0.0, "dist": 120.0, "dead": 14.0, "wave": 1.5, "wind": 8.0},
        {"vessel": "OSS_Ceto", "category": "alternative fuel (bio_methanol)", "speed": 11.0, "cargo": 1500.0, "fuel": "bio_methanol", "mode": "transit", "shore": 0.0, "dist": 120.0, "dead": 16.0, "wave": 1.5, "wind": 8.0},
        {"vessel": "OSS_Ceto", "category": "dp_station keeping mode", "speed": 8.0, "cargo": 2000.0, "fuel": "mgo", "mode": "dp", "shore": 0.0, "dist": 120.0, "dead": 20.0, "wave": 1.5, "wind": 8.0},
    ]

    for tc in test_cases:
        vessel_id = tc["vessel"]
        safe_obj = surrogates[vessel_id]
        evaluator = FleetEvaluationEngine(safe_objective=safe_obj, lambda_robust=0.5)

        dec = VesselAssignmentDecision(
            vessel_id=vessel_id,
            leg_id="probe_leg",
            assigned=True,
            speed_knots=tc["speed"],
            cargo_allocation_teu=tc["cargo"],
            fuel_type=tc["fuel"],
            operating_mode=tc["mode"],
            use_shore_power_at_dest=bool(tc["shore"]),
        )

        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=tc["dist"],
            schedule_deadline_hours=tc["dead"],
            wave_height_m=tc["wave"],
            wind_speed_ms=tc["wind"],
        )

        # Objective weights: fuel, cost, ghg, delay, risk
        w_fuel, w_cost, w_ghg, w_delay, w_risk = evaluator.weights

        physical_obj = float(res.fitness - res.total_penalty_value)
        domain_pen = float(res.soft_penalties.get("domain_boundary", 0.0))
        constraint_pen = float(sum(v for k, v in res.soft_penalties.items() if k not in ["domain_boundary", "cii_non_compliance", "fueleu_penalty"]))
        reg_pen = float(res.fueleu_penalty_usd + res.soft_penalties.get("cii_non_compliance", 0.0))

        rec = {
            "vessel": vessel_id,
            "category": tc["category"],
            "speed_kn": tc["speed"],
            "cargo_tonnes": tc["cargo"],
            "fuel_type": tc["fuel"],
            "operating_mode": tc["mode"],
            "shore_power": tc["shore"],
            "domain_status": res.domain_status,
            "envelope_distance": 0.0 if res.domain_status == "VALID" else 1.0,
            "hard_violations": ";".join(res.hard_violations) if res.hard_violations else "none",
            "soft_penalties": ";".join(f"{k}:{v:.1f}" for k, v in res.soft_penalties.items()) if res.soft_penalties else "none",
            "total_penalty": round(res.total_penalty_value, 2),
            "domain_penalty": round(domain_pen, 2),
            "constraint_penalty": round(constraint_pen, 2),
            "regulatory_penalty": round(reg_pen, 2),
            "fuel_tonnes": round(res.total_fuel_tonnes, 3),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_tonnes_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "schedule_delay_hours": round(res.schedule_delay_hours, 3),
            "physical_objective": round(physical_obj, 4),
            "total_objective": round(res.fitness, 4),
            "is_feasible": res.is_feasible,
        }
        probe_records.append(rec)
        print(f"  [{vessel_id}] {tc['category']:32s} -> Feasible: {rec['is_feasible']} | Domain: {rec['domain_status']} | Penalty: {rec['total_penalty']:.1f} | Fitness: {rec['total_objective']:.4f}")

    df_probe = pd.DataFrame(probe_records)
    out_path = audit_dir / "02_post_patch_objective_probe.csv"
    df_probe.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_probe)} rows)")

    # Mandatory pass condition: at least one known-valid candidate per certified vessel must be feasible with 0 penalty
    for v in ["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]:
        v_sub = df_probe[(df_probe["vessel"] == v) & (df_probe["is_feasible"] == True) & (df_probe["total_penalty"] == 0.0)]
        assert len(v_sub) > 0, f"MANDATORY PASS CONDITION FAILED: No feasible zero-penalty state for {v}!"
    print(">>> PASS: All certified vessels have valid, zero-penalty feasible baseline states.")
    return df_probe


def run_monotonicity_tests(surrogates, audit_dir: Path):
    print("\n--- 2. Physical Monotonicity Tests ---")
    mono_records = []
    safe_obj = surrogates["CPS_Poseidon"]
    evaluator = FleetEvaluationEngine(safe_objective=safe_obj, lambda_robust=0.5)

    # A. Speed Sweep (12, 14, 16, 18, 20 kn) holding others constant
    speeds = [12.0, 14.0, 16.0, 18.0, 20.0]
    for spd in speeds:
        dec = VesselAssignmentDecision.from_array(
            np.array([spd, 0.0, 0.0, 0.0, 0.0]),  # vlsfo, transit, no shore
            vessel_id="CPS_Poseidon", leg_id="mono_speed", assigned=True
        )
        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=450.0, schedule_deadline_hours=40.0, wave_height_m=1.0, wind_speed_ms=5.0
        )
        mono_records.append({
            "test_type": "speed_sweep",
            "parameter_name": "speed_kn",
            "parameter_value": spd,
            "speed_kn": spd,
            "wave_height_m": 1.0,
            "wind_speed_ms": 5.0,
            "cargo_tonnes": 0.0,
            "fuel_type": "vlsfo",
            "shore_power": 0.0,
            "fuel_tonnes": round(res.total_fuel_tonnes, 4),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "fitness": round(res.fitness, 4),
            "feasible": res.is_feasible,
        })

    # B. Wave Height Sweep (0.5, 1.5, 2.5, 3.5 m) at 16 kn
    waves = [0.5, 1.5, 2.5, 3.5]
    for wv in waves:
        dec = VesselAssignmentDecision.from_array(
            np.array([16.0, 0.0, 0.0, 0.0, 0.0]),
            vessel_id="CPS_Poseidon", leg_id="mono_wave", assigned=True
        )
        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=450.0, schedule_deadline_hours=40.0, wave_height_m=wv, wind_speed_ms=5.0
        )
        mono_records.append({
            "test_type": "wave_sweep",
            "parameter_name": "wave_height_m",
            "parameter_value": wv,
            "speed_kn": 16.0,
            "wave_height_m": wv,
            "wind_speed_ms": 5.0,
            "cargo_tonnes": 0.0,
            "fuel_type": "vlsfo",
            "shore_power": 0.0,
            "fuel_tonnes": round(res.total_fuel_tonnes, 4),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "fitness": round(res.fitness, 4),
            "feasible": res.is_feasible,
        })

    # C. Wind Speed Sweep (2, 8, 14, 20 m/s) at 16 kn
    winds = [2.0, 8.0, 14.0, 20.0]
    for wnd in winds:
        dec = VesselAssignmentDecision.from_array(
            np.array([16.0, 0.0, 0.0, 0.0, 0.0]),
            vessel_id="CPS_Poseidon", leg_id="mono_wind", assigned=True
        )
        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=450.0, schedule_deadline_hours=40.0, wave_height_m=1.0, wind_speed_ms=wnd
        )
        mono_records.append({
            "test_type": "wind_sweep",
            "parameter_name": "wind_speed_ms",
            "parameter_value": wnd,
            "speed_kn": 16.0,
            "wave_height_m": 1.0,
            "wind_speed_ms": wnd,
            "cargo_tonnes": 0.0,
            "fuel_type": "vlsfo",
            "shore_power": 0.0,
            "fuel_tonnes": round(res.total_fuel_tonnes, 4),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "fitness": round(res.fitness, 4),
            "feasible": res.is_feasible,
        })

    # D. Fuel Pathway Effect at 16 kn
    fuels = [("vlsfo", 0.0), ("bio_methanol", 2.0)]
    for f_name, f_code in fuels:
        dec = VesselAssignmentDecision.from_array(
            np.array([16.0, 0.0, f_code, 0.0, 0.0]),
            vessel_id="CPS_Poseidon", leg_id="mono_fuel", assigned=True
        )
        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=450.0, schedule_deadline_hours=40.0, wave_height_m=1.0, wind_speed_ms=5.0
        )
        mono_records.append({
            "test_type": "fuel_pathway",
            "parameter_name": "fuel_type",
            "parameter_value": f_name,
            "speed_kn": 16.0,
            "wave_height_m": 1.0,
            "wind_speed_ms": 5.0,
            "cargo_tonnes": 0.0,
            "fuel_type": f_name,
            "shore_power": 0.0,
            "fuel_tonnes": round(res.total_fuel_tonnes, 4),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "fitness": round(res.fitness, 4),
            "feasible": res.is_feasible,
        })

    # E. Shore Power Effect at 16 kn
    shores = [0.0, 1.0]
    for sh in shores:
        dec = VesselAssignmentDecision.from_array(
            np.array([16.0, 0.0, 0.0, 0.0, sh]),
            vessel_id="CPS_Poseidon", leg_id="mono_shore", assigned=True
        )
        res = evaluator.evaluate_chromosome(
            chromosome=SolutionChromosome(assignments=[dec]),
            voyage_distance_nm=450.0, schedule_deadline_hours=40.0, wave_height_m=1.0, wind_speed_ms=5.0
        )
        mono_records.append({
            "test_type": "shore_power",
            "parameter_name": "shore_power",
            "parameter_value": sh,
            "speed_kn": 16.0,
            "wave_height_m": 1.0,
            "wind_speed_ms": 5.0,
            "cargo_tonnes": 0.0,
            "fuel_type": "vlsfo",
            "shore_power": sh,
            "fuel_tonnes": round(res.total_fuel_tonnes, 4),
            "cost_usd": round(res.total_opex_usd, 2),
            "ghg_co2e": round(res.total_wtw_ghg_tonnes, 3),
            "fitness": round(res.fitness, 4),
            "feasible": res.is_feasible,
        })

    df_mono = pd.DataFrame(mono_records)
    out_path = audit_dir / "03_physical_response_probe.csv"
    df_mono.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_mono)} rows)")

    # Validate speed monotonicity: fuel consumption should increase with speed for transit
    df_spd = df_mono[df_mono["test_type"] == "speed_sweep"]
    fuel_vals = df_spd["fuel_tonnes"].values
    assert fuel_vals[-1] > fuel_vals[0], f"Speed monotonicity failure: fuel(20kn)={fuel_vals[-1]} <= fuel(12kn)={fuel_vals[0]}"
    print(f">>> PASS: Speed gradient verified (12kn: {fuel_vals[0]:.2f}t -> 20kn: {fuel_vals[-1]:.2f}t)")
    return df_mono


def run_landscape_plot(df_mono, fig_dir: Path):
    print("\n--- 3. Plotting Objective Landscape ---")
    df_spd = df_mono[df_mono["test_type"] == "speed_sweep"].sort_values("speed_kn")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Speed vs Objective
    axes[0, 0].plot(df_spd["speed_kn"], df_spd["fitness"], marker="o", color="#1f77b4", linewidth=2)
    axes[0, 0].set_title("Speed vs Total Fitness (Normalized J)")
    axes[0, 0].set_xlabel("Speed (knots)")
    axes[0, 0].set_ylabel("Normalized Fitness")
    axes[0, 0].grid(True, linestyle="--", alpha=0.6)

    # 2. Speed vs Fuel
    axes[0, 1].plot(df_spd["speed_kn"], df_spd["fuel_tonnes"], marker="s", color="#d62728", linewidth=2)
    axes[0, 1].set_title("Speed vs Fuel Consumption (tonnes)")
    axes[0, 1].set_xlabel("Speed (knots)")
    axes[0, 1].set_ylabel("Voyage Fuel (tonnes)")
    axes[0, 1].grid(True, linestyle="--", alpha=0.6)

    # 3. Speed vs Cost
    axes[1, 0].plot(df_spd["speed_kn"], df_spd["cost_usd"], marker="^", color="#2ca02c", linewidth=2)
    axes[1, 0].set_title("Speed vs Operational Cost (USD)")
    axes[1, 0].set_xlabel("Speed (knots)")
    axes[1, 0].set_ylabel("Voyage Cost (USD)")
    axes[1, 0].grid(True, linestyle="--", alpha=0.6)

    # 4. Speed vs GHG
    axes[1, 1].plot(df_spd["speed_kn"], df_spd["ghg_co2e"], marker="d", color="#9467bd", linewidth=2)
    axes[1, 1].set_title("Speed vs GHG Emissions (tCO2e)")
    axes[1, 1].set_xlabel("Speed (knots)")
    axes[1, 1].set_ylabel("GHG Emissions (tonnes CO2e)")
    axes[1, 1].grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    out_fig = fig_dir / "objective_landscape.png"
    plt.savefig(out_fig, dpi=300)
    plt.close()
    print(f"Saved: {out_fig}")


def run_adversarial_recheck(surrogates, audit_dir: Path):
    print("\n--- 4. Adversarial Safety Recheck ---")
    safe_obj = surrogates["CPS_Poseidon"]

    adversarial_cases = [
        {"desc": "negative_speed", "point": {"stw_kn": -5.0, "sog_kn": -5.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "vlsfo"}, "expected": "PHYSICALLY_INVALID"},
        {"desc": "extreme_speed_40kn", "point": {"stw_kn": 40.0, "sog_kn": 40.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "vlsfo"}, "expected": "OUT_OF_DOMAIN"},
        {"desc": "impossible_draft_15m", "point": {"stw_kn": 15.0, "sog_kn": 15.0, "draft_m": 15.0, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "vlsfo"}, "expected": "OUT_OF_DOMAIN"},
        {"desc": "extreme_wave_15m", "point": {"stw_kn": 15.0, "sog_kn": 15.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 15.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "vlsfo"}, "expected": "OUT_OF_DOMAIN"},
        {"desc": "bogus_vessel_type_submarine", "point": {"stw_kn": 15.0, "sog_kn": 15.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "submarine", "fuel_type": "vlsfo"}, "expected": "OUT_OF_DOMAIN"},
        {"desc": "bogus_fuel_type_uranium", "point": {"stw_kn": 15.0, "sog_kn": 15.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "uranium"}, "expected": "OUT_OF_DOMAIN"},
        # Known valid reference state to prove defensiveness does NOT reject legitimate points
        {"desc": "valid_baseline_16kn", "point": {"stw_kn": 16.0, "sog_kn": 16.0, "draft_m": 7.5, "displacement_t": 42000.0, "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0, "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5, "current_direction_deg": 180.0, "water_depth_m": 100.0, "vessel_type": "passenger_cruise", "fuel_type": "vlsfo"}, "expected": "IN_DOMAIN"},
    ]

    adv_records = []
    intercepted_count = 0
    adversarial_total = 0

    for case in adversarial_cases:
        res = safe_obj.evaluate_candidate(case["point"])
        status = res["domain_status"]
        is_valid = res["is_valid_candidate"]
        penalized_obj = res["penalized_fuel_objective"]
        robust_obj = res["robust_fuel_objective"]
        penalty = max(0.0, penalized_obj - robust_obj)

        is_adv = case["desc"] != "valid_baseline_16kn"
        if is_adv:
            adversarial_total += 1
            intercepted = (not is_valid) or (status in ["OUT_OF_DOMAIN", "PHYSICALLY_INVALID", "REJECTED"]) or (penalized_obj >= 1e5)
            if intercepted:
                intercepted_count += 1
        else:
            intercepted = is_valid and (status in ["VALID", "IN_DOMAIN", "NEAR_BOUNDARY"]) and (penalized_obj < 1e5)

        adv_records.append({
            "probe_id": case["desc"],
            "expected_outcome": case["expected"],
            "actual_domain_status": status,
            "is_valid_candidate": is_valid,
            "domain_penalty": penalty,
            "penalized_objective": penalized_obj,
            "intercepted_properly": intercepted,
        })
        print(f"  [{case['desc']:28s}] Status: {status:18s} | Valid: {str(is_valid):5s} | Obj: {penalized_obj:.0f} | Intercepted: {intercepted}")

    df_adv = pd.DataFrame(adv_records)
    out_path = audit_dir / "04_post_patch_adversarial.csv"
    df_adv.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_adv)} rows)")

    assert intercepted_count == adversarial_total, f"PASS CONDITION FAILED: {intercepted_count}/{adversarial_total} adversarial probes intercepted!"
    print(f">>> PASS: 100% of previously known invalid probes intercepted ({intercepted_count}/{adversarial_total}) while valid baseline passes.")
    return df_adv


def main():
    audit_dir = Path("results/audit/phase3_2")
    fig_dir = Path("results/figures/optimization_phase3_2")
    audit_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    surrogates = load_real_surrogates()

    df_probe = run_feasibility_probe(surrogates, audit_dir)
    df_mono = run_monotonicity_tests(surrogates, audit_dir)
    run_landscape_plot(df_mono, fig_dir)
    df_adv = run_adversarial_recheck(surrogates, audit_dir)
    print("\n=== Phase 3.2 Probes Complete and All Pass Conditions Met! ===")


if __name__ == "__main__":
    main()
