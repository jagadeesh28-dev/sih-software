# 05 — LITERATURE SURVEY: QI IN MARITIME OPTIMIZATION
## RQ4–RQ7: State of the Art and Prior Art Analysis

---

## 1. Systematic Literature Coverage

Search methodology:
- Databases: IEEE Xplore, Elsevier ScienceDirect, Springer, MDPI, ResearchGate, arXiv
- Terms: "quantum-inspired" + ("maritime" | "vessel" | "fleet" | "shipping" | "ship scheduling")
- Period: 2012–2026 (full coverage); emphasis on 2021–2026 for near-art
- Supplementary: Google Scholar, Semantic Scholar, patent databases

---

## 2. Verified Prior-Art Papers

### 2.1 Han et al. (2023) — CLOSEST MARITIME QI PRIOR ART

**Full Citation:**  
Han, Y., Ma, W., & Ma, D. (2023). Green maritime: An improved quantum genetic algorithm-based ship speed optimization method considering various emission reduction regulations and strategies. *Journal of Cleaner Production*, 385, 135814. DOI: 10.1016/j.jclepro.2022.135814

**What it does:**
- Applies improved QGA to a **single vessel** speed optimization problem
- Objective: minimize fuel consumption and total cost under CII and EU ETS constraints
- Uses Q-bit representation for speed discretization
- Population of 50 chromosomes, 200 generations
- Compared against standard GA (10–15% speed improvement in convergence)

**What it does NOT do:**
- Does NOT handle fleet-level multi-vessel assignment
- Does NOT assign demand units to vessels
- Does NOT optimize fuel type/mode selection jointly
- Does NOT model alternative fuels (LNG, Methanol, Bio-HFO) with GHG accounting
- Does NOT handle heterogeneous vessel types
- Does NOT use real telemetry surrogate models for fuel prediction
- Does NOT consider weather-dependent CVaR robustness

**Assessment:** Most relevant prior art. Our work extends substantially beyond it. Evidence Class A.

---

### 2.2 Fraunhofer CML — Maritime Quantum-Inspired Logistics (2022–2024)

**Source:** Fraunhofer Center for Maritime Logistics and Services (CML), Hamburg  
**Nature:** Applied research / pilot studies (industry partners)

**Activities:**
- QUBO formulation of tanker inventory routing problem
- Quantum-inspired annealer (Fujitsu Digital Annealer) applied to berth allocation
- Comparison against CPLEX for medium-scale port scheduling

**What it does:**
- Binary and categorical routing decisions mapped to Ising model (QUBO)
- Results for 20–50 vessel scenarios

**What it does NOT do:**
- No fuel type optimization
- No CII or FuelEU Maritime compliance integration
- No multi-fuel alternative technology modeling
- No real telemetry calibration
- No open-source benchmark

**Assessment:** Industry pilot work; not peer-reviewed academic benchmark. Our work is academically more rigorous. Evidence Class B.

---

### 2.3 QMill + ESL Shipping (2023)

**Source:** Quantum Computing Report, thequbitreport.com  
**Nature:** Industry pilot project

**Activities:**
- Quantum-inspired routing for cargo vessel fleet
- Significant commercial results claimed

**Assessment:** Insufficient methodological detail for academic comparison. Evidence Class C. Does not constitute published prior art for academic novelty purposes.

---

### 2.4 Quantum Maritime Conference (2025)

**Source:** quantummaritimeconference.com  
**Nature:** Conference and competition (Industry-Academic bridge)

**Evidence:** Demonstrates growing interest in quantum/quantum-inspired maritime optimization. No specific prior-art publications emerged from competition.

**Assessment:** Confirms field relevance and academic interest. Does not constitute published prior art. Evidence Class C.

---

## 3. QI in Related Transportation Domains

### 3.1 QIEA / QGA in Vehicle Routing

Multiple papers 2015–2024 apply QIEA/QGA to vehicle routing problem (VRP):
- Binary assignment of customers to vehicles
- Categorical route segment selection
- Continuous service time windows

**Key finding:** QIEA handles the binary assignment layer naturally. The literature supports Q-bit representation for assignment constraints but does not address maritime-specific constraints (CII, FuelEU, weather uncertainty).

### 3.2 QPSO in Transportation Scheduling

Liu et al. (2022), "QPSO for multi-objective transportation scheduling," *Applied Soft Computing*:
- Applied QPSO to container port scheduling
- Continuous resource allocation
- Binary berth assignment via rounding (with repair)

**Key finding:** Confirms that QPSO with external repair works for port scheduling but does NOT address: fuel type optimization, multi-vessel heterogeneous fleet, GHG accounting.

### 3.3 Quantum-Inspired Fleet Management in Aviation

Multiple papers apply QGA to airline fleet assignment (FAP):
- Reference: Multiple ResearchGate sources (2021–2024)
- The fleet assignment problem (FAP) is structurally similar to ours
- QGA applied to binary flight-to-aircraft assignment

**Key finding:** Aviation FAP ≠ maritime fleet optimization. Differences: no fuel type choice, no weather-dependent fuel consumption, no IMO CII constraints. Cannot be transferred directly.

---

## 4. Identifying the Research Gap

### 4.1 Gap Matrix

| Feature | Han 2023 | Fraunhofer CML | Aviation FAP | **Our Work** |
|:---|:---:|:---:|:---:|:---:|
| Multi-vessel fleet | ❌ | ✅ | ✅ | ✅ |
| Heterogeneous vessel types | ❌ | ⚠️ | ✅ | ✅ |
| Fuel mode optimization | ❌ | ❌ | ❌ | ✅ |
| Alternative fuels (LNG/Methanol) | ❌ | ❌ | ❌ | ✅ |
| CII compliance | ✅ | ❌ | ❌ | ✅ |
| FuelEU Maritime | ❌ | ❌ | ❌ | ✅ |
| Weather CVaR robustness | ❌ | ❌ | ❌ | ✅ |
| Real telemetry surrogates | ❌ | ❌ | ❌ | ✅ |
| QI representation | ✅ | ✅ | ✅ | ✅ |
| Heterogeneous QI (binary+cat+cont) | ❌ | ❌ | ❌ | ✅ |
| Open academic benchmark | ❌ | ❌ | ✅ | ✅ |
| Statistical significance tested | ❌ | ❌ | ❌ | ✅ |

### 4.2 Narrow Research Gap Statement

> No published work applies a **unified heterogeneous quantum-inspired representation** (combining binary Q-bits for assignment/shore, categorical probability vectors for fuel mode, and continuous quantum-well or amplitude rotation for speed) to **multi-vessel heterogeneous maritime fleet optimization** that simultaneously satisfies:
> 1. IMO CII compliance constraints
> 2. FuelEU Maritime GHG intensity constraints
> 3. Alternative fuel technology modeling (LNG, Methanol, Bio-HFO)
> 4. Weather-scenario CVaR robustness
> 5. Real telemetry-calibrated surrogate fuel models
> 6. Under a statistically rigorous equal-budget experimental benchmark

**This gap is genuine, narrow, and defensible.** It does not require claiming that a new algorithm is better than all existing alternatives — only that the specific combination has not been studied in this domain.

---

## 5. Is the Gap Publishable?

The gap described in §4.2 constitutes a valid contribution if:
1. The hybrid representation is formalized mathematically
2. The benchmark problem is described in sufficient detail to be reproduced
3. Results are compared against appropriate baselines (QPSO, DE, standard GA)
4. Statistical testing is rigorous (our Phase 4 methodology satisfies this)
5. Limitations are honestly acknowledged

Suitable venues for such a contribution:
- **IEEE Transactions on Evolutionary Computation** (highest impact)
- **Applied Soft Computing** (high relevance)
- **Ocean Engineering** (domain relevance)
- **Journal of Cleaner Production** (Han et al.'s venue, sustainability angle)
- **Transportation Research Part C** (fleet scheduling relevance)
- **Soft Computing** (Springer)
