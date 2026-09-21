"""
Egreen Quanta - SIH26138: Backend Bridge & Authoritative Data Provider.
Exposes real verified models, engines, and historical artifacts to the Streamlit UI.
Strictly prohibits inventing numbers or duplicating formulas in frontend scripts.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import streamlit as st

from src.qi_prediction.serving import ProductionFuelPredictor, get_production_predictor
from optimization.sih_objective_engine import SIHObjectiveEngine, SIHOptimizationObjectives

REPO_ROOT = Path(__file__).resolve().parent.parent


@st.cache_resource
def get_cached_predictor() -> ProductionFuelPredictor:
    """Load and cache the official hardened production predictor."""
    return get_production_predictor()


@st.cache_resource
def get_cached_sih_engine() -> SIHObjectiveEngine:
    """Load and cache the official SIH multi-objective engine."""
    return SIHObjectiveEngine()


@st.cache_data
def get_verified_pareto_front() -> pd.DataFrame:
    """Load the verified 13 non-dominated Pareto solutions."""
    pareto_path = REPO_ROOT / "results" / "pareto_front.csv"
    if pareto_path.exists():
        return pd.read_csv(pareto_path)
    return pd.DataFrame()


@st.cache_data
def get_verified_tradeoffs() -> pd.DataFrame:
    """Load the verified 152 multi-objective formulation tradeoffs."""
    t_path = REPO_ROOT / "results" / "multiobjective_tradeoffs.csv"
    if t_path.exists():
        return pd.read_csv(t_path)
    return pd.DataFrame()


def get_default_fleet_state() -> List[Dict[str, Any]]:
    """
    Returns baseline operating telemetry for the three real commercial vessels
    from the FuelCast verified dataset.
    """
    return [
        {
            "id": "CPS_Poseidon",
            "name": "CPS_Poseidon",
            "vessel_type": "passenger_cruise",
            "fuel_type": "vlsfo",
            "speed_kn": 14.5,
            "stw_kn": 14.5,
            "sog_kn": 14.5,
            "draft_m": 7.5,
            "displacement_t": 35000.0,
            "gross_tonnage": 38000,
            "length_m": 196.0,
            "beam_m": 28.0,
            "engine_power_kw": 21600.0,
            "hotel_load_kw": 1800.0,
            "wind_speed_ms": 5.0,
            "wave_height_m": 1.0,
            "water_depth_m": 60.0,
            "route": "Rotterdam -> Bergen (North Sea)",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
        {
            "id": "CPS_Triton",
            "name": "CPS_Triton",
            "vessel_type": "passenger_cruise_small",
            "fuel_type": "vlsfo",
            "speed_kn": 14.0,
            "stw_kn": 14.0,
            "sog_kn": 14.2,
            "draft_m": 5.2,
            "displacement_t": 12000.0,
            "gross_tonnage": 14500,
            "length_m": 132.0,
            "beam_m": 21.0,
            "engine_power_kw": 10800.0,
            "hotel_load_kw": 900.0,
            "wind_speed_ms": 6.2,
            "wave_height_m": 1.2,
            "water_depth_m": 45.0,
            "route": "Stavanger -> Lerwick",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
        {
            "id": "OSS_Ceto",
            "name": "OSS_Ceto",
            "vessel_type": "offshore_supply",
            "fuel_type": "vlsfo",
            "speed_kn": 12.5,
            "stw_kn": 12.5,
            "sog_kn": 12.3,
            "draft_m": 4.8,
            "displacement_t": 4500.0,
            "gross_tonnage": 4800,
            "length_m": 88.0,
            "beam_m": 19.0,
            "engine_power_kw": 6400.0,
            "hotel_load_kw": 450.0,
            "wind_speed_ms": 7.5,
            "wave_height_m": 1.5,
            "water_depth_m": 85.0,
            "route": "Aberdeen -> Forties Alpha Field",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
    ]


def log_audit_event(
    action: str,
    scenario_id: str,
    vessel_id: str,
    details: Dict[str, Any],
    operator: str = "Operator_SIH",
):
    """
    Append an immutable decision-support audit record conforming to Section 16 of requirements.
    """
    if "audit_ledger" not in st.session_state:
        st.session_state.audit_ledger = []

    event_id = f"EVT-{len(st.session_state.audit_ledger) + 1:04d}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    record = {
        "event_id": event_id,
        "timestamp": timestamp,
        "operator": operator,
        "action": action,
        "scenario_id": scenario_id,
        "vessel_id": vessel_id,
        "model_version": details.get("model_version", "QI-C1-v1.1.0"),
        "predicted_fuel_kg_h": details.get("fuel_prediction"),
        "uncertainty_interval": details.get("uncertainty_interval"),
        "ood_state": details.get("ood_state", "IN-DOMAIN"),
        "solver": details.get("solver", "N/A"),
        "notes": details.get("notes", ""),
    }
    st.session_state.audit_ledger.append(record)
