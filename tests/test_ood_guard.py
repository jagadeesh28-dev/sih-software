"""OOD guard properties (see docs/ood_validation.md section 0)."""

from src.qi_prediction.serving import get_production_predictor

P = get_production_predictor()
BASE = {"vessel_type": "passenger_cruise", "fuel_type": "vlsfo", "stw_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0}


def test_in_envelope_scores_zero():
    assert P.compute_envelope_distance(BASE) == 0.0


def test_adding_in_range_measurements_never_lowers_the_distance():
    extreme = {**BASE, "draft_m": 22.0}
    more = {**extreme, "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0, "wave_period_s": 6.0}
    assert P.compute_envelope_distance(more) == P.compute_envelope_distance(extreme) > 1.5


def test_imputed_defaults_do_not_dilute_serving_distance():
    storm = {**BASE, "stw_kn": 33.0, "sog_kn": 32.0, "draft_m": 22.0, "displacement_t": 160000.0,
             "wind_speed_ms": 48.0, "wave_height_m": 14.0, "water_depth_m": 15.0}
    res = P.predict_fuel_with_uncertainty(storm, raise_on_error=False)
    assert res["envelope_distance"] == round(P.compute_envelope_distance(storm), 3)
    assert res["routing_status"] == "REJECT" and res["fuel_prediction"] is None


def test_single_extreme_feature_is_out_of_domain():
    res = P.predict_fuel_with_uncertainty({**BASE, "draft_m": 22.0}, raise_on_error=False)
    assert res["in_domain"] is False and res["confidence"] == "LOW"
    assert "draft_m" in res["warning"]


def test_missing_vessel_type_is_invalid_input():
    res = P.predict_fuel_with_uncertainty({k: v for k, v in BASE.items() if k != "vessel_type"}, raise_on_error=False)
    assert res["routing_status"] == "REJECT" and "'vessel_type'" in res["warning"]
