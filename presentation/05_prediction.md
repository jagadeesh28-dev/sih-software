# Slide 5: Predictive Modeling & Baseline Benchmark

## Multi-Model Test Benchmark (34,796 Held-Out Records)

| Model Architecture | Features Used | Seed 42 MAE (kg/h) | Seed 42 $R^2$ | 30-Seed Mean MAE (kg/h) | 30-Seed Mean $R^2$ | Verdict vs Classical Control |
|:-------------------|:--------------|:-------------------|:--------------|:------------------------|:-------------------|:-----------------------------|
| **Pure First-Principles Physics** | 14 hydrodynamic | $1,885.45$ | $-0.5471$ | N/A (Deterministic) | N/A | Deficient without telemetry tuning |
| **MODEL-REAL-04** (Reference Anchor) | 14 features | $246.91$ | $0.9503$ | $248.12 \pm 0.81$ | $0.9501 \pm 0.0003$ | Strong classical LightGBM baseline |
| **Classical GA Control** | 6 features | $237.24$ | $0.9532$ | $237.24 \pm 4.89$ | $0.9532$ | Strong classical evolutionary control |
| **QI-C1** (Quantum-Inspired Candidate)| **6 canonical** | **$244.86$** | **$0.9500$** | **$237.96 \pm 5.46$** | **$0.9530 \pm 0.0018$** | **Competitive ($p = 0.684$); +44.7% diversity** |

---

## The Canonical 6-Feature Subset (QIEA Selected)
1. `stw_kn`: Speed Through Water (primary hydrodynamic resistance driver).
2. `sog_kn`: Speed Over Ground (decoupled to preserve ocean current effects).
3. `draft_m`: Vessel Draft (wetted surface area and displacement indicator).
4. `wave_height_m`: Significant Wave Height (added wave resistance).
5. `water_depth_m`: Bathymetry (shallow water squatted resistance effect).
6. `fuel_type`: Categorical fuel grade (VLSFO / MGO energy density mapping).

---

## Scientific Rigor & Reconciled Claims
- **Statistical Parity**: Paired Wilcoxon signed-rank test yields $p = 0.684$ ($p > 0.05$). QI-C1 is **statistically competitive** with classical GA, not superior.
- **Dimensionality Reduction**: Achieves equivalent accuracy to full-feature models with **57% fewer sensor inputs**, drastically reducing sensor noise and acquisition costs.
