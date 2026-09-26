"""
Artifact integrity for the committed LightGBM text models.

LightGBM's text format stores byte offsets (tree_sizes=). A CRLF checkout
(core.autocrlf=true on Windows) shifts those offsets and loading fails with
"Model format error, expect a tree here". .gitattributes pins models/*.txt to LF.
"""

from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest
from pandas.api.types import CategoricalDtype

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"
MODEL_FILES = ["model_real_04.txt", "qi_c1.txt", "qi_c1_vessel_type.txt"]


@pytest.mark.parametrize("name", MODEL_FILES)
def test_model_file_has_lf_line_endings(name):
    assert b"\r\n" not in (MODELS_DIR / name).read_bytes()


def test_gitattributes_pins_models_to_lf():
    rules = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "models/*.txt text eol=lf" in rules


@pytest.mark.parametrize("name", MODEL_FILES)
def test_model_loads_and_predicts(name):
    booster = lgb.Booster(model_file=str(MODELS_DIR / name))
    assert booster.num_trees() == 150

    df = pd.read_parquet(REPO_ROOT / "data" / "processed" / "real" / "fuelcast" / "CPS_Triton.parquet")
    X = df[booster.feature_name()].tail(50).copy()
    if "vessel_type" in X:
        X["vessel_type"] = X["vessel_type"].astype(
            CategoricalDtype(["offshore_supply", "passenger_cruise", "passenger_cruise_small"])
        )
    if "fuel_type" in X:
        X["fuel_type"] = X["fuel_type"].astype(CategoricalDtype(["mgo", "vlsfo"]))
    residual = booster.predict(X)
    assert residual.shape == (50,)
    assert np.isfinite(residual).all()
