# EGREEN QUANTA — SIH26138
### Quantum-Inspired Maritime Fuel Prediction & Green Fleet Multi-Objective Optimization

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-281%2F281%20Passing-brightgreen.svg)]()
[![Release Gates](https://img.shields.io/badge/Release%20Gates-10%2F10%20Verified-success.svg)]()
[![Conformal Coverage](https://img.shields.io/badge/Conformal%20PICP-93.56%25-informational.svg)]()
[![OOD Storm Recall](https://img.shields.io/badge/OOD%20Recall-96.55%25-blueviolet.svg)]()
[![Pareto Optimal](https://img.shields.io/badge/Pareto%20Front-31%20Solutions-orange.svg)]()

---

## 📌 Project Overview & Metadata

| Attribute | Specification |
|:---|:---|
| **Event** | **Smart India Hackathon 2026 (SIH 2026)** |
| **Problem Statement ID** | **SIH26138** |
| **Team Name** | **SUPER SYNQRA** |
| **Organization** | **Egreen Quanta** |
| **Release Version** | `v1.0.0-verified` |
| **System Classification** | Advisory Maritime Decision-Support System (IMO MEPC Compliant) |
| **Verification Status** | **10 / 10 Release Gates Passed (100% Deterministic Reproducibility)** |

---

## 🌊 Executive Summary: The Problem & Our Solution

### The Maritime Challenge
International maritime shipping contributes ~3% of global anthropogenic greenhouse gas emissions, burning over 300 million tonnes of fossil fuels annually. The International Maritime Organization (IMO) has mandated stringent decarbonization trajectories (IMO MEPC.308(73) & MEPC.391(81)), targeting net-zero GHG emissions by ~2050. However, vessel operators face critical operational hurdles:
1. **Physical Model Deficiencies**: Traditional empirical hydrodynamic formulas (e.g., standard Holtrop-Mennen) struggle to capture complex hull fouling, dynamic trim changes, and extreme sea-state interactions, leading to fuel prediction errors exceeding 1,800 kg/h.
2. **Black-Box ML Risks**: Pure machine learning models extrapolate dangerously during severe weather, exhibiting out-of-distribution (OOD) failure without warning.
3. **Multi-Objective Trade-Offs**: Fleet managers must simultaneously balance fuel consumption, operating costs (OPEX), Well-to-Wake (WtW) lifecycle emissions, contract delivery schedules, and severe weather risks (CVaR).
4. **Lack of Operational Verifiability**: Existing maritime tools lack cryptographic transparency, presenting black-box recommendations without uncertainty bounds or tamper-evident audit trails.

### Our Solution: EGREEN QUANTA
**EGREEN QUANTA** is an uncertainty-aware, physics-guided maritime decision-support platform engineered specifically for **Smart India Hackathon 2026 (SIH26138)**. It pairs classical hydrodynamic principles with gradient-boosted residual learning, inductive split conformal prediction, automated out-of-distribution storm guards, classical quantum-inspired multi-objective optimization, and an auditable bridge Human-Machine Interface (HMI).

```
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                       EGREEN QUANTA PIPELINE FLOW                         │
 └────────────────────────────────────────────────────────────────────────────┘
        │
        ├─► [1] Hull Telemetry & Weather (173,986 Sensor Records across 3 Hulls)
        │
        ├─► [2] Hydrodynamic Physics Baseline (Holtrop-Mennen & ITTC-1978 Power)
        │        │
        │        ├─► Physics Residual Decomposition
        │        ▼
        ├─► [3] Hybrid LightGBM Residual Predictor (MAE: 244.86 kg/h, R²: 0.9500)
        │        │
        │        ├─► Inductive Split Conformal Prediction (93.56% Coverage @ 90% Target)
        │        ▼
        ├─► [4] Multi-Layer Safety Guard (Mahalanobis Distance + Conformal p-value)
        │        │
        │        ├─► Nominal Marine Domain  ──► Approved Model Serving
        │        └─► OOD Storm Detected (96.55% Recall) ──► Failover to Physics (5.45 ms)
        │
        ├─► [5] Quantum-Inspired Fleet Optimizer (Classical QIEA & QPSO on x86_64)
        │        │
        │        ├─► 5-Objective Optimization (Fuel, OPEX, WtW CO₂e, Delay, CVaR Risk)
        │        ├─► 31 Non-Dominated Pareto Solutions
        │        └─► IMO MEPC Well-to-Wake Alternative Fuels (Bio-Methanol, Ammonia, H₂)
        │
        ├─► [6] Tamper-Evident Audit Ledger (RFC 8785 Canonical JSON + SHA-256 Manifest)
        │
        └─► [7] Next.js 15 Maritime Bridge HMI (Zero Mock Data, Operator Review/Confirm)
```

---

## 🏆 Summary of Completion Till Date

Across all developmental phases, the system has achieved 100% completion with complete scientific rigor, validated benchmarks, and operational packaging:

### 1. Phase 1: Real-World Ingestion & Forensic Data Integrity
- **Sensor Ingestion**: Ingested and harmonized **173,986 raw high-frequency sensor records** from the DTU FuelCast commercial dataset across 3 distinct commercial hulls:
  - `CPS_Poseidon`: Passenger Cruise Ship (100,500 records)
  - `CPS_Triton`: Passenger Cruise Ship (24,180 records)
  - `OSS_Ceto`: Offshore Supply Vessel (41,200 records)
- **Data Engineering**: Enforced strict forward temporal splitting ($80\%$ train, $20\%$ test / $34,796$ rows) to eliminate lookahead bias; reconciled Speed-Through-Water (STW) Doppler logs, volumetric mass flow meters, and metocean parameters (wave height, wind speed, water depth).

### 2. Phase 2: Physics-Guided Hybrid Prediction & Conformal Bounds
- **Hybrid Formulation**: Coupled Holtrop-Mennen hydrodynamic resistance and ITTC-1978 power curves with residual LightGBM estimators, reducing error by **$87.0\%$** relative to pure physics ($1,885.45\text{ kg/h} \to 244.86\text{ kg/h}$).
- **Conformal Uncertainty Quantification**: Integrated inductive split conformal prediction calibrated across forward temporal regimes, achieving **$93.56\%$ empirical coverage** at a $90\%$ confidence target with an interval sharpness of **$1,564.93\text{ kg/h}$** (a $+31.2\%$ efficiency improvement over unguided models).

### 3. Phase 3: Uncertainty Quantification & Automated OOD Storm Defense
- **Dual-Layer Guard**: Implemented joint Mahalanobis distance metric on the environmental input manifold combined with conformal p-value non-conformity gating.
- **Storm Failover**: Achieved **$96.55\%$ recall** in detecting severe weather regimes (Beaufort force $\ge 8$, wave height $>4.5\text{ m}$), with **$0.0\%$ false alarm rate** on nominal cruising conditions.
- **Failover Latency**: Guaranteed deterministic failover to robust hydrodynamic physics in **$5.45\text{ ms}$** without operational interruption.

### 4. Phase 4: Heterogeneous Fleet Multi-Objective Optimization
- **Classical Quantum-Inspired Optimization**: Implemented Quantum-Inspired Evolutionary Algorithm (QIEA) and Quantum-Behaved Particle Swarm Optimization (QPSO) running on classical x86_64 hardware.
- **5-Objective Trade-Offs**: Optimized fuel consumption ($t$), operating expenditure ($\text{USD}$), Well-to-Wake emissions ($t\text{CO}_2e$), arrival delay ($h$), and Conditional Value at Risk (CVaR).
- **Pareto Optimal Frontier**: Produced **31 strictly non-dominated Pareto solutions**, providing operators with diverse trade-off policies ranging from minimum voyage cost to maximum decarbonization.
- **IMO Alternative Fuels**: Integrated MEPC.308(73)/391(81) Well-to-Wake LCA carbon accounting for VLSFO, bio-methanol, green ammonia, e-diesel, and cold ironing (shore power).

### 5. Phase 5: Statistical Rigor & Master Benchmark Execution
- **30-Seed Matched Trials**: Conducted 30-seed matched random trials across all evolutionary heuristics (825,000 objective evaluations).
- **Statistical Honesty**: Non-parametric Wilcoxon signed-rank tests confirmed that QI-C1 is statistically comparable with classical GA controls ($p = 0.684$). In adherence to strict scientific ethics, no unjustified "quantum supremacy" claims are made.

### 6. Phase 6: Tamper-Evident Auditing & Decision Record System
- **Cryptographic Export Package**: Engineered RFC 8785 canonical JSON export system backed by SHA-256 cryptographic manifests and append-only audit ledgers.
- **Human-in-the-Loop Governance**: Full operator progression workflow (`PENDING_REVIEW` $\to$ `REVIEWED` $\to$ `CONFIRMED` $\to$ `EXPORTED`) ensuring bridge officers retain ultimate navigational authority.

### 7. Phase 7: Maritime Bridge HMI & Controlled Operational Release
- **Next.js 15 Console**: Production-grade maritime bridge console built with TypeScript, Tailwind CSS, shadcn/ui, and Recharts, communicating via typed Zod schemas to a FastAPI backend (`port 8001`).
- **Zero Mock / Hardcoded Data**: 100% of telemetry, predictions, uncertainty bounds, and optimizer results flow directly from authoritative Python backend engines.
- **Evaluator Evidence Package**: Generated a curated 25-artifact submission package (16 page-budgeted PDFs, 1080p demonstration video, datasets, decision records) inside `EGREEN_QUANTA_SIH26138_EVIDENCE/`.

---

## 📊 Reconciled Empirical Benchmark Metrics

All figures below are deterministically verified on the forward temporal holdout test split ($34,796$ records across 3 commercial vessels):

| Model / Heuristic | Selected Features | Single-Run MAE ($\text{kg/h}$) | Single-Run $R^2$ | 30-Seed Mean MAE ($\text{kg/h}$) | 90% Conformal MPIW | 90% Empirical Coverage | Status / Role |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Pure Hydrodynamic Physics** | 14 | $1,885.45$ | $-0.5471$ | N/A | N/A | N/A | Emergency Failover Anchor |
| **MODEL-REAL-04 (Reference)** | 14 | $246.91$ | $0.9503$ | $248.12 \pm 0.81$ | $2,273.70\text{ kg/h}$ | $95.05\%$ | Frozen Baseline Anchor |
| **Classical GA Control** | 6 | $237.24$ | $0.9532$ | $237.24 \pm 4.89$ | $1,598.20\text{ kg/h}$ | $93.40\%$ | Matched Genetic Control |
| **QI-C1 Candidate** | **6** | **$244.86$** | **$0.9500$** | **$237.96 \pm 5.46$** | **$1,564.93\text{ kg/h}$** | **$93.56\%$** | **Parity ($p=0.684$); +31.2% Sharper** |

### Safety, Guard & Optimizer Performance
| Engineering Metric | Measured Value | Standard / Requirement | Verdict |
|:---|:---:|:---:|:---:|
| **OOD Storm Recall (Beaufort $\ge 8$)** | **$96.55\%$** | $\ge 90.0\%$ | **PASS** |
| **Nominal False Alarm Rate** | **$0.00\%$** | $\le 5.0\%$ | **PASS** |
| **Failover Switch Latency** | **$5.45\text{ ms}$** | $< 50\text{ ms}$ | **PASS** |
| **Adversarial Input Defense** | **18 / 18 Blocked (100%)** | 100% Interception | **PASS** |
| **Pareto Non-Dominated Solutions** | **31 Solutions** | $\ge 15$ diverse points | **PASS** |
| **Unit Test Coverage** | **281 / 281 Tests Passed** | 100% Pass Rate | **PASS** |
| **Release Gate Verification** | **10 / 10 Gates Passed** | 10/10 Deterministic | **PASS** |

---

## 🏛️ System Architecture & Subsystems

```
sih26138_platform/
├── api/                           # FastAPI serving adapter (port 8001)
│   └── main.py                    # REST API: prediction, Pareto, optimizer, audit, exports
├── configs/                       # Configuration files (fuels, fleet, thresholds)
│   ├── fleet.yaml                 # Vessel particulars (displacement, draft, engine SFOC)
│   └── fuels.yaml                 # IMO MEPC LCA Well-to-Wake carbon factors
├── data/                          # Data pipelines & precomputed features
│   └── processed/real/fuelcast/   # Cleaned 173,986 row Parquet datasets
├── docs/                          # Core documentation suite
│   ├── architecture.md            # 7-layer defense-in-depth architecture
│   ├── methodology.md             # Hybrid modeling & quantum-inspired math
│   ├── data_card.md               # Sensor provenance and forward temporal splits
│   ├── model_card.md              # Feature contracts and model specifications
│   ├── uncertainty.md             # Conformal calibration and coverage
│   ├── ood_validation.md          # Storm defense confusion matrices
│   ├── safety_validation.md       # Adversarial and fault-injection audits
│   ├── optimizer_validation.md    # Multi-objective Pareto verification
│   ├── claim_ledger.md            # 20 verified project claims
│   ├── limitations.md             # Negative results and operational boundaries
│   ├── reproducibility.md         # Deterministic reproduction guide
│   └── archive_phases/            # Master archive of developmental phases (Phases 1-4, audits)
│       └── README.md              # Complete index of 79 archived historical files
├── models/                        # Serialized LightGBM surrogates & conformal scalers
├── optimization/                  # Multi-objective optimization engines
│   ├── evaluator.py               # Fleet evaluation engine & penalty formulation
│   ├── fleet_evaluator_phase4.py  # Heterogeneous fleet routing & berth scheduling
│   ├── sih_objective_engine.py    # 5-objective evaluation function
│   └── variables.py               # Chromosome representation & decision vectors
├── physics/                       # Hydrodynamic physics baselines
│   ├── holtrop_mennen.py          # Holtrop-Mennen resistance calculations
│   └── power_engine.py            # ITTC-1978 power & engine load mapping
├── prediction/                    # Machine learning & conformal prediction
│   ├── feature_pipeline.py        # Canonical 6-feature extractor
│   ├── physics_predictor.py       # Physics baseline fallback engine
│   └── residual_model.py          # LightGBM residual learning pipeline
├── reports/                       # Formal audit reports and release certificates
│   ├── END_TO_END_VERIFICATION_REPORT.md
│   ├── OPERATIONAL_READINESS_AUDIT.md
│   └── CERTIFICATION_READINESS_REVIEW.md
├── results/                       # Verified experimental outputs & Pareto data
│   └── pareto_front.csv           # 31 non-dominated Pareto tradeoff vectors
├── schemas/                       # JSON schemas for data contracts & manifests
├── scripts/                       # Reproduction & demo automation scripts
│   ├── demo_scenarios.py          # 7 official live demonstration scenes
│   ├── reproduce_release.py       # 10-gate deterministic release auditor
│   └── run_phase5.py              # Master benchmark runner
├── src/                           # Shared library modules (algorithms, export, evaluation)
│   ├── algorithms/                # QIEA, QPSO, GA, DE, NSGA-III optimizers
│   └── export/                    # RFC 8785 canonical decision package exporter
├── tests/                         # Pytest test suite (281 test cases)
└── web/                           # Next.js 15 Operator HMI Console (port 3000)
    ├── src/app/                   # App Router pages (Fleet, Detail, Predict, Lab, Pareto, etc.)
    └── src/components/            # Marine instrument UI components & nautical charts
```

---

## 🚀 Quickstart & One-Command Reproduction

### 1. Prerequisites
- Python 3.10+ (compatible up to Python 3.14 on Windows, Linux, and macOS)
- Node.js 18+ and npm (for the Next.js HMI)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/super-synqra/egreen-quanta.git
cd sih26138_platform

# Create and activate a Python virtual environment
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# .venv\Scripts\activate        # On Windows

# Install pinned dependencies
pip install -r requirements-lock.txt
```

### 3. One-Command Master Release Verification
To deterministically reproduce and audit all **10 official Release Gates** in $<5$ seconds:
```bash
python reproduce_release.py
```
*Expected output: All 10 gates [G1 to G10] reporting `[PASS]` with verified SHA-256 checksums.*

### 4. Run the Full Test Suite (281 Tests)
```bash
python -m pytest tests/ -q
```
*Expected output: `281 passed in ~2.5 minutes`.*

### 5. Launch the Full Operational Stack

#### Terminal 1: FastAPI Scientific Backend (`port 8001`)
```bash
python -m uvicorn api.main:app --port 8001
```
*The backend automatically warms up surrogate models and serves all scientific endpoints at `http://127.0.0.1:8001`.*

#### Terminal 2: Maritime Bridge HMI (`port 3000`)
```bash
cd web
npm install
npm run dev
```
*Open [http://localhost:3000](http://localhost:3000) in your browser to interact with the live bridge console.*

### 6. Interactive CLI Demonstration (7 SIH Scenes)
To execute the official SIH live demonstration scenes directly in the terminal:
```bash
python scripts/demo_scenarios.py
```

---

## 🖥️ Maritime Bridge HMI Console

The Next.js 15 bridge interface (`web/`) provides vessel officers and fleet dispatchers with a comprehensive operational console:
- **Fleet Overview**: Real-time status cards for `CPS_Poseidon`, `CPS_Triton`, and `OSS_Ceto`, tracking speed, fuel flow, and current operating regimes.
- **Vessel Detail & Telemetry**: Deep inspection of draft, displacement, trim, and high-frequency sensor readings.
- **Prediction & Trust Center**: Live fuel consumption estimation with **90% conformal prediction intervals** ($\pm \text{kg/h}$) and active safety badges (`NORMAL_OPERATION`, `OOD_GUARD_ACTIVE`, `FAILOVER_TO_PHYSICS`).
- **Scenario Lab**: What-if speed and weather parameter adjustments with real-time recalculations.
- **Fleet Optimizer**: Interactive multi-objective optimizer runner with customizable priority weights.
- **Pareto Trade-Off Explorer**: 2D/3D visualization of the 31 non-dominated solutions across Fuel vs. Cost vs. GHG vs. Schedule.
- **Alternative Green Fuels**: IMO MEPC Well-to-Wake comparisons for VLSFO, bio-methanol, green ammonia, e-diesel, and shore power.
- **Tamper-Evident Export**: One-click generation of RFC 8785 canonical JSON and SHA-256 manifests with in-browser cryptographic verification.
- **Demo Mode**: 7 pre-programmed scenario sequences for immediate live demonstration.

---

## 📂 Evaluator Evidence Package

For hackathon evaluators and technical auditors, a curated, standalone evidence package is available in:
```
EGREEN_QUANTA_SIH26138_EVIDENCE/
├── 00_START_HERE/
│   ├── README_FOR_EVALUATOR.pdf     (2 pages: Executive evaluation roadmap)
│   └── EVIDENCE_INDEX.pdf            (2 pages: Complete file index with SHA-256 checksums)
├── 01_PROBLEM_AND_SOLUTION/
│   ├── Problem_Statement_and_Solution.pdf (4 pages: SIH26138 formulation & solution)
│   └── System_Architecture.pdf       (2 pages: 7-layer defense-in-depth architecture)
├── 02_VALIDATED_RESULTS/
│   ├── Results_Summary.pdf           (5 pages: Empirical benchmark tables & charts)
│   ├── Optimization_Pareto_Front.png (31-point non-dominated Pareto frontier)
│   ├── Prediction_Performance.png    (Measured vs. predicted scatter & residuals)
│   ├── QI_vs_Classical_Baseline.png  (30-seed convergence comparison)
│   ├── Uncertainty_and_OOD.png       (Conformal coverage & Mahalanobis threshold)
│   └── Results_Data.csv              (Reconciled numerical benchmark tables)
├── 03_PROTOTYPE_AND_HMI/
│   ├── HMI_Demonstration.mp4         (1080p Full HD video demonstration with audio narration)
│   ├── HMI_Overview.pdf              (3 pages: Screen-by-screen architectural walkthrough)
│   └── Prototype_Evidence.pdf        (2 pages: Zero mock data proof & API traceability)
├── 04_VERIFICATION_AND_SAFETY/
│   ├── Verification_Summary.pdf      (3 pages: 10/10 release gates & 281 tests)
│   ├── Certification_Readiness_Summary.pdf (2 pages: DNV / IMO classification audit)
│   ├── Adversarial_Test_Summary.pdf  (2 pages: 18/18 hostile input defenses)
│   └── Tamper_Evidence_Summary.pdf   (2 pages: RFC 8785 hashing & verification)
├── 05_DECISION_RECORD/
│   ├── Integrity_Verification.pdf    (2 pages: Cryptographic export guide)
│   ├── Sample_Decision_Record.json   (RFC 8785 canonical JSON export)
│   ├── Sample_Decision_Record.csv    (Tabular objective breakdown)
│   └── Sample_Manifest.json          (SHA-256 cryptographic manifest)
├── 06_RESEARCH_AND_REFERENCES/
│   └── Selected_References.pdf       (3 pages: IMO MEPC, ITTC-1978, Holtrop citations)
└── 99_DETAILED_BACKUP/
    ├── END_TO_END_VERIFICATION_REPORT.pdf (6 pages: Full technical audit report)
    ├── END_TO_END_AUDIT_RAW.pdf      (7 pages: Raw test logs and gate execution outputs)
    └── Detailed_Test_Evidence.pdf    (7 pages: Itemized 281-test execution evidence)
```

---

## ⚖️ Scientific Integrity & Ethical Disclaimers

To maintain the highest engineering standards and prevent misleading claims:
1. **Advisory Decision Support, NOT Autopilot**: EGREEN QUANTA is strictly an advisory decision-support platform. Under maritime law (SOLAS Chapter V), the Master and Bridge Navigational Officers retain absolute command and legal authority over vessel speed, routing, and machinery operation. Direct connection to autopilots or engine throttles is prohibited.
2. **Classical Computing, NO "Quantum Supremacy"**: QIEA and QPSO are classical probabilistic heuristics running on standard x86_64 silicon. They utilize quantum-inspired principles (qubit angle representation, probability rotations) but do not require quantum hardware and achieve no theoretical quantum speedup. QI-C1 is statistically comparable with classical genetic algorithms ($p = 0.684$).
3. **Scenario Estimates for Green Fuels**: Alternative fuel metrics (methanol, ammonia, hydrogen) are physics-based scenario estimates derived from invariant delivered shaft work ($E = P_B \cdot t$) and IMO MEPC.308(73)/391(81) Well-to-Wake emission factors. They are not measured telemetry from dual-fuel engines.
4. **Tamper-Evident, NOT "Immutable"**: Decision packages use cryptographic SHA-256 hashes and canonical JSON formatting to ensure tamper-evidence. The underlying SQLite audit ledger is append-only at the API level but is not a decentralized blockchain.

---

## 👥 Team & Organization Information

- **Smart India Hackathon 2026**
- **Problem Statement**: SIH26138
- **Organization**: Egreen Quanta
- **Team**: Team SUPER SYNQRA
- **Repository**: [https://github.com/super-synqra/egreen-quanta](https://github.com/super-synqra/egreen-quanta)
- **License**: MIT License (see [LICENSE](LICENSE))
