# 11 — COMMERCIAL & PATENT PRIOR ART
## RQ14–RQ16: Commercial Systems and Patent Landscape

---

## 1. Commercial System Survey

### 1.1 Wärtsilä Fleet Optimisation Solution (FOS)

**Website:** wartsila.com/services/fleet-optimisation  
**Technology:** AI/ML, route optimization, predictive analytics  
**Capabilities:**
- Voyage optimization (speed, route, weather routing)
- Real-time fuel consumption monitoring
- CII compliance tracking and prediction
- Engine performance analytics

**What it does NOT do:**
- Fuel type/mode optimization (no alternative fuel selection)
- Fleet-wide demand assignment optimization
- Quantum-inspired metaheuristics
- Open-source benchmark availability
- Formal statistical analysis with multiple seeds

**Intellectual Property:** Closed proprietary system. Algorithm details unpublished. Does not constitute academic prior art.

**Assessment:** Academic work on QI fleet optimization is not blocked by Wärtsilä FOS.

---

### 1.2 Kongsberg K-Fleet / Vessel Insight

**Technology:** Connected vessel data platform, performance analytics  
**Capabilities:**
- Fuel consumption reporting
- Performance benchmarking across fleet
- CII/Carbon compliance module
- Weather-optimized routing via DTN partnership

**What it does NOT do:**
- QI optimization
- Multi-fuel scenario planning
- Combinatorial fleet assignment optimization
- Public benchmarking

---

### 1.3 ABB OCTOPUS Marine Advisory System

**Technology:** Motion monitoring, weather routing, fuel efficiency  
**Capabilities:**
- Real-time hull performance monitoring
- Weather routing for fuel savings
- Integration with ABB Genix AI platform
- ~13,000 vessels serviced annually (post-DTN integration)

**What it does NOT do:** Same limitations as above.

---

### 1.4 Inmarsat / Fleet Data

**Technology:** Satellite connectivity + fleet analytics  
**Capabilities:** Voyage efficiency tracking, emissions reporting

---

## 2. Patent Landscape

### 2.1 Patent Search Methodology

**Databases searched:**
- Google Patents (patents.google.com)
- WIPO PatentScope
- USPTO Public PAIR
- Espacenet

**Key search terms:**
- "quantum-inspired" AND ("vessel routing" OR "fleet scheduling" OR "ship optimization")
- "quantum genetic algorithm" AND "maritime"
- "quantum particle swarm" AND "shipping"
- "QUBO" AND ("vessel" OR "ship" OR "fleet")

**Search period:** 2015–2026

### 2.2 Patent Findings

**Finding 1:** No patents found explicitly claiming quantum-inspired optimization for maritime fleet management (vessel routing + fuel assignment + CII compliance). Evidence Class A.

**Finding 2:** Several patents exist for quantum-inspired logistics routing in general (not maritime-specific). These are general QUBO or quantum annealing formulations for VRP-type problems. They do not cover maritime-specific regulatory constraints.

**Key general QI logistics patents:**
- US 2023/0385791 A1 (2023): Quantum-computing-based route optimization system. Covers QUBO formulation for general routing. Does NOT address maritime CII, fuel type, or heterogeneous fleets.
- EP 4163827 A1 (2023): AI-based route planning for logistics. Uses quantum-inspired annealing. Does not address maritime.

**Finding 3:** No patents cover the combination of: (a) QIEA Q-bit representation + (b) maritime fuel type categorical + (c) CII/FuelEU compliance + (d) CVaR robustness.

### 2.3 Freedom to Operate Assessment

The SIH26138 research prototype is:
- ✅ Free to develop as academic research
- ✅ Free to publish in peer-reviewed venues
- ✅ Free to open-source
- ⚠️ Commercial deployment would require patent freedom-to-operate analysis (outside scope of academic SIH research)

---

## 3. Software / Open Source Prior Art

### 3.1 QPSO Implementations

Multiple open-source QPSO implementations exist (PyPI, GitHub):
- `pyqpso` — Standard QPSO, continuous space only
- `qpso-python` — Academic implementations
- **None address** maritime fleet optimization, CII compliance, or categorical fuel mode

### 3.2 QIEA Implementations

- GitHub repositories for QIEA in various contexts (TSP, knapsack, scheduling)
- No Python package specifically for maritime optimization with regulatory constraints

### 3.3 Maritime Optimization Open Source

- **ShipX** (SINTEF): Hydrodynamics only, not scheduling
- **OpenVSP**: Vessel geometry, not fleet scheduling
- **PortPy**: Port scheduling research tool, not fleet-level

**Assessment:** No open-source software combines QI optimization with maritime fleet regulatory constraints. Our platform would be novel open-source software.

---

## 4. Academic Novelty vs. Commercial Existence

An important distinction:

**Commercial tools** may solve similar practical problems but:
1. Do not publish algorithms (no academic peer review)
2. Are not open benchmarks
3. May not use QI methods
4. Cannot be reproduced or verified by third parties

**Academic novelty** requires:
1. Publication in peer-reviewed venues
2. Reproducible methodology
3. Comparison with baselines under equal conditions
4. Honest reporting including negative results

Our work satisfies academic novelty criteria. Commercial existence does not block academic contribution.

---

## 5. Summary

| Prior Art Category | Blocks Research Gap? | Assessment |
|:---|:---:|:---|
| Wärtsilä/Kongsberg/ABB commercial systems | ❌ | Closed, non-QI, non-academic |
| Han 2023 (QGA maritime) | ❌ Partial | Single vessel, no fleet, no fuel choice |
| Fraunhofer CML pilots | ❌ | QUBO/annealing, no CII/FuelEU, non-academic |
| General QI logistics patents | ❌ | VRP only, no maritime-specific features |
| Open-source QPSO/QIEA | ❌ | Academic but no maritime domain |
| Aviation FAP (QI) | ❌ | Different domain, no fuel, no CII |
| Phase 4 baseline (DE + QPSO) | ✅ Self-baseline | Our own work; strengthens novelty claim |
