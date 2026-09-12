"""
Deterministic Unit Normalization Layer.
Section 4: Explicit conversion tracking with audit logging.
Rejects ambiguous units and strictly forbids silent transformations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConversionRecord:
    """Audit log entry for an individual unit conversion."""
    field_name: str
    original_value: float
    original_unit: str
    canonical_value: float
    canonical_unit: str
    conversion_rule: str


class UnitNormalizationEngine:
    """
    Normalizes diverse incoming telemetry units into the canonical schema.
    Tracks every conversion in an internal audit trail.
    """

    SUPPORTED_CONVERSIONS = {
        # Speed: canonical = knots
        "speed": {
            "knots": (lambda v: v, "identity: value * 1.0", "knots"),
            "kn": (lambda v: v, "identity: value * 1.0", "knots"),
            "m_s": (lambda v: v * 1.943844, "multiply by 1.943844 (m/s to knots)", "knots"),
            "km_h": (lambda v: v / 1.852, "divide by 1.852 (km/h to knots)", "knots"),
        },
        # Power: canonical = kW
        "power": {
            "kw": (lambda v: v, "identity: value * 1.0", "kW"),
            "w": (lambda v: v / 1000.0, "divide by 1000.0 (W to kW)", "kW"),
            "mw": (lambda v: v * 1000.0, "multiply by 1000.0 (MW to kW)", "kW"),
            "hp": (lambda v: v * 0.745699872, "multiply by 0.745699872 (hp to kW)", "kW"),
        },
        # Instantaneous Fuel Flow: canonical = kg/h
        "fuel_flow": {
            "kg_h": (lambda v: v, "identity: value * 1.0", "kg/h"),
            "kg_per_hour": (lambda v: v, "identity: value * 1.0", "kg/h"),
            "g_s": (lambda v: v * 3.6, "multiply by 3.6 (g/s to kg/h)", "kg/h"),
            "tonnes_day": (lambda v: (v * 1000.0) / 24.0, "multiply by 1000/24 (tonnes/day to kg/h)", "kg/h"),
            "t_d": (lambda v: (v * 1000.0) / 24.0, "multiply by 1000/24 (t/d to kg/h)", "kg/h"),
        },
        # Mass (displacement, cargo): canonical = metric tonnes
        "mass_tonnes": {
            "tonnes": (lambda v: v, "identity: value * 1.0", "metric_tonnes"),
            "t": (lambda v: v, "identity: value * 1.0", "metric_tonnes"),
            "metric_tonnes": (lambda v: v, "identity: value * 1.0", "metric_tonnes"),
            "kg": (lambda v: v / 1000.0, "divide by 1000.0 (kg to metric tonnes)", "metric_tonnes"),
            "lbs": (lambda v: v * 0.00045359237, "multiply by 0.00045359237 (lbs to metric tonnes)", "metric_tonnes"),
        },
        # Torque: canonical = N*m
        "torque": {
            "nm": (lambda v: v, "identity: value * 1.0", "N·m"),
            "n_m": (lambda v: v, "identity: value * 1.0", "N·m"),
            "knm": (lambda v: v * 1000.0, "multiply by 1000.0 (kN·m to N·m)", "N·m"),
        },
        # Distance: canonical = meters
        "distance": {
            "m": (lambda v: v, "identity: value * 1.0", "meters"),
            "meters": (lambda v: v, "identity: value * 1.0", "meters"),
            "nm": (lambda v: v * 1852.0, "multiply by 1852.0 (nautical miles to meters)", "meters"),
            "km": (lambda v: v * 1000.0, "multiply by 1000.0 (km to meters)", "meters"),
            "feet": (lambda v: v * 0.3048, "multiply by 0.3048 (feet to meters)", "meters"),
        },
        # Wind & Current Speed: canonical = m/s
        "environmental_speed": {
            "m_s": (lambda v: v, "identity: value * 1.0", "m/s"),
            "knots": (lambda v: v * 0.514444, "multiply by 0.514444 (knots to m/s)", "m/s"),
            "kn": (lambda v: v * 0.514444, "multiply by 0.514444 (knots to m/s)", "m/s"),
            "km_h": (lambda v: v / 3.6, "divide by 3.6 (km/h to m/s)", "m/s"),
        },
        # Rotation: canonical = RPM
        "rotation": {
            "rpm": (lambda v: v, "identity: value * 1.0", "RPM"),
            "hz": (lambda v: v * 60.0, "multiply by 60.0 (Hz to RPM)", "RPM"),
            "rad_s": (lambda v: v * (60.0 / (2.0 * np.pi)), "multiply by 60/(2*pi) (rad/s to RPM)", "RPM"),
        },
    }

    def __init__(self):
        self.audit_records: List[ConversionRecord] = []

    def convert_value(
        self,
        value: float,
        quantity_type: str,
        from_unit: str,
        field_name: str = "unspecified",
    ) -> Tuple[float, ConversionRecord]:
        """
        Convert a single numerical value to canonical unit.
        Raises ValueError on unsupported or ambiguous units.
        """
        normalized_type = quantity_type.lower()
        normalized_unit = from_unit.lower().replace(" ", "_").replace("-", "_")

        if normalized_type not in self.SUPPORTED_CONVERSIONS:
            raise ValueError(f"Unknown quantity type '{quantity_type}'. Supported: {list(self.SUPPORTED_CONVERSIONS.keys())}")

        unit_map = self.SUPPORTED_CONVERSIONS[normalized_type]
        if normalized_unit not in unit_map:
            raise ValueError(
                f"Unsupported or ambiguous unit '{from_unit}' for quantity '{quantity_type}'. "
                f"Allowed units: {list(unit_map.keys())}"
            )

        func, rule, canonical_unit = unit_map[normalized_unit]
        converted = float(func(value))

        record = ConversionRecord(
            field_name=field_name,
            original_value=float(value),
            original_unit=from_unit,
            canonical_value=converted,
            canonical_unit=canonical_unit,
            conversion_rule=rule,
        )
        self.audit_records.append(record)
        return converted, record

    def normalize_dataframe(
        self,
        df: pd.DataFrame,
        unit_spec: Dict[str, Tuple[str, str]],
    ) -> pd.DataFrame:
        """
        Batch normalize a DataFrame given unit_spec mapping:
        {column_name: (quantity_type, from_unit)}
        """
        df_out = df.copy()
        for col, (q_type, from_unit) in unit_spec.items():
            if col in df_out.columns:
                converted_vals = []
                for val in df_out[col]:
                    if pd.isna(val):
                        converted_vals.append(val)
                    else:
                        c_val, _ = self.convert_value(float(val), q_type, from_unit, field_name=col)
                        converted_vals.append(c_val)
                df_out[col] = converted_vals
        return df_out

    def get_audit_trail(self) -> pd.DataFrame:
        """Export all logged unit conversions as a pandas DataFrame."""
        return pd.DataFrame([vars(r) for r in self.audit_records])
