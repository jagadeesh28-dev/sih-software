# SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization
**Release Version**: `1.0.0-verified`  
**Classification**: Controlled Decision-Support Prototype (SIH 2026 Ready)  
**Release Gate Verdict**: **`VERIFIED CONTROLLED RELEASE` (10/10 Gates Passed)**  
**Audit Date**: September 2026  

---

## 1. Executive Summary & One-Command Reproduction
**Egreen Quanta** is an uncertainty-aware, physics-guided, quantum-inspired maritime fuel prediction and fleet optimization decision-support prototype developed for the **Smart India Hackathon 2026 (Problem Statement SIH26138)**.

The platform provides ship operators and fleet managers with verifiable, auditable voyage speed recommendations, conformal uncertainty bounds, alternative-fuel scenario simulations, and automated out-of-distribution storm guards.

### Single-Command Master Reproduction
To deterministically reproduce and audit all 10 release gates from a clean environment in $<5$ seconds:

```bash
python reproduce_release.py
```

### Single-Command Interactive Demonstration
To execute the 7 official SIH live demonstration scenes:

```bash
python scripts/demo_scenarios.py
```

---

## 2. Reconciled Performance & Benchmark Summary

All numbers are deterministically reproducible on the held-out forward temporal test split ($34,796$ records across 3 commercial vessels):

| Model / Baseline | Selected Features | Seed 42 MAE ($\text{kg/h}$) | Seed 42 $R^2$ | 30-Seed Matched Mean MAE | 90% Conformal MPIW | 90% Empirical Coverage | Status |
|:-----------------|:-----------------:|:----------------------------|:--------------|:-------------------------|:-------------------|:-----------------------|:-------|
| **Pure Physics** | 14 | $1,885.45$ | $-0.5471$ | N/A | N/A | N/A | Deficient (Emergency fallback only) |
| **MODEL-REAL-04** (Reference) | 14 | $246.91$ | $0.9503$ | $248.12 \pm 0.81$ | $2,273.70\text{ kg/h}$ | $95.05\%$ | Verified Frozen Baseline Anchor |
| **Classical GA Control** | 6 | $237.24$ | $0.9532$ | $237.24 \pm 4.89$ | $1,598.20\text{ kg/h}$ | $93.40\%$ | Matched Evolutionary Control |
| **QI-C1** (Candidate) | **6** | **$244.86$** | **$0.9500$** | **$237.96 \pm 5.46$** | **$1,564.93\text{ kg/h}$** | **$93.56\%$** | **Competitive ($p=0.684$); +31.2% Sharper** |

---

## 3. Scientific Honesty & Release Gate Protocol

Egreen Quanta adheres to non-negotiable scientific integrity rules:
1. **No Quantum Hardware Claims**: All algorithms are classical quantum-inspired heuristics running on standard x86-64 hardware.
2. **Statistical Parity, Not Superiority**: QI-C1 is statistically competitive with classical genetic algorithms ($p=0.684$), not universally superior.
3. **Transparent Green Fuel Basis**: Alternative fuel figures (methanol, ammonia, liquid hydrogen) are physics-based scenario simulations using invariant delivered shaft work ($E = P_B \cdot t$). They are **not** measured telemetry.
4. **Decision Support, Not Autopilot**: The system is an advisory decision-support prototype. It is strictly prohibited from direct connection to autopilot, steering gear, or engine throttles.
5. **Exact Optimality Language**: The penalized objective optimum ($J^*_{\text{pen}} = 873.23\text{ t}$) is rigorously distinguished from the pure physical grid minimum ($3.24\text{ t}$).

---

## 4. Documentation Suite & Audit Navigation

Comprehensive documentation is organized across `docs/`, `release/`, and `reports/`:

### Core Documentation (`docs/`)
- [System Architecture](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/architecture.md): 7-layer defense-in-depth pipeline and serving logic.
- [Scientific Methodology](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/methodology.md): Hybrid residual modeling, QIEA, QPSO, and thermodynamic equations.
- [Data Card](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/data_card.md): 173,974 records, 12 removed rows, sensor provenance, and splitting protocol.
- [Model Card](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/model_card.md): Model details, metric reconciliation, feature contracts, and limitations.
- [Uncertainty Quantification](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/uncertainty.md): Conformal coverage vs sharpness, vessel and regime calibrations.
- [OOD Validation](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/ood_validation.md): Confusion matrices across modest, moderate, and severe OOD.
- [Safety Validation](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/safety_validation.md): 1,000 invalid stress tests, 16 edge cases, 10 failure injections.
- [Optimizer Validation](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/optimizer_validation.md): Phase 5 frozen benchmark (825,000 evals) and exact-optimality language.
- [Claim Ledger](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/claim_ledger.md): 20 cataloged claims with audit trail and verification status.
- [Limitations & Risk](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/limitations.md): Operational boundaries and negative results.
- [Reproducibility Guide](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/reproducibility.md): Pinned environment setup and immutable SHA256 hashes.
- [Final Master Results](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/docs/final_results.md): Unified tables across all experimental phases.

### Release Gate & Audits (`release/`)
- [Release Manifest JSON](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/release/release_manifest.json): Immutable hashes for data, models, and scripts.
- [Release Gate Audit JSON](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/release/release_gate.json): Official audit output for Gates G1 to G10.

### Master Reports (`reports/`)
- [Final Scientific Validation Report](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/reports/final_validation_report.md): 20-section complete technical and scientific audit.
- [Final SIH Executive Report](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/reports/final_sih_report.md): Hackathon summary and jury demonstration narrative.

---

## 5. Quickstart Installation

```bash
# 1. Clone repository
git clone https://github.com/sih2026/egreen-quanta.git
cd egreen-quanta

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install pinned dependencies
pip install -r requirements-lock.txt

# 4. Verify release
python reproduce_release.py
```
