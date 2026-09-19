# Quickstart Guide: Egreen Quanta (v1.0.0)

Get started with fuel consumption prediction and green fleet optimization in under five minutes.

---

## 1. Single-Line Python Prediction

Egreen Quanta exposes a clean, high-throughput prediction API through `src.qi_prediction.serving`:

```python
from src.qi_prediction.serving import predict_fuel

# Operational vessel state query
query = {
    "stw_kn": 14.5,            # Speed Through Water (knots)
    "sog_kn": 14.2,            # Speed Over Ground (knots)
    "draft_m": 8.5,            # Mean draft (meters)
    "displacement_t": 25000.0, # Total displaced ship mass (tonnes)
    "wind_speed_ms": 7.5,      # True wind speed (m/s)
    "wave_height_m": 1.5,      # Significant wave height (meters)
    "vessel_type": "ContainerShip",
    "fuel_type": "VLSFO",
}

# Predict instantaneous fuel mass flow rate (kg/h)
predicted_fuel_kg_h = predict_fuel(query)
print(f"Predicted Fuel Consumption: {predicted_fuel_kg_h:.2f} kg/h")
```

---

## 2. Prediction with Conformal Uncertainty & OOD Guard

For safety-critical maritime operations, invoke the diagnostic interface to obtain predictive confidence bounds and operating domain status:

```python
from src.qi_prediction.serving import predict_fuel_with_uncertainty

result = predict_fuel_with_uncertainty(query, coverage=0.90)

print("Fuel Prediction:", result["fuel_prediction"], "kg/h")
print("Serving Model:", result["model"], f"({result['routing_status']})")
print("In-Domain Status:", result["in_domain"], f"(Distance: {result['envelope_distance']:.3f})")
print(f"90% Conformal Range: [{result['uncertainty']['lower_bound_kg_h']:.1f}, {result['uncertainty']['upper_bound_kg_h']:.1f}] kg/h")
print("Warning Message:", result["warning"])
```

---

## 3. Running the Live Demo Scenarios

To see the system handle normal cruise, high-demand surges, alternative green fuels, severe out-of-distribution events, and model failure recovery:

```bash
python scripts/demo_scenarios.py
```

---

## 4. Running the Complete Test Suite

Verify all unit, integration, and regression tests:
```bash
pytest tests/
```
