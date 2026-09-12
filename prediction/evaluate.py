"""
Comprehensive Evaluation Metrics for Fuel Prediction and Uncertainty Estimation.
Section 14:
- Deterministic regression metrics: MAE, RMSE, MAPE, R2, Mean Error (bias), Median Absolute Error, Max Absolute Error.
- Quantile metrics: PICP, MPIW, coverage error, Pinball loss.
"""

from typing import Dict, List, Optional
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    median_absolute_error,
)


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, float]:
    """
    Compute full suite of deterministic regression evaluation metrics.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred)) if len(y_true) > 1 and np.ptp(y_true) > 1e-6 else 0.0

    # Mean error (signed bias): positive means model over-predicts, negative means under-predicts
    mean_error = float(np.mean(y_pred - y_true))

    med_ae = float(median_absolute_error(y_true, y_pred))
    max_ae = float(np.max(np.abs(y_pred - y_true)))

    # Safe MAPE
    non_zero = y_true > 1e-3
    if np.any(non_zero):
        mape = float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100.0)
    else:
        mape = 0.0

    return {
        "mae": mae,
        "rmse": rmse,
        "mape_pct": mape,
        "r2": r2,
        "mean_error": mean_error,
        "median_absolute_error": med_ae,
        "max_absolute_error": max_ae,
    }


def calculate_picp(y_true: np.ndarray, q_low: np.ndarray, q_high: np.ndarray) -> float:
    """
    Calculate Prediction Interval Coverage Probability (PICP) in percent [0, 100].
    """
    y_true = np.asarray(y_true, dtype=float)
    q_low = np.asarray(q_low, dtype=float)
    q_high = np.asarray(q_high, dtype=float)
    covered = (y_true >= q_low) & (y_true <= q_high)
    return float(np.mean(covered) * 100.0)


def compute_pinball_loss(
    y_true: np.ndarray,
    y_pred_q: np.ndarray,
    quantile: Optional[float] = None,
    tau: Optional[float] = None,
) -> float:
    """
    Compute pinball (tilted absolute) loss for a given quantile tau in (0, 1).
    Loss = max(tau * (y - q), (1 - tau) * (q - y))
    """
    q = tau if tau is not None else (quantile if quantile is not None else 0.5)
    diff = y_true - y_pred_q
    loss = np.maximum(q * diff, (q - 1.0) * diff)
    return float(np.mean(loss))


pinball_loss = compute_pinball_loss


def evaluate_quantiles(
    y_true: np.ndarray,
    q05: np.ndarray,
    q50: np.ndarray,
    q95: np.ndarray,
) -> Dict[str, float]:
    """
    Evaluate 90% prediction interval metrics (q05 to q95) and quantile loss.
    """
    y_true = np.asarray(y_true, dtype=float)
    q05 = np.asarray(q05, dtype=float)
    q50 = np.asarray(q50, dtype=float)
    q95 = np.asarray(q95, dtype=float)

    # 1. Prediction Interval Coverage Probability (PICP)
    in_interval = (y_true >= q05) & (y_true <= q95)
    picp = float(np.mean(in_interval))

    # 2. Mean Prediction Interval Width (MPIW)
    interval_widths = q95 - q05
    mpiw = float(np.mean(interval_widths))

    # 3. Normalized Mean Prediction Interval Width (NMPIW)
    y_range = float(np.ptp(y_true)) if np.ptp(y_true) > 0 else 1.0
    nmpiw = mpiw / y_range

    # 4. Coverage error relative to nominal 90% target
    coverage_error = picp - 0.90

    # 5. Pinball loss per quantile
    loss_q05 = compute_pinball_loss(y_true, q05, 0.05)
    loss_q50 = compute_pinball_loss(y_true, q50, 0.50)
    loss_q95 = compute_pinball_loss(y_true, q95, 0.95)
    mean_pinball = float(np.mean([loss_q05, loss_q50, loss_q95]))

    return {
        "picp_coverage": picp,
        "picp_pct": picp * 100.0,
        "target_coverage": 0.90,
        "coverage_error": coverage_error,
        "mpiw_interval_width": mpiw,
        "mpiw": mpiw,
        "nmpiw_normalized_width": nmpiw,
        "pinball_loss_q05": loss_q05,
        "pinball_loss_q50": loss_q50,
        "pinball_loss_q95": loss_q95,
        "mean_pinball_loss": mean_pinball,
    }
