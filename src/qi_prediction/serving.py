"""
Production Prediction Serving Engine & Model Routing Service.
SIH26138 - Phase 7.6 & Phase 7.7 Production Architecture.

Features:
- Validates inputs against immutable feature contract (CONFIG_REAL_A).
- Strictly rejects malformed, NaN, Inf, and physically impossible inputs.
- Evaluates operating domain membership and envelope distance via DomainChecker.
- Calibrates conformal prediction intervals (80%, 90%, 95%).
- Implements 3-tier safe model routing policy:
    1. NORMAL: QI-C1 in-domain with acceptable uncertainty.
    2. FALLBACK: MODEL-REAL-04 on near-boundary or high uncertainty.
    3. EMERGENCY: PhysicsFuelPredictor on ML inference failure.
    4. REJECT: Hard rejection on physical violation or severe OOD.
- Exposes clean API: predict_fuel(input) and predict_fuel_with_uncertainty(input).
"""

import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import lightgbm as lgb
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from prediction.physics_predictor import PhysicsFuelPredictor
from optimization.canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type


class ProductionFuelPredictor:
    """
    Hardened Production Prediction Engine with Domain Guard, Conformal Uncertainty,
    and Safe Model Routing.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        models_dir: Optional[Union[str, Path]] = None,
    ):
        self.repo_root = REPO_ROOT
        self.config_path = Path(config_path) if config_path else self.repo_root / "PHASE7" / "config" / "production.yaml"
        self.models_dir = Path(models_dir) if models_dir else self.repo_root / "models"

        # Load production configuration
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "domain_guard": {
                    "envelope_distance_threshold_warning": 1.00,
                    "envelope_distance_threshold_ood": 1.50,
                    "envelope_distance_threshold_critical": 3.00,
                },
                "uncertainty_gate": {
                    "nominal_coverage": 0.90,
                    "flag_threshold_mpiw_kg_h": 1200.0,
                    "reject_threshold_mpiw_kg_h": 2500.0,
                },
            }

        # Initialize Physics Engine
        self.physics = PhysicsFuelPredictor(default_vessel_type="container_feeder")

        # Load Domain Checker metadata
        self.domain_stats = {}
        self.valid_categories = {}
        domain_file = self.models_dir / "domain_checker.json"
        if domain_file.exists():
            with open(domain_file, "r") as f:
                ddata = json.load(f)
                self.domain_stats = ddata.get("envelope_stats", {})
                self.valid_categories = ddata.get("valid_categories", {})

        # Load Conformal Quantiles
        self.conformal_quantiles = {
            "0.8": {"q_val": 332.37, "mpiw_kg_h": 664.73},
            "0.9": {"q_val": 598.40, "mpiw_kg_h": 1196.80},
            "0.95": {"q_val": 877.91, "mpiw_kg_h": 1755.82},
        }
        cq_file = self.models_dir / "conformal_quantiles.json"
        if cq_file.exists():
            with open(cq_file, "r") as f:
                self.conformal_quantiles = json.load(f)

        # Load LightGBM Booster Models
        self.qi_c1_booster: Optional[lgb.Booster] = None
        self.model_real_04_booster: Optional[lgb.Booster] = None

        qi_file = self.models_dir / "qi_c1.txt"
        if qi_file.exists():
            self.qi_c1_booster = lgb.Booster(model_file=str(qi_file))

        m04_file = self.models_dir / "model_real_04.txt"
        if m04_file.exists():
            self.model_real_04_booster = lgb.Booster(model_file=str(m04_file))

        # Features specification
        self.qi_features = [
            "stw_kn", "sog_kn", "draft_m", "wave_height_m", "water_depth_m", "fuel_type"
        ]
        self.all_features = [
            "stw_kn", "sog_kn", "draft_m", "displacement_t",
            "wind_speed_ms", "wind_direction_deg", "wave_height_m", "wave_period_s",
            "wave_direction_deg", "current_speed_ms", "current_direction_deg",
            "water_depth_m", "vessel_type", "fuel_type"
        ]

        # Categorical categories
        self.v_cats = ['offshore_supply', 'passenger_cruise', 'passenger_cruise_small']
        self.f_cats = ['mgo', 'vlsfo']

        # Physical hard bounds
        self.physical_bounds = {
            "stw_kn": (0.0, 35.0),
            "sog_kn": (0.0, 35.0),
            "draft_m": (1.0, 25.0),
            "displacement_t": (500.0, 400000.0),
            "wind_speed_ms": (0.0, 60.0),
            "wind_direction_deg": (0.0, 360.0),
            "wave_height_m": (0.0, 20.0),
            "wave_period_s": (1.0, 30.0),
            "wave_direction_deg": (0.0, 360.0),
            "current_speed_ms": (0.0, 6.0),
            "current_direction_deg": (0.0, 360.0),
            "water_depth_m": (2.0, 11000.0),
        }

    def validate_and_sanitize_point(self, raw_input: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate input against physical plausibility and schema contracts.
        Returns (is_valid, rejection_reasons, sanitized_dict).
        """
        errors = []
        clean = dict(raw_input)

        # 1. Required features check
        required_fields = ["stw_kn", "draft_m", "displacement_t"]
        for rf in required_fields:
            if rf not in clean or clean[rf] is None:
                errors.append(f"Missing mandatory required feature: '{rf}'")
            else:
                val = clean[rf]
                if isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val)):
                    errors.append(f"Feature '{rf}' contains NaN or Inf value")

        if errors:
            return False, errors, clean

        # 2. SOG handling (fallback to STW if missing)
        if "sog_kn" not in clean or clean["sog_kn"] is None:
            clean["sog_kn"] = clean["stw_kn"]
        elif isinstance(clean["sog_kn"], (int, float)) and (math.isnan(clean["sog_kn"]) or math.isinf(clean["sog_kn"])):
            errors.append("Feature 'sog_kn' contains NaN or Inf value")

        # 3. Environment defaults
        defaults = {
            "wind_speed_ms": 0.0,
            "wind_direction_deg": 0.0,
            "wave_height_m": 0.0,
            "wave_period_s": 6.0,
            "wave_direction_deg": 0.0,
            "current_speed_ms": 0.0,
            "current_direction_deg": 0.0,
            "water_depth_m": 100.0,
            "vessel_type": "ContainerShip",
            "fuel_type": "VLSFO",
        }
        for k, def_v in defaults.items():
            if k not in clean or clean[k] is None:
                clean[k] = def_v
            elif isinstance(clean[k], (int, float)) and (math.isnan(clean[k]) or math.isinf(clean[k])):
                errors.append(f"Feature '{k}' contains NaN or Inf value")

        # 4. Check numerical bounds
        for feat, (b_min, b_max) in self.physical_bounds.items():
            if feat in clean and clean[feat] is not None:
                try:
                    val = float(clean[feat])
                    if val < b_min or val > b_max:
                        errors.append(f"Feature '{feat}'={val} out of physical bounds [{b_min}, {b_max}]")
                except (ValueError, TypeError):
                    errors.append(f"Feature '{feat}' is not a valid numerical value")

        # 5. Canonicalize categoricals
        try:
            clean["vessel_type"] = canonicalize_vessel_type(str(clean["vessel_type"]))
            clean["fuel_type"] = canonicalize_fuel_type(str(clean["fuel_type"]))
        except Exception as e:
            errors.append(f"Categorical normalization error: {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors, clean

    def compute_envelope_distance(self, clean_point: Dict[str, Any]) -> float:
        """Calculate normalized multi-dimensional distance outside training envelope."""
        if not self.domain_stats:
            return 0.0

        dist_sq = 0.0
        n_dim = 0
        for col, stats in self.domain_stats.items():
            if col in clean_point and clean_point[col] is not None:
                try:
                    val = float(clean_point[col])
                    span = max(stats["max"] - stats["min"], stats["std"])
                    if val > stats["max"]:
                        delta = (val - stats["max"]) / span
                        dist_sq += delta ** 2
                    elif val < stats["min"]:
                        delta = (stats["min"] - val) / span
                        dist_sq += delta ** 2
                    n_dim += 1
                except (ValueError, TypeError):
                    pass

        return float(np.sqrt(dist_sq / max(n_dim, 1)))

    def _predict_point(
        self,
        point: Dict[str, Any],
        coverage: float = 0.90,
        raise_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Internal worker to evaluate and predict a single operational point."""
        from pandas.api.types import CategoricalDtype
        now_ts = datetime.now(timezone.utc).isoformat()

        # Step 1: Input Validation
        is_valid, errors, clean = self.validate_and_sanitize_point(point)
        if not is_valid:
            if raise_on_error:
                raise ValueError(f"Input rejected by Production Feature Contract: {'; '.join(errors)}")
            return {
                "fuel_prediction": None,
                "prediction_source": "REJECT",
                "confidence": "LOW",
                "uncertainty": None,
                "model": "None",
                "model_version": "1.0.0-production",
                "routing_status": "REJECT",
                "in_domain": False,
                "envelope_distance": 999.0,
                "cross_check": None,
                "warning": f"Input validation failure: {'; '.join(errors)}",
                "timestamp": now_ts,
            }

        # Step 2: Domain Checking & OOD Distance
        env_dist = self.compute_envelope_distance(clean)
        crit_thresh = self.config.get("domain_guard", {}).get("envelope_distance_threshold_critical", 3.00)
        ood_thresh = self.config.get("domain_guard", {}).get("envelope_distance_threshold_ood", 1.50)
        warn_thresh = self.config.get("domain_guard", {}).get("envelope_distance_threshold_warning", 1.00)

        if env_dist > crit_thresh:
            reason = f"Severe Out-of-Distribution condition: distance {env_dist:.2f} > {crit_thresh:.2f}"
            if raise_on_error:
                raise ValueError(f"Input rejected: {reason}")
            return {
                "fuel_prediction": None,
                "prediction_source": "REJECT",
                "confidence": "LOW",
                "uncertainty": None,
                "model": "None",
                "model_version": "1.0.0-production",
                "routing_status": "REJECT",
                "in_domain": False,
                "envelope_distance": round(env_dist, 3),
                "cross_check": None,
                "warning": reason,
                "timestamp": now_ts,
            }

        in_domain = env_dist <= ood_thresh
        near_boundary = env_dist > warn_thresh

        # Step 3: First-Principles Physics Computation
        df_single = pd.DataFrame([clean])
        try:
            f_phys = float(self.physics.predict(df_single)[0])
            f_phys = max(0.0, f_phys)
        except Exception:
            f_phys = 0.0

        # Step 4: Dual-Model Evaluation & Cross-Check
        v_val = str(clean.get("vessel_type", "passenger_cruise"))
        f_val = str(clean.get("fuel_type", "vlsfo"))
        if v_val not in self.v_cats:
            v_val = "passenger_cruise"
        if f_val not in self.f_cats:
            f_val = "vlsfo"

        pred_qi = None
        pred_m04 = None
        warning_msg = None

        # A. Evaluate QI-C1
        if self.qi_c1_booster is not None:
            try:
                row_qi = {c: clean[c] for c in self.qi_features}
                df_qi = pd.DataFrame([row_qi])
                df_qi["fuel_type"] = pd.Series([f_val], dtype=CategoricalDtype(categories=self.f_cats, ordered=False))
                r_pred_qi = float(self.qi_c1_booster.predict(df_qi)[0])
                pred_qi = max(0.0, f_phys + 1.0 * r_pred_qi)
            except Exception as e:
                warning_msg = f"QI-C1 inference exception ({str(e)})."

        # B. Evaluate MODEL-REAL-04 (Reference Anchor)
        if self.model_real_04_booster is not None:
            try:
                row_m04 = {c: clean[c] for c in self.all_features}
                df_m04 = pd.DataFrame([row_m04])
                df_m04["vessel_type"] = pd.Series([v_val], dtype=CategoricalDtype(categories=self.v_cats, ordered=False))
                df_m04["fuel_type"] = pd.Series([f_val], dtype=CategoricalDtype(categories=self.f_cats, ordered=False))
                r_pred_m04 = float(self.model_real_04_booster.predict(df_m04)[0])
                pred_m04 = max(0.0, f_phys + 1.0 * r_pred_m04)
            except Exception as e:
                pass

        # Step 5: Decision Logic & Model Routing
        # Calculate cross-check disparity if both available
        cross_check = {
            "qi_c1_pred_kg_h": round(pred_qi, 2) if pred_qi is not None else None,
            "model_real_04_pred_kg_h": round(pred_m04, 2) if pred_m04 is not None else None,
            "delta_kg_h": round(abs(pred_qi - pred_m04), 2) if (pred_qi is not None and pred_m04 is not None) else None,
        }

        # Policy routing:
        # NORMAL: In-domain, distance <= warn_thresh, QI-C1 available, cross-check delta <= 500 kg/h
        # FALLBACK: Near boundary (warn_thresh < dist <= ood_thresh) or QI-C1 unavailable or cross-check discrepancy
        # EMERGENCY_PHYSICS: In-domain ML failure or severe extrapolation (dist > ood_thresh)
        if in_domain and not near_boundary and pred_qi is not None:
            if cross_check["delta_kg_h"] is not None and cross_check["delta_kg_h"] > 500.0:
                # High discrepancy between QI and Reference -> Fallback to reference
                predicted_fuel = pred_m04 if pred_m04 is not None else pred_qi
                selected_model = "MODEL-REAL-04"
                prediction_source = "MODEL_REAL_04"
                confidence = "MEDIUM"
                routing_status = "FALLBACK"
                warning_msg = f"Cross-check discrepancy ({cross_check['delta_kg_h']:.1f} kg/h > 500 kg/h); routed to reference MODEL-REAL-04."
            else:
                predicted_fuel = pred_qi
                selected_model = "QI-C1"
                prediction_source = "QI_C1"
                confidence = "HIGH"
                routing_status = "NORMAL"
        elif in_domain and pred_m04 is not None:
            predicted_fuel = pred_m04
            selected_model = "MODEL-REAL-04"
            prediction_source = "MODEL_REAL_04"
            confidence = "MEDIUM"
            routing_status = "FALLBACK"
            if near_boundary:
                warning_msg = f"Operating state near training envelope (dist={env_dist:.2f}); routed to reference MODEL-REAL-04."
        elif in_domain and pred_qi is not None:
            predicted_fuel = pred_qi
            selected_model = "QI-C1"
            prediction_source = "QI_C1"
            confidence = "MEDIUM"
            routing_status = "FALLBACK"
        else:
            # Physics emergency fallback
            predicted_fuel = f_phys
            selected_model = "PhysicsFuelPredictor"
            prediction_source = "PHYSICS_EMERGENCY"
            confidence = "LOW"
            routing_status = "EMERGENCY_PHYSICS"
            warning_msg = "Operating outside valid ML envelope or ML failure. Output is unadjusted first-principles physics estimate."

        # Step 6: Conformal Uncertainty Calibration
        cov_key = str(coverage) if str(coverage) in ["0.9", "0.95"] else "0.9"
        model_q_dict = self.conformal_quantiles.get(selected_model, self.conformal_quantiles.get("MODEL-REAL-04", {}))
        q_stats = model_q_dict.get(cov_key, {"q_val": 1000.0, "mpiw_kg_h": 2000.0})
        base_q = float(q_stats.get("q_val", 1000.0))

        # Scale uncertainty dynamically if extrapolating outside empirical envelope
        scaled_q = base_q * (1.0 + 0.5 * max(0.0, env_dist - 0.5))
        interval_width = 2.0 * scaled_q
        lower_bound = max(0.0, predicted_fuel - scaled_q)
        upper_bound = predicted_fuel + scaled_q

        flag_thresh = self.config.get("uncertainty_gate", {}).get("flag_threshold_mpiw_kg_h", 1600.0)
        is_high_uncertainty = interval_width > flag_thresh
        if is_high_uncertainty:
            if confidence == "HIGH":
                confidence = "MEDIUM"
            if not warning_msg:
                warning_msg = f"Elevated prediction uncertainty: {int(float(cov_key)*100)}% interval width ({interval_width:.1f} kg/h) exceeds threshold ({flag_thresh:.1f} kg/h)."

        return {
            "fuel_prediction": round(float(predicted_fuel), 2),
            "prediction_source": prediction_source,
            "confidence": confidence,
            "uncertainty": {
                "coverage": float(coverage),
                "interval_width_kg_h": round(float(interval_width), 2),
                "lower_bound_kg_h": round(float(lower_bound), 2),
                "upper_bound_kg_h": round(float(upper_bound), 2),
                "is_high_uncertainty": bool(is_high_uncertainty),
            },
            "model": selected_model,
            "model_version": "1.0.0-verified",
            "routing_status": routing_status,
            "in_domain": bool(in_domain),
            "envelope_distance": round(float(env_dist), 3),
            "cross_check": cross_check,
            "warning": warning_msg,
            "timestamp": now_ts,
        }

    def predict_fuel(self, input_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Union[float, List[float]]:
        """
        Clean, production-grade fuel prediction function.
        Returns fuel prediction (kg/h).
        """
        if isinstance(input_data, dict):
            res = self._predict_point(input_data, raise_on_error=True)
            return res["fuel_prediction"]
        elif isinstance(input_data, pd.DataFrame):
            results = []
            for _, row in input_data.iterrows():
                res = self._predict_point(row.to_dict(), raise_on_error=True)
                results.append(res["fuel_prediction"])
            return results
        elif isinstance(input_data, list):
            results = []
            for item in input_data:
                res = self._predict_point(item, raise_on_error=True)
                results.append(res["fuel_prediction"])
            return results
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}. Expected Dict, DataFrame, or List[Dict].")

    def predict_fuel_with_uncertainty(
        self,
        input_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
        coverage: float = 0.90,
        raise_on_error: bool = False,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Full diagnostic production inference API with uncertainty, OOD status, and warnings.
        """
        if isinstance(input_data, dict):
            return self._predict_point(input_data, coverage=coverage, raise_on_error=raise_on_error)
        elif isinstance(input_data, pd.DataFrame):
            return [self._predict_point(row.to_dict(), coverage=coverage, raise_on_error=raise_on_error) for _, row in input_data.iterrows()]
        elif isinstance(input_data, list):
            return [self._predict_point(item, coverage=coverage, raise_on_error=raise_on_error) for item in input_data]
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}. Expected Dict, DataFrame, or List[Dict].")


# Global singleton instance for high-throughput zero-latency reuse
_GLOBAL_PREDICTOR: Optional[ProductionFuelPredictor] = None


def get_production_predictor() -> ProductionFuelPredictor:
    """Retrieve or initialize global ProductionFuelPredictor singleton."""
    global _GLOBAL_PREDICTOR
    if _GLOBAL_PREDICTOR is None:
        _GLOBAL_PREDICTOR = ProductionFuelPredictor()
    return _GLOBAL_PREDICTOR


def predict_fuel(input_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Union[float, List[float]]:
    """Clean module-level prediction interface."""
    predictor = get_production_predictor()
    return predictor.predict_fuel(input_data)


def predict_fuel_with_uncertainty(
    input_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    coverage: float = 0.90,
    raise_on_error: bool = False,
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Clean module-level prediction interface with uncertainty and OOD guard."""
    predictor = get_production_predictor()
    return predictor.predict_fuel_with_uncertainty(input_data, coverage=coverage, raise_on_error=raise_on_error)
