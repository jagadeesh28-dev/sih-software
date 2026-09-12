"""
IMO Carbon Intensity Indicator (CII) Compliance Module.
Reference: IMO Resolution MEPC.338(76) & MARPOL Annex VI Regulation 28.
Note: Distinct from WtW lifecycle intensity. CII is strictly Tank-to-Wake operational CO2 based.
"""

from typing import Dict, Any


def calculate_imo_cii(
    ship_type: str,
    capacity_dwt: float,
    co2_emissions_grams: float,
    distance_nautical_miles: float,
    reduction_factor_pct: float = 11.0,  # 2026 default baseline
) -> Dict[str, Any]:
    """
    Calculate Attained and Required CII, compliance margin, and rating (A through E).

    Inputs:
        ship_type: Ship category ('container', 'bulk_carrier', 'tanker', etc.)
        capacity_dwt: Deadweight tonnage (dwt) or gross tonnage for passenger
        co2_emissions_grams: Total operational CO2 emitted (grams)
        distance_nautical_miles: Distance travelled laden and ballast (nm)
        reduction_factor_pct: Configurable annual reduction factor Z% (default 11% for 2026)

    Returns:
        Dict containing:
            attained_cii: Attained operational CII (g CO2 / (dwt * nm))
            required_cii: Required annual target CII
            margin_pct: ((Required - Attained) / Required) * 100
            rating: Rating letter ('A', 'B', 'C', 'D', 'E')
            is_compliant: True if rating in ['A', 'B', 'C']
    """
    if distance_nautical_miles <= 0.0 or capacity_dwt <= 0.0:
        return {
            "attained_cii": 0.0,
            "required_cii": 0.0,
            "margin_pct": 0.0,
            "rating": "UNKNOWN",
            "is_compliant": False,
        }

    # 1. Attained CII: Grams CO2 / (Capacity * Distance)
    transport_work = capacity_dwt * distance_nautical_miles
    attained_cii = co2_emissions_grams / max(transport_work, 1.0)

    # 2. Reference Line CII_ref = a * Capacity^(-c)
    # IMO reference parameters for container ships (MEPC.338(76)):
    # a = 1984, c = 0.489
    # Bulk carriers: a = 4745, c = 0.622
    if "container" in ship_type.lower():
        a, c = 1984.0, 0.489
    else:  # General bulk baseline
        a, c = 4745.0, 0.622

    cii_ref = a * (capacity_dwt ** (-c))

    # 3. Required CII = CII_ref * (1 - Z / 100)
    required_cii = cii_ref * (1.0 - (reduction_factor_pct / 100.0))

    # 4. Rating Boundaries (ratio = attained / required)
    ratio = attained_cii / max(required_cii, 1e-6)
    if ratio <= 0.83:
        rating = "A"
    elif ratio <= 0.94:
        rating = "B"
    elif ratio <= 1.06:
        rating = "C"
    elif ratio <= 1.19:
        rating = "D"
    else:
        rating = "E"

    is_compliant = rating in ["A", "B", "C"]
    margin_pct = ((required_cii - attained_cii) / required_cii) * 100.0

    return {
        "attained_cii": attained_cii,
        "cii_ref": cii_ref,
        "required_cii": required_cii,
        "ratio_attained_over_required": ratio,
        "margin_pct": margin_pct,
        "rating": rating,
        "is_compliant": is_compliant,
    }
