"""
Safe Objective-Function Interface for Fleet Optimization.
Phase 2.2 Optimization Readiness Gate:
- Formal, defensive interface between fuel prediction models and future optimization algorithms.
- Evaluates domain membership, physical plausibility, and uncertainty width.
- Strictly prevents silent extrapolation outside the empirical training envelope.
- Applies explicit mathematical penalties or hard rejection for out-of-distribution / invalid states.
- Exposes risk-adjusted robust objectives: J(lambda) = q50 + lambda * (q95 - q05).
- Diagnoses model disagreement against first-principles physics reference.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from common.logger import get_logger
from .domain_checker import DomainChecker
from .ml_baseline import PureMLPredictor
from .physics_predictor import PhysicsFuelPredictor
from .quantile_model import QuantileUncertaintyPredictor

logger = get_logger(__name__)

# Disagreement thresholds between ML and Physics
DISAGREEMENT_MODERATE_KG_H = 150.0
DISAGREEMENT_HIGH_KG_H = 400.0

# Base penalty constant for invalid or out-of-domain states
BASE_OOD_PENALTY_KG_H = 10000.0


class SafeFuelObjective:
    """
    Optimization-ready, defensive wrapper around the frozen prediction engine.
    Guarantees that optimization algorithms cannot exploit ungrounded regions of the ML model.
    """

    def __init__(
        self,
        ml_predictor: PureMLPredictor,
        quantile_predictor: QuantileUncertaintyPredictor,
        physics_predictor: PhysicsFuelPredictor,
        domain_checker: DomainChecker,
        default_lambda_robust: float = 0.5,
        penalty_constant: float = BASE_OOD_PENALTY_KG_H,
    ):
        self.ml_predictor = ml_predictor
        self.quantile_predictor = quantile_predictor
        self.physics_predictor = physics_predictor
        self.domain_checker = domain_checker
        self.default_lambda_robust = default_lambda_robust
        self.penalty_constant = penalty_constant

    def evaluate_candidate(
        self,
        candidate: Dict[str, Any],
        lambda_robust: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single candidate operating state.
        Returns full diagnostics, uncertainty bounds, domain status, and penalized objective.
        """
        lam = lambda_robust if lambda_robust is not None else self.default_lambda_robust
        df_single = pd.DataFrame([candidate])

        # 1. Operating Domain & Physical Sanity Check
        domain_res = self.domain_checker.evaluate_point(candidate)
        d_status = domain_res["domain_status"]
        env_dist = domain_res["envelope_distance"]
        reasons = domain_res["reasons"]

        # 2. Model Predictions
        try:
            f_ml = float(self.ml_predictor.predict(df_single)[0])
        except Exception as e:
            f_ml = float("nan")
            reasons.append(f"ML prediction error: {str(e)}")

        try:
            q_res = self.quantile_predictor.predict_quantiles(df_single)
            q05 = float(q_res["q05"][0])
            q50 = float(q_res["q50"][0])
            q95 = float(q_res["q95"][0])
            unc_width = float(q_res["quantile_derived_dispersion_proxy"][0])
        except Exception as e:
            q05 = q50 = q95 = unc_width = float("nan")
            reasons.append(f"Quantile prediction error: {str(e)}")

        # 3. Physics Reference Prediction & Disagreement Check
        try:
            f_phys = float(self.physics_predictor.predict(df_single)[0])
            disagreement = abs(f_ml - f_phys) if not np.isnan(f_ml) else float("nan")
        except Exception as e:
            f_phys = float("nan")
            disagreement = float("nan")
            reasons.append(f"Physics reference error: {str(e)}")

        # Disagreement Classification
        if np.isnan(disagreement):
            disagreement_status = "UNKNOWN"
        elif disagreement >= DISAGREEMENT_HIGH_KG_H:
            disagreement_status = "HIGH_DISAGREEMENT"
        elif disagreement >= DISAGREEMENT_MODERATE_KG_H:
            disagreement_status = "MODERATE_DISAGREEMENT"
        else:
            disagreement_status = "LOW_DISAGREEMENT"

        # 4. Final Risk & Penalty Determination
        if d_status == "PHYSICALLY_INVALID":
            confidence_risk_flag = "REJECTED"
            final_domain_status = "PHYSICALLY_INVALID"
            # Massive static penalty to ensure optimizer immediately repels
            penalized_objective = self.penalty_constant * 10.0
            robust_objective = penalized_objective

        elif d_status == "OUT_OF_DOMAIN":
            confidence_risk_flag = "REJECTED"
            final_domain_status = "OUT_OF_DOMAIN"
            # Distance-proportional penalty prevents exploitation of ungrounded low-fuel troughs
            base_val = max(f_ml, 500.0) if not np.isnan(f_ml) else 500.0
            penalized_objective = base_val + self.penalty_constant * (1.0 + env_dist)
            robust_objective = penalized_objective

        elif d_status == "NEAR_BOUNDARY":
            confidence_risk_flag = "CAUTION"
            final_domain_status = "NEAR_BOUNDARY"
            robust_objective = q50 + lam * unc_width
            # Soft penalty for boundary operation to gently favor interior points
            penalized_objective = robust_objective + 25.0 * env_dist

        else:  # IN_DOMAIN
            final_domain_status = "VALID"
            # Check for excessive uncertainty even within empirical bounds
            if unc_width > 200.0:
                confidence_risk_flag = "CAUTION"
                final_domain_status = "UNCERTAIN"
            else:
                confidence_risk_flag = "SAFE"
            
            robust_objective = q50 + lam * unc_width
            penalized_objective = robust_objective

        return {
            "predicted_fuel": f_ml,
            "lower_prediction_bound": q05,
            "median_prediction": q50,
            "upper_prediction_bound": q95,
            "uncertainty_width": unc_width,
            "robust_fuel_objective": robust_objective,
            "penalized_fuel_objective": penalized_objective,
            "physics_reference_fuel": f_phys,
            "physics_ml_disagreement": disagreement,
            "disagreement_status": disagreement_status,
            "domain_status": final_domain_status,
            "envelope_distance": env_dist,
            "confidence_risk_flag": confidence_risk_flag,
            "is_valid_candidate": (confidence_risk_flag != "REJECTED"),
            "validity_reason": "; ".join(reasons) if reasons else "Nominal in-domain state",
        }

    def evaluate_batch(
        self,
        df: pd.DataFrame,
        lambda_robust: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Vectorized/batched evaluation of candidates.
        """
        results = []
        for _, row in df.iterrows():
            res = self.evaluate_candidate(row.to_dict(), lambda_robust=lambda_robust)
            results.append(res)
        return pd.DataFrame(results, index=df.index)
