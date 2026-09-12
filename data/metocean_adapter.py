"""
Environmental & Metocean Data Adapter Interface.
Section 11: Modular adapter for ECMWF ERA5 reanalysis, CMEMS, or calibrated synthetic grids.
Separates metocean metadata and spatial resolution configs from vessel telemetry.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class MetoceanObservation:
    """Standardized point environmental observation."""
    timestamp: str
    latitude: float
    longitude: float
    wave_height_m: float
    wave_period_s: float
    wave_direction_deg: float
    wind_speed_ms: float
    wind_direction_deg: float
    current_speed_ms: float
    current_direction_deg: float
    source_product: str
    spatial_resolution_deg: float


class BaseMetoceanAdapter(ABC):
    """Abstract Base Class for environmental data providers."""

    @abstractmethod
    def query_point(
        self,
        timestamp: datetime,
        latitude: float,
        longitude: float,
    ) -> MetoceanObservation:
        """Query environmental conditions at a given space-time coordinate."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return dataset provider, grid resolution, and coverage metadata."""
        pass


class CalibratedBenchmarkMetoceanAdapter(BaseMetoceanAdapter):
    """
    Adapter reading standardized synthetic metocean regimes or test grids.
    Explicitly tags all outputs with synthetic source product.
    """

    def __init__(self, default_regime: str = "moderate"):
        self.default_regime = default_regime
        self.regimes = {
            "calm": {
                "wave_height_m": 0.5, "wave_period_s": 5.0, "wave_direction_deg": 0.0,
                "wind_speed_ms": 3.0, "wind_direction_deg": 0.0,
                "current_speed_ms": 0.2, "current_direction_deg": 0.0,
            },
            "moderate": {
                "wave_height_m": 1.5, "wave_period_s": 7.0, "wave_direction_deg": 15.0,
                "wind_speed_ms": 7.5, "wind_direction_deg": 20.0,
                "current_speed_ms": 0.5, "current_direction_deg": 10.0,
            },
            "monsoon": {
                "wave_height_m": 3.5, "wave_period_s": 9.5, "wave_direction_deg": 30.0,
                "wind_speed_ms": 13.0, "wind_direction_deg": 35.0,
                "current_speed_ms": 1.2, "current_direction_deg": 25.0,
            },
            "extreme": {
                "wave_height_m": 6.0, "wave_period_s": 12.0, "wave_direction_deg": 45.0,
                "wind_speed_ms": 19.5, "wind_direction_deg": 45.0,
                "current_speed_ms": 1.8, "current_direction_deg": 40.0,
            },
        }

    def query_point(
        self,
        timestamp: datetime,
        latitude: float,
        longitude: float,
    ) -> MetoceanObservation:
        r = self.regimes.get(self.default_regime, self.regimes["moderate"])
        return MetoceanObservation(
            timestamp=timestamp.isoformat(),
            latitude=latitude,
            longitude=longitude,
            wave_height_m=r["wave_height_m"],
            wave_period_s=r["wave_period_s"],
            wave_direction_deg=r["wave_direction_deg"],
            wind_speed_ms=r["wind_speed_ms"],
            wind_direction_deg=r["wind_direction_deg"],
            current_speed_ms=r["current_speed_ms"],
            current_direction_deg=r["current_direction_deg"],
            source_product="SYNTHETIC_CALIBRATED_BENCHMARK",
            spatial_resolution_deg=0.25,  # Comparable to ERA5 0.25x0.25 deg grid
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_product": "SYNTHETIC_CALIBRATED_BENCHMARK",
            "provider": "SIH26138 Platform Benchmark",
            "native_grid_resolution_deg": 0.25,
            "temporal_resolution_hours": 1.0,
            "is_authoritative_reanalysis": False,
            "validation_note": "For algorithmic pipeline testing; replace with verified ERA5 for real-world validation.",
        }
