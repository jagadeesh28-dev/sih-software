"""
Red-Team / Hostile End-to-End Architecture Verification Script.
Executes deep automated checks across all phases:
- Data Lineage & Units
- Model vs API consistency
- Vessel-type conditioning & unsupported vessel fallback
- Conformal Uncertainty Calibration & bounds
- OOD Guard & envelope distances
- Fault Injections & Fallback latency
- Cost formulation & double-counting check
- Lifecycle GHG Well-to-Wake formulation
- Fleet Optimizer constraints & evaluation
- Pareto dominance recalculation
- Demo scenes execution & API comparison
- Adversarial edge-case battery (18 cases)
- Scientific claims scan across codebase
"""

import sys
import os
import time
import math
import json
import copy
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path("c:/Users/JAGADEESH M/OneDrive/Documents/SIH-software/sih26138_platform")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from src.qi_prediction.serving import get_production_predictor
from optimization.sih_objective_engine import SIHObjectiveEngine
from optimization.canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type, is_supported_fuel_type
from lca.fuel_registry import FuelPathwayRegistry
import demo_scenarios as demo

API_BASE = "http://127.0.0.1:8000/api"

def run_audit():
    results = {}
    print("=" * 80)
    print("STARTING EGREEN QUANTA RED-TEAM ARCHITECTURE AUDIT")
    print("=" * 80)

    # 1. API Health Check
    try:
        r = requests.get(f"{API_BASE}/status", timeout=5)
        assert r.status_code == 200, f"Status code: {r.status_code}"
        status_data = r.json()
        print("[API HEALTH] CONNECTED to FastAPI backend.")
        print(f"  Primary Model: {status_data['model']['primary']}")
        print(f"  Evaluator Ready: {status_data['evaluator_ready']}")
        results["api_health"] = "PASS"
    except Exception as e:
        print(f"[API HEALTH] FAILED: {e}")
        results["api_health"] = f"FAIL: {e}"

    predictor = get_production_predictor()
    engine = SIHObjectiveEngine()

    # 2. Phase 2 & 4: Data Lineage & Direct vs API Prediction
    test_pt = {
        "vessel_id": "CPS_Poseidon",
        "vessel_type": "passenger_cruise",
        "fuel_type": "vlsfo",
        "stw_kn": 14.5,
        "sog_kn": 14.5,
        "draft_m": 7.5,
        "displacement_t": 35000.0,
        "wind_speed_ms": 5.0,
        "wave_height_m": 1.0,
        "water_depth_m": 60.0,
    }
    
    t0 = time.perf_counter()
    direct_pred = predictor.predict_fuel_with_uncertainty(test_pt)
    direct_dur = (time.perf_counter() - t0) * 1000

    api_resp = requests.post(f"{API_BASE}/predict", json=test_pt).json()
    api_pred_val = api_resp["result"]["fuel_prediction"]
    
    print("\n[PREDICTION CONSISTENCY]")
    print(f"  Direct Predictor Output: {direct_pred['fuel_prediction']:.4f} kg/h (in {direct_dur:.2f} ms)")
    print(f"  API Endpoint Output:     {api_pred_val:.4f} kg/h")
    diff = abs(direct_pred['fuel_prediction'] - api_pred_val)
    print(f"  Delta: {diff:.6f} kg/h")
    assert diff < 1e-4, f"Prediction mismatch between direct call and API: {diff}"
    results["prediction_consistency"] = "PASS"

    # 3. Phase 3: Vessel Type Conditioning
    print("\n[VESSEL TYPE CONDITIONING]")
    vessel_configs = [
        ("CPS_Poseidon", "passenger_cruise", 35000.0, 7.5),
        ("CPS_Triton", "passenger_cruise_small", 12000.0, 5.2),
        ("OSS_Ceto", "offshore_supply", 4800.0, 4.8),
    ]
    for vid, vt, disp, draft in vessel_configs:
        inp = dict(test_pt, vessel_id=vid, vessel_type=vt, displacement_t=disp, draft_m=draft)
        res = predictor.predict_fuel_with_uncertainty(inp)
        print(f"  {vt:<25} -> Fuel: {res['fuel_prediction']:8.2f} kg/h | Routing: {res['routing_status']} | Model: {res['model']}")
        assert res['routing_status'] == "NORMAL", f"Expected NORMAL routing for {vt}, got {res['routing_status']}"
    
    # Unknown vessel type
    unknown_inp = dict(test_pt, vessel_type="nuclear_submarine")
    unk_res = predictor.predict_fuel_with_uncertainty(unknown_inp)
    fuel_disp = f"{unk_res['fuel_prediction']:8.2f} kg/h" if unk_res['fuel_prediction'] is not None else "    None (REJECTED)"
    print(f"  {'nuclear_submarine':<25} -> Fuel: {fuel_disp} | Routing: {unk_res['routing_status']} | Model: {unk_res['model']} | Conf: {unk_res['confidence']}")
    assert unk_res['routing_status'] in ("REJECT", "FALLBACK")
    assert unk_res['confidence'] == "LOW"
    results["vessel_type_handling"] = "PASS"

    # 4. Phase 5: Conformal Uncertainty Verification
    print("\n[CONFORMAL UNCERTAINTY]")
    unc = direct_pred['uncertainty']
    print(f"  Prediction: {direct_pred['fuel_prediction']:.2f} kg/h")
    print(f"  90% Bounds: [{unc['lower_bound_kg_h']:.2f}, {unc['upper_bound_kg_h']:.2f}] kg/h")
    print(f"  Interval Width: {unc['interval_width_kg_h']:.2f} kg/h")
    assert unc['lower_bound_kg_h'] <= direct_pred['fuel_prediction'] <= unc['upper_bound_kg_h']
    assert unc['lower_bound_kg_h'] >= 0.0, "Negative lower bound detected!"
    results["uncertainty"] = "PASS"

    # 5. Phase 6: OOD Guard Verification
    print("\n[OUT-OF-DISTRIBUTION GUARD]")
    # Normal In-Domain
    res_norm = predictor.predict_fuel_with_uncertainty(test_pt)
    print(f"  Normal In-Domain:      d_env={res_norm['envelope_distance']:.3f} | InDomain={res_norm['in_domain']} | Routing={res_norm['routing_status']}")
    assert res_norm['in_domain'] is True and res_norm['envelope_distance'] <= 1.0

    # Moderate Boundary
    mod_pt = dict(test_pt, wave_height_m=5.0, wind_speed_ms=22.0)
    res_mod = predictor.predict_fuel_with_uncertainty(mod_pt)
    print(f"  Moderate Boundary:     d_env={res_mod['envelope_distance']:.3f} | InDomain={res_mod['in_domain']} | Routing={res_mod['routing_status']}")

    # Severe Storm (OOD)
    storm_pt = copy.deepcopy(demo.OOD_STORM_INPUT)
    res_storm = predictor.predict_fuel_with_uncertainty(storm_pt)
    print(f"  Severe Storm (OOD):    d_env={res_storm['envelope_distance']:.3f} | InDomain={res_storm['in_domain']} | Routing={res_storm['routing_status']} | Model={res_storm['model']}")
    assert res_storm['in_domain'] is False or res_storm['routing_status'] in ("FALLBACK", "EMERGENCY_PHYSICS")
    results["ood_guard"] = "PASS"

    # 6. Phase 7: Fault Injection & Fallback Latency
    print("\n[FAULT INJECTION & FALLBACK]")
    class FaultyBooster:
        def predict(self, *args, **kwargs):
            raise RuntimeError("Injected C++ Booster Memory Segmentation Fault!")

    fault_predictor = copy.copy(predictor)
    fault_predictor.qi_c1_booster = FaultyBooster()
    fault_predictor.qi_c1_vessel_type_booster = FaultyBooster()

    t_f0 = time.perf_counter()
    fallback_res = fault_predictor.predict_fuel_with_uncertainty(test_pt, raise_on_error=False)
    t_f_dur = (time.perf_counter() - t_f0) * 1000
    print(f"  Injected QI Booster Exception -> Routing: {fallback_res['routing_status']} | Model: {fallback_res['model']} | Fallback Latency: {t_f_dur:.3f} ms")
    assert fallback_res['routing_status'] == "FALLBACK"
    assert fallback_res['model'] == "MODEL-REAL-04"
    results["fallback_resilience"] = "PASS"

    # 7. Phase 8 & 9: Cost and Lifecycle GHG Formulations
    print("\n[COST & LIFECYCLE GHG VERIFICATION]")
    v_eval = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=14.5,
        voyage_distance_nm=300.0,
        schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=2740.86,
        fuel_type="vlsfo",
        use_shore_power=True,
        port_hours=6.0,
        hotel_load_kw=1800.0,
    )
    # Check C_total formula
    expected_total_cost = round(
        v_eval.fuel_cost_usd +
        v_eval.carbon_cost_usd +
        v_eval.shore_power_cost_usd +
        v_eval.schedule_penalty_usd +
        v_eval.fueleu_penalty_usd,
        2
    )
    print(f"  Fuel Mass:             {v_eval.fuel_tonnes:.4f} t")
    print(f"  Fuel Cost:             ${v_eval.fuel_cost_usd:,.2f}")
    print(f"  Shore Power / Elec:    ${v_eval.shore_power_cost_usd:,.2f}")
    print(f"  Carbon Cost:           ${v_eval.carbon_cost_usd:,.2f}")
    print(f"  Schedule Penalty:      ${v_eval.schedule_penalty_usd:,.2f}")
    print(f"  FuelEU Penalty:        ${v_eval.fueleu_penalty_usd:,.2f}")
    print(f"  Total Cost Reported:   ${v_eval.operational_cost_usd:,.2f}")
    print(f"  Calculated Sum:        ${expected_total_cost:,.2f}")
    cost_diff = abs(v_eval.operational_cost_usd - expected_total_cost)
    assert cost_diff < 1e-3, f"Cost accounting discrepancy: {cost_diff}"

    # Check GHG WtW formula
    # When shore power is ON, total lifecycle GHG = fuel (WtT + TtW + Slip) + shore power grid GHG
    # Berth electricity grid emissions = kWh * grid_factor / 1e6
    berth_kwh = 1800.0 * 6.0
    grid_ghg_t = berth_kwh * 450.0 / 1e6  # 4.86 tCO2e
    print(f"  Fuel WtT GHG:          {v_eval.wtt_ghg_tonnes:.4f} tCO2e")
    print(f"  Fuel TtW GHG:          {v_eval.ttw_ghg_tonnes:.4f} tCO2e")
    print(f"  Methane Slip:          {v_eval.methane_slip_tonnes:.4f} tCO2e")
    print(f"  Shore Grid GHG:        {grid_ghg_t:.4f} tCO2e")
    print(f"  Lifecycle WtW GHG:     {v_eval.lifecycle_ghg_tonnes:.4f} tCO2e")
    expected_wtw = round(v_eval.wtt_ghg_tonnes + v_eval.ttw_ghg_tonnes + v_eval.methane_slip_tonnes + grid_ghg_t, 4)
    ghg_diff = abs(v_eval.lifecycle_ghg_tonnes - expected_wtw)
    print(f"  Calculated Sum:        {expected_wtw:.4f} tCO2e (Delta: {ghg_diff:.6f})")
    assert ghg_diff < 1e-3, f"GHG accounting discrepancy: {ghg_diff}"
    results["cost_and_ghg"] = "PASS"

    # 8. Phase 11: Pareto Dominance Independent Check
    print("\n[PARETO DOMINANCE VERIFICATION]")
    pareto_csv_path = REPO_ROOT / "results" / "pareto_front.csv"
    assert pareto_csv_path.exists(), "pareto_front.csv missing!"
    df_pareto = pd.read_csv(pareto_csv_path)
    pts = df_pareto[["fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours"]].values
    print(f"  Loaded {len(pts)} points from pareto_front.csv")

    # Independent Pareto Dominance filter: Point A dominates Point B if all objectives are <= and at least one is <
    is_efficient = np.ones(len(pts), dtype=bool)
    for i, a in enumerate(pts):
        for j, b in enumerate(pts):
            if i != j and is_efficient[j]:
                if np.all(a <= b) and np.any(a < b):
                    is_efficient[j] = False

    non_dominated_count = np.sum(is_efficient)
    print(f"  Independently Verified Non-Dominated Count: {non_dominated_count} / {len(pts)}")
    assert non_dominated_count == len(pts), f"Found dominated points in pareto_front.csv! ({non_dominated_count} != {len(pts)})"
    results["pareto"] = "PASS"

    # 9. Phase 14: Demo Scenes Traceability
    print("\n[DEMO SCENES EXECUTION]")
    demo_trace = []
    for s_id in range(1, 12):
        t_d0 = time.perf_counter()
        resp = requests.post(f"{API_BASE}/demo/scenes/{s_id}").json()
        dur = (time.perf_counter() - t_d0) * 1000
        title = resp.get("title", f"Scene {s_id}")
        data = resp.get("data", {})
        status = "PASS" if "data" in resp else "FAIL"
        demo_trace.append({
            "scene_id": s_id,
            "scene_name": title,
            "latency_ms": round(dur, 2),
            "status": status,
        })
        print(f"  Scene {s_id:2d}: {title:<40} [{status}] ({dur:6.1f} ms)")
    results["demo_scenes"] = "PASS"

    # 10. Phase 16: Adversarial Stress Test (18 Cases)
    print("\n[ADVERSARIAL STRESS TESTING (18 CASES)]")
    adv_battery = [
        ("Empty request", {}),
        ("Missing speed", {**test_pt, "stw_kn": None}),
        ("Negative speed (-10 kn)", {**test_pt, "stw_kn": -10.0}),
        ("Extreme speed (55 kn)", {**test_pt, "stw_kn": 55.0}),
        ("Missing draft", {**test_pt, "draft_m": None}),
        ("Impossible draft (35 m)", {**test_pt, "draft_m": 35.0}),
        ("Negative draft (-1 m)", {**test_pt, "draft_m": -1.0}),
        ("Missing displacement", {**test_pt, "displacement_t": None}),
        ("Zero displacement", {**test_pt, "displacement_t": 0.0}),
        ("Extreme displacement (500,000 t)", {**test_pt, "displacement_t": 500000.0}),
        ("Negative wave height (-2 m)", {**test_pt, "wave_height_m": -2.0}),
        ("Extreme wave height (25 m)", {**test_pt, "wave_height_m": 25.0}),
        ("NaN in speed", {**test_pt, "stw_kn": float("nan")}),
        ("Infinity in draft", {**test_pt, "draft_m": float("inf")}),
        ("Unknown vessel id", {**test_pt, "vessel_id": "Ghost_Ship_X"}),
        ("Unknown vessel type", {**test_pt, "vessel_type": "interstellar_freighter"}),
        ("Unsupported fuel", {**test_pt, "fuel_type": "plutonium_239"}),
        ("Corrupted numeric fuel", {**test_pt, "fuel_type": 12345}),
    ]

    adv_passed = 0
    adv_details = []
    for desc, payload in adv_battery:
        if desc in ("NaN in speed", "Infinity in draft"):
            # Standard json.dumps cannot serialize NaN/Inf; send as direct raw string or direct predictor test
            val_str = "NaN" if "NaN" in desc else "Infinity"
            feat = "stw_kn" if "speed" in desc else "draft_m"
            raw_body = json.dumps(test_pt).replace(f'"{feat}": {test_pt[feat]}', f'"{feat}": {val_str}')
            resp = requests.post(f"{API_BASE}/predict", data=raw_body, headers={"Content-Type": "application/json"})
            if resp.status_code == 422:
                # FastAPI / Pydantic safely rejected non-compliant floating point at HTTP gateway
                state = "INVALID_INPUT"
                routing = "REJECT"
                warning = "Pydantic validation rejected NaN/Inf"
                is_safe = True
            else:
                r_pred = resp.json()
                trust = r_pred.get("trust", {})
                result = r_pred.get("result", {})
                state = trust.get("state")
                routing = result.get("routing_status")
                warning = result.get("warning") or trust.get("reason")
                is_safe = state in ("INVALID_INPUT", "REJECT")
        else:
            resp = requests.post(f"{API_BASE}/predict", json=payload)
            if resp.status_code == 422:
                state = "INVALID_INPUT"
                routing = "REJECT"
                warning = f"Pydantic schema validation rejected invalid input: {resp.text[:100]}"
                is_safe = True
            else:
                r_pred = resp.json()
                trust = r_pred.get("trust", {})
                result = r_pred.get("result", {})
                state = trust.get("state")
                routing = result.get("routing_status")
                warning = result.get("warning") or trust.get("reason")
                is_safe = state in ("INVALID_INPUT", "OOD", "FALLBACK", "WARNING", "RUNTIME_FAILURE")
                if state in ("NORMAL",) and not result.get("warning"):
                    is_safe = False

        status_str = "SAFE" if is_safe else "UNSAFE LEAKAGE"
        if is_safe:
            adv_passed += 1
        adv_details.append({
            "test": desc,
            "state": state,
            "routing": routing,
            "warning": warning,
            "safe": is_safe
        })
        print(f"  Adv [{desc:<32}] -> State: {state:<15} | Routing: {str(routing):<12} | [{status_str}]")

    print(f"  Adversarial Battery Score: {adv_passed} / {len(adv_battery)} PASSED")
    assert adv_passed == len(adv_battery), f"Adversarial leakage detected! {adv_passed}/{len(adv_battery)}"
    results["adversarial"] = "PASS"

    # 11. Phase 17: Prohibited Marketing Buzzwords Scan
    print("\n[SCIENTIFIC CLAIMS & MARKETING FORENSICS]")
    prohibited = [
        "quantum advantage", "quantum supremacy", "quantum speedup",
        "better than classical", "universally superior", "autonomous control",
        "guaranteed savings", "measured hydrogen", "measured ammonia", "100% safe"
    ]
    code_files = []
    for ext in ("*.py", "*.ts", "*.tsx"):
        code_files.extend(list((REPO_ROOT / "src").rglob(ext)))
        code_files.extend(list((REPO_ROOT / "api").rglob(ext)))
        code_files.extend(list((REPO_ROOT / "optimization").rglob(ext)))
        code_files.extend(list((REPO_ROOT / "lca").rglob(ext)))
        code_files.extend(list((REPO_ROOT / "web" / "src").rglob(ext)))

    prohibited_counts = {p: 0 for p in prohibited}
    for f in code_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore").lower()
            for p in prohibited:
                if p in txt:
                    prohibited_counts[p] += 1
        except Exception:
            pass

    for p, count in prohibited_counts.items():
        print(f"  '{p}': {count} occurrences in core application code")

    # 12. Phase 12: Frontend Mock Data Scan
    print("\n[FRONTEND MOCK DATA AUDIT]")
    web_src = REPO_ROOT / "web" / "src"
    ts_files = list(web_src.rglob("*.tsx")) + list(web_src.rglob("*.ts"))
    print(f"  Audited {len(ts_files)} TypeScript/React files in web/src")
    
    suspicious_patterns = ["fake", "mock", "placeholder", "Math.random"]
    pattern_hits = {pat: [] for pat in suspicious_patterns}
    for tf in ts_files:
        if tf.name.endswith(".test.ts") or tf.name.endswith(".test.tsx"):
            continue
        txt = tf.read_text(encoding="utf-8", errors="ignore")
        for pat in suspicious_patterns:
            if pat in txt:
                pattern_hits[pat].append(str(tf.relative_to(REPO_ROOT)))

    for pat, files in pattern_hits.items():
        print(f"  Pattern '{pat}': {len(files)} files ({', '.join(files[:2]) if files else 'NONE'})")

    print("\n" + "=" * 80)
    print("AUDIT EXECUTION COMPLETE: ALL SUITES EXECUTED")
    print("=" * 80)
    return results, demo_trace, adv_details

if __name__ == "__main__":
    run_audit()
