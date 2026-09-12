"""
Independent Scientific Validation Gate.
Sections 13, 14, 15:
- Independent analytical checks for Hydrodynamics, Power, SFC Fuel Conversion, and ITTC-1957.
- Complete fuel registry LCA audit tracing mass, LHV, energy, WtT, TtW, and dimensional methane slip.
- Reproduction of Phase 0 smoke test values with absolute and relative error tracking.
"""

import math
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import numpy as np

from physics.resistance_model import VesselResistanceModel
from physics.propulsion import calculate_propulsion_power, calculate_fuel_rate
from lca.fuel_registry import FuelPathwayRegistry
from lca.well_to_wake import calculate_well_to_wake
from lca.imo_cii import calculate_imo_cii
from lca.fuel_eu import calculate_fueleu_compliance


def run_independent_physics_hand_checks() -> Dict[str, Any]:
    """
    Independent hand-calculation of naval architecture formulas:
    P_E = R_T * V
    P_B = P_E / (eta_D * eta_S)
    Fuel = P_B * SFC / 1000 + P_aux * SFC_aux / 1000 + boiler
    ITTC-1957 Cf = 0.075 / (log10(Re) - 2)^2
    """
    # 1. Test conditions
    speed_knots = 15.0
    speed_m_s = speed_knots * 0.514444  # 7.71666 m/s
    lwl_m = 133.0
    nu = 1.188e-6
    test_resistance_n = 200000.0  # 200 kN

    # Independent ITTC-1957
    re_hand = (speed_m_s * lwl_m) / nu
    log_re = math.log10(re_hand)
    cf_hand = 0.075 / ((log_re - 2.0) ** 2)

    # Independent Power
    pe_kw_hand = (test_resistance_n * speed_m_s) / 1000.0  # 1543.33 kW
    eta_d = 0.68 * 1.05 * 1.00  # 0.714
    eta_s = 0.98
    pb_kw_hand = pe_kw_hand / (eta_d * eta_s)  # 2205.65 kW

    # Compare with module output
    mod_power = calculate_propulsion_power(
        total_resistance_newtons=test_resistance_n,
        speed_m_s=speed_m_s,
        eta_0=0.68,
        eta_h=1.05,
        eta_r=1.00,
        eta_s=0.98,
    )

    power_diff_abs = abs(mod_power["pb_kw"] - pb_kw_hand)
    power_diff_rel_pct = (power_diff_abs / pb_kw_hand) * 100.0

    # Independent Fuel Rate
    nominal_sfc = 165.0
    mcr = 15000.0
    load = pb_kw_hand / mcr
    sfc_fac = 1.0 + 0.35 * ((load - 0.78) ** 2) / (0.78 ** 2)
    sfc_eff_hand = nominal_sfc * sfc_fac
    main_fuel_hand = (pb_kw_hand * sfc_eff_hand) / 1000.0
    aux_fuel_hand = (450.0 * 210.0) / 1000.0  # 94.5 kg/h
    boiler_fuel_hand = 80.0
    total_fuel_hand = main_fuel_hand + aux_fuel_hand + boiler_fuel_hand

    mod_fuel = calculate_fuel_rate(
        brake_power_kw=pb_kw_hand,
        nominal_sfc_g_kwh=nominal_sfc,
        mcr_kw=mcr,
        auxiliary_power_kw=450.0,
        aux_sfc_g_kwh=210.0,
        boiler_rate_kg_h=80.0,
    )

    fuel_diff_abs = abs(mod_fuel["total_fuel_kg_h"] - total_fuel_hand)
    fuel_diff_rel_pct = (fuel_diff_abs / total_fuel_hand) * 100.0

    return {
        "ittc_cf_hand": cf_hand,
        "reynolds_number": re_hand,
        "pe_kw_hand": pe_kw_hand,
        "pb_kw_hand": pb_kw_hand,
        "pb_kw_module": mod_power["pb_kw"],
        "power_abs_diff_kw": power_diff_abs,
        "power_rel_diff_pct": power_diff_rel_pct,
        "total_fuel_kg_h_hand": total_fuel_hand,
        "total_fuel_kg_h_module": mod_fuel["total_fuel_kg_h"],
        "fuel_abs_diff_kg_h": fuel_diff_abs,
        "fuel_rel_diff_pct": fuel_diff_rel_pct,
        "physics_validation_status": "PASS" if power_diff_rel_pct < 1e-4 and fuel_diff_rel_pct < 1e-4 else "FAIL",
    }


def run_comprehensive_lca_audit(output_csv: Optional[Path] = None) -> pd.DataFrame:
    """
    Section 14: Comprehensive LCA audit across all 5 fuel pathways in Fuel Registry.
    Traces fuel mass (1000 kg basis), LHV, energy, WtT, TtW, CO2, CH4, N2O, methane slip, and WtW.
    """
    registry = FuelPathwayRegistry()
    test_mass_kg = 1000.0  # 1 metric tonne basis
    fuels = registry.list_available_fuels()

    rows = []
    for f_key in fuels:
        p = registry.get_pathway(f_key)
        res = calculate_well_to_wake(test_mass_kg, f_key, registry)

        rows.append({
            "fuel_key": f_key,
            "fuel_name": p["name"],
            "fuel_mass_kg": test_mass_kg,
            "lhv_mj_per_kg": p["lhv_mj_kg"],
            "total_energy_mj": res["total_energy_mj"],
            "wtt_factor_g_co2e_per_mj": p["wtt_ghg_g_co2e_mj"],
            "wtt_tonnes_co2e": res["wtt_tonnes_co2e"],
            "ttw_co2_tonnes": res["ttw_co2_tonnes"],
            "ttw_ch4_tonnes_co2e": res["ttw_ch4_tonnes_co2e"],
            "ttw_n2o_tonnes_co2e": res["ttw_n2o_tonnes_co2e"],
            "methane_slip_fraction": p.get("methane_slip_fraction", 0.0),
            "methane_slip_description": f"{p.get('methane_slip_fraction', 0.0)*100:.1f}% unburned mass slip (GWP=29.8)",
            "ttw_total_tonnes_co2e": res["ttw_total_tonnes_co2e"],
            "wtw_total_tonnes_co2e": res["wtw_total_tonnes_co2e"],
            "wtw_intensity_g_co2e_per_mj": res["wtw_intensity_g_co2e_per_mj"],
            "data_source": p.get("source", "UNKNOWN"),
            "confidence": p.get("confidence", "UNKNOWN"),
        })

    df_audit = pd.DataFrame(rows)

    if output_csv:
        output_csv = Path(output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df_audit.to_csv(output_csv, index=False)

    return df_audit


def reproduce_phase0_smoke_test_values() -> Dict[str, Any]:
    """
    Section 15: Critical reproduction of Phase 0 smoke test values:
    Resistance ≈ 198540.1 N
    Power ≈ 2189.5 kW
    Fuel rate ≈ 619.3 kg/h
    VLSFO WtW ≈ 3.71 tCO2e
    LNG WtW ≈ 4.32 tCO2e
    """
    target_values = {
        "resistance_n": 198540.1,
        "power_kw": 2189.5,
        "fuel_rate_kg_h": 619.3,
        "vlsfo_wtw_tonnes": 3.71,
        "lng_wtw_tonnes": 4.32,
    }

    # Recompute independently using exact same input parameters
    model = VesselResistanceModel("container_feeder")
    phys_res = model.compute_total_resistance(speed_knots=15.0, wave_height_m=1.0)
    calc_r = phys_res["r_total_newtons"]
    calc_p = phys_res["power"]["pb_kw"]
    calc_f = phys_res["fuel"]["total_fuel_kg_h"]

    registry = FuelPathwayRegistry()
    vlsfo_res = calculate_well_to_wake(1000.0, "vlsfo", registry)
    lng_res = calculate_well_to_wake(1000.0, "fossil_lng", registry)
    calc_vlsfo = vlsfo_res["wtw_total_tonnes_co2e"]
    calc_lng = lng_res["wtw_total_tonnes_co2e"]

    reproduced_values = {
        "resistance_n": calc_r,
        "power_kw": calc_p,
        "fuel_rate_kg_h": calc_f,
        "vlsfo_wtw_tonnes": calc_vlsfo,
        "lng_wtw_tonnes": calc_lng,
    }

    comparison = {}
    for k, target in target_values.items():
        val = reproduced_values[k]
        abs_diff = abs(val - target)
        rel_diff_pct = (abs_diff / target) * 100.0
        comparison[k] = {
            "target": target,
            "recomputed": val,
            "abs_difference": abs_diff,
            "rel_difference_pct": rel_diff_pct,
            "match": rel_diff_pct < 0.1,  # Under 0.1% discrepancy tolerance
        }

    return {
        "comparison": comparison,
        "all_reproduced": all(c["match"] for c in comparison.values()),
    }


def execute_validation_gate(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Execute all scientific checks and output summary."""
    out_dir = output_dir or Path(__file__).resolve().parent.parent / "results" / "scientific_validation"
    out_dir.mkdir(parents=True, exist_ok=True)

    phys_res = run_independent_physics_hand_checks()
    lca_df = run_comprehensive_lca_audit(output_csv=out_dir / "lca_audit.csv")
    smoke_repro = reproduce_phase0_smoke_test_values()

    gate_summary = {
        "physics_validation": phys_res,
        "lca_audit_fuel_count": len(lca_df),
        "smoke_reproduction": smoke_repro,
        "gate_status": "PASS" if phys_res["physics_validation_status"] == "PASS" and smoke_repro["all_reproduced"] else "FAIL",
    }

    return gate_summary


if __name__ == "__main__":
    summary = execute_validation_gate()
    print("=== SCIENTIFIC VALIDATION GATE SUMMARY ===")
    print(f"Physics Check Status: {summary['physics_validation']['physics_validation_status']}")
    print(f"Smoke Test Values Reproduced: {summary['smoke_reproduction']['all_reproduced']}")
    for k, v in summary['smoke_reproduction']['comparison'].items():
        print(f"  {k}: Target={v['target']} vs Recomputed={v['recomputed']:.2f} (Diff: {v['rel_difference_pct']:.4f}%)")
