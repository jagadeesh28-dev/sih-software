# Clean-Environment Reproducibility Guide

> **OOD figures updated (FRESHLY COMPUTED):** the OOD guard was revalidated. Earlier figures in this document (e.g. 96.55% severe recall) are HISTORICAL and did not describe deployed behaviour. Current: 0.0% in-domain FPR; severe 100.0%, moderate 100.0% recall at d_env 1.50. See docs/ood_validation.md.

**Project**: SIH26138 — Egreen Quanta  
**Release**: 1.0.0-verified  
**Target Environment**: Python 3.10 to 3.14 on Linux / Windows / macOS  

---

## 1. Quickstart: One-Command Master Reproduction
To verify the entire project from a clean checkout, execute:

```bash
python reproduce_release.py
```

This single deterministic command executes all 10 release gates in $<5$ seconds:
1. Validates dataset integrity (173,974 records across 3 parquets; verifies exact SHA256 hashes).
2. Verifies production model boosters and metadata (`qi_c1.txt`, `model_real_04.txt`).
3. Re-evaluates baseline predictive metrics ($\text{MAE} = 246.91\text{ kg/h}$, $R^2 = 0.9503$).
4. Re-evaluates candidate QI-C1 predictive metrics ($\text{MAE} = 244.86\text{ kg/h}$, $R^2 = 0.9500$).
5. Verifies conformal uncertainty coverage ($93.56\%$ test coverage, $31.17\%$ sharpness gain).
6. Verifies OOD Guard performance ($0.0\%$ in-domain FPR, $96.55\%$ severe OOD recall).
7. Verifies 1,000 invalid input stress tests ($100.0\%$ safe rejection rate) + 16 edge cases.
8. Verifies Phase 5 frozen fleet optimization benchmarks (825,000 evaluations).
9. Executes end-to-end multi-fuel and slow-steaming scenario traces.
10. Validates scientific claim consistency against `docs/claim_ledger.md`.

---

## 2. Environment Setup from Scratch

```bash
# 1. Clone repository
git clone https://github.com/sih2026/egreen-quanta.git
cd egreen-quanta

# 2. Create clean Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install pinned dependencies
pip install -r requirements-lock.txt
```

### Key Pinned Dependencies
- `python >= 3.10`
- `numpy >= 1.24.0, < 2.3.0`
- `pandas >= 2.0.0`
- `scipy >= 1.10.0`
- `lightgbm >= 4.0.0`
- `scikit-learn >= 1.3.0`
- `pyarrow >= 14.0.0`
- `pyyaml >= 6.0`

---

## 3. Step-by-Step Individual Audits

### Rebuilding Production Artifacts
To retrain and serialize all production models, domain bounds, and conformal quantiles strictly from raw telemetry:
```bash
python scripts/build_production_models.py
```

### Running Comprehensive Scientific Audits
To re-evaluate all 34,796 test records, run 1,000 stress tests, and calculate multi-regime metrics:
```bash
python scripts/compute_detailed_metrics.py
```

### Running the Official Release Gate Audit
To verify all 10 release gates (G1 through G10) and export `release/release_gate.json`:
```bash
python scripts/release_gate.py
```

### Running the Live SIH Demonstration Script
To execute all 7 live presentation scenes:
```bash
python scripts/demo_scenarios.py
```

---

## 4. Immutable Artifact Hashes (SHA256)

| Artifact File | Expected SHA256 Hash (First 32 chars) | Status |
|:--------------|:--------------------------------------|:-------|
| `data/processed/real/fuelcast/CPS_Poseidon.parquet` | `da85f2e21b6e8724c8350f9aadbda4e4...` | Verified |
| `data/processed/real/fuelcast/CPS_Triton.parquet` | `fa8cc7f9f6a92d330088e41e3f275b8d...` | Verified |
| `data/processed/real/fuelcast/OSS_Ceto.parquet` | `ac3f8d5e865f11cd40f147d6153de991...` | Verified |
| `models/model_real_04.txt` | `e9f80a3bb69c0d9c490a612507851239...` | Verified |
| `models/qi_c1.txt` | `b3ca3dc196a60db620021df677dca08f...` | Verified |
| `models/conformal_quantiles.json` | `5c84d72dcf35198ff6c4a6fbc610dc25...` | Verified |
| `models/domain_checker.json` | `2d4ff90e5f2cfbbd8e20253f5ff26391...` | Verified |
