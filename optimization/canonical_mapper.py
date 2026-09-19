"""
Canonical Vocabulary & Category Normalization Interface.
SIH26138 - Phase 3.2 Correction Patch.

Provides deterministic, bi-directional normalization of vessel class families
and marine fuel types between raw telemetry schemas, naval architectural profiles,
and optimization decision vectors.
"""

from typing import Dict, List, Optional, Set

# Canonical Vessel Category Vocabulary
# Derived directly from FuelCast telemetry, MARPOL Annex VI, and fleet configuration.
CANONICAL_VESSEL_TYPES: Set[str] = {
    "passenger_cruise",
    "passenger_cruise_small",
    "offshore_supply",
    "cargo_feeder",
}

# Alias mapping from various schemas and historical code into canonical vocabulary
VESSEL_TYPE_ALIASES: Dict[str, str] = {
    # Cruise passenger variants
    "cruise_passenger": "passenger_cruise",
    "cruise": "passenger_cruise",
    "passenger": "passenger_cruise",
    "passenger_cruise": "passenger_cruise",
    "cps_poseidon": "passenger_cruise",
    
    # Small / expedition cruise variants
    "passenger_cruise_small": "passenger_cruise_small",
    "small_cruise": "passenger_cruise_small",
    "cruise_small": "passenger_cruise_small",
    "cps_triton": "passenger_cruise_small",

    # Offshore supply variants
    "offshore_supply": "offshore_supply",
    "osv": "offshore_supply",
    "psv": "offshore_supply",
    "supply": "offshore_supply",
    "offshore": "offshore_supply",
    "oss_ceto": "offshore_supply",

    # Cargo feeder variants
    "cargo_feeder": "cargo_feeder",
    "container": "cargo_feeder",
    "container_feeder": "cargo_feeder",
    "feeder": "cargo_feeder",
    "cargo": "cargo_feeder",
}

# Canonical Marine Fuel Vocabulary
CANONICAL_FUEL_TYPES: Set[str] = {
    "vlsfo",
    "mgo",
    "lsmgo",
    "hfo",
    "bio_methanol",
    "fossil_lng",
    "green_ammonia",
    "liquid_hydrogen",
}

FUEL_TYPE_ALIASES: Dict[str, str] = {
    "vlsfo": "vlsfo",
    "very_low_sulfur_fuel_oil": "vlsfo",
    "mgo": "mgo",
    "marine_gas_oil": "mgo",
    "lsmgo": "lsmgo",
    "hfo": "hfo",
    "heavy_fuel_oil": "hfo",
    "bio_methanol": "bio_methanol",
    "biomethanol": "bio_methanol",
    "methanol": "bio_methanol",
    "fossil_lng": "fossil_lng",
    "lng": "fossil_lng",
    "green_ammonia": "green_ammonia",
    "ammonia": "green_ammonia",
    "liquid_hydrogen": "liquid_hydrogen",
    "hydrogen": "liquid_hydrogen",
}

# Calibrated Baseline Fuels per Vessel Class (from real FuelCast telemetry)
VESSEL_BASELINE_FUELS: Dict[str, str] = {
    "passenger_cruise": "vlsfo",
    "passenger_cruise_small": "vlsfo",
    "offshore_supply": "mgo",
    "cargo_feeder": "vlsfo",
}


def canonicalize_vessel_type(vessel_type: str) -> str:
    """
    Map raw or historical vessel type string to canonical representation.
    If already canonical, returns clean lowercase.
    If unknown and not aliasable, returns the original lowercase string (which DomainChecker will flag).
    """
    if not vessel_type:
        return ""
    clean = str(vessel_type).strip().lower()
    return VESSEL_TYPE_ALIASES.get(clean, clean)


def canonicalize_fuel_type(fuel_type: str) -> str:
    """
    Map raw or historical fuel type string to canonical representation.
    """
    if not fuel_type:
        return ""
    clean = str(fuel_type).strip().lower()
    return FUEL_TYPE_ALIASES.get(clean, clean)


def get_baseline_fuel_for_vessel(vessel_id_or_class: str) -> str:
    """
    Retrieve the baseline training fuel used for first-principles/ML surrogate calibration.
    """
    v_norm = canonicalize_vessel_type(vessel_id_or_class)
    if "ceto" in vessel_id_or_class.lower() or v_norm == "offshore_supply":
        return "mgo"
    return VESSEL_BASELINE_FUELS.get(v_norm, "vlsfo")
