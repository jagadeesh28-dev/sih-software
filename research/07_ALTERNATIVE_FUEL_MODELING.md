# 07 — ALTERNATIVE FUEL MODELING: SCIENTIFIC FOUNDATIONS
## RQ9: How Do Alternative Fuels Affect Optimization Formulation?

---

## 1. Alternative Fuel Landscape (IMO 2025 Horizon)

The SIH26138 problem includes four fuel modes:
1. **HFO** — Heavy Fuel Oil (conventional)
2. **LNG** — Liquefied Natural Gas
3. **Methanol** — Bio-methanol or grey methanol
4. **Bio-HFO** — Biofuel-blended HFO

### 1.1 Key Regulatory Drivers

**IMO 2023 GHG Strategy:**  
- 2030: 20% reduction in total GHG emissions vs. 2008 baseline
- 2040: 70% reduction
- 2050: Net-zero (indicative)

**FuelEU Maritime (EU, 2025):**  
- Annual GHG intensity limit on energy delivered to EU-flagged or EU-calling vessels
- Penalty for non-compliance: €2,400/ton CO₂-equivalent excess
- Multiplier for LSFO vs. zero-carbon fuels

**CII (Carbon Intensity Indicator, IMO 2023+):**  
- Annual rating: A (best) → E (worst)
- Ships rated D or E for consecutive years face operational restrictions
- CII depends on: vessel type, DWT, reported fuel consumption, distance

---

## 2. Fuel Cost and GHG Parameters

### 2.1 Cost Structure

| Fuel Mode | Energy Price ($/GJ) | CO₂ Intensity (gCO₂/MJ) | GHG Intensity (gCO₂eq/MJ) | Availability Risk |
|:---|:---:|:---:|:---:|:---|
| HFO | 14–18 | 91.5 | 91.5 | Low |
| LNG | 22–28 | 57.5 | 75.5 (incl. methane slip) | Medium |
| Methanol (grey) | 35–45 | 69.3 | 69.3 | Medium |
| Bio-HFO (20% blend) | 20–27 | 72.0 | 72.0 | Medium-High |

_Note: GHG intensity for LNG includes 3.1% methane slip (well-to-wake, LCA approach per FuelEU Maritime Annex II)._

### 2.2 Bunkering Constraints

Each fuel mode has different bunkering infrastructure availability:
- **HFO**: Available at virtually all major ports
- **LNG**: Available at ~200 major ports globally (primary ports: Rotterdam, Singapore, Houston)
- **Methanol**: Available at ~60 ports globally (2025 data)
- **Bio-HFO**: Available by arrangement (not standard bunker)

This creates a **port-fuel compatibility constraint**:
$$\text{fuel\_avail}(v, \text{port}) = \{f : f \in \mathcal{F}_v \cap \mathcal{F}_{port}\}$$

If a vessel selects LNG but its route includes a port without LNG bunkering, the fuel choice is infeasible.

---

## 3. How Alternative Fuels Change the Optimization Formulation

### 3.1 Fuel Mode as Categorical Variable (Existing)

Our formulation treats fuel mode $f_v$ as a categorical decision variable. This is correct.

The **cost calculation** must use:
$$\text{FuelCost}(v, s_v, f_v, D) = \text{FuelConsumption}(v, s_v, D) \cdot \text{EnergyConversionFactor}(f_v) \cdot \text{FuelPrice}(f_v)$$

where:
- $\text{FuelConsumption}(v, s_v, D)$ = surrogate model (telemetry-calibrated)
- $\text{EnergyConversionFactor}(f_v)$ = fuel-specific energy density conversion
- $\text{FuelPrice}(f_v)$ = current market price for fuel type $f_v$

### 3.2 GHG Intensity Constraint (New for FuelEU Maritime)

FuelEU Maritime defines GHG intensity $GFI$:
$$GFI_{actual} = \frac{\sum_{v} \text{Energy}(v) \cdot \text{GHGIntensity}(f_v)}{\sum_{v} \text{Energy}(v)} \leq GFI_{limit}$$

This is a **fleet-wide weighted average constraint**, not a per-vessel constraint. This creates coupling across all vessels: the fuel mode choice for one vessel affects whether others can use high-GHG fuels.

**Optimization implication:** This constraint cannot be decomposed per-vessel. It must be evaluated fleet-wide. This is naturally handled by our fleet-level fitness function.

### 3.3 CII Per-Vessel Constraint

$$CII_v = \frac{\text{CO}_2_{v}(\text{annual})}{DWT_v \cdot \text{NM}_v} \leq CII_{ref,v}$$

This is a **per-vessel constraint** dependent on:
- Vessel type and DWT (fixed)
- Annual distance (partially fixed by route)
- CO₂ emissions (depends on speed + fuel type)

**Optimization implication:** Given a fixed route, CII constraint creates a coupled $\{s_v, f_v\}$ feasibility region: higher speeds with HFO are infeasible; the same speeds with LNG may be CII-compliant.

---

## 4. Alternative Fuels and the Categorical Variable Problem

The presence of alternative fuels **strengthens the case for QIEA over QPSO** for fuel mode selection:

1. **Non-ordinal categories:** HFO, LNG, Methanol, Bio-HFO have no natural ordering. There is no sense in which "LNG is between HFO and Methanol." Continuous interpolation (QPSO's implicit mechanism) is physically meaningless for fuel type.

2. **Discontinuous cost landscape:** Switching from HFO to LNG typically reduces cost by $X but requires LNG-capable engine. This creates discrete jumps in the cost surface that QPSO's continuous update cannot handle without rounding artifacts.

3. **Port-fuel compatibility:** The feasibility of a fuel choice depends on the route, which depends on demand assignment. This **cross-constraint coupling** is naturally handled by QIEA's joint Q-bit representation.

4. **Methane slip modeling:** LNG's GHG intensity is significantly affected by methane slip, which is engine-speed and vessel-type dependent. The per-vessel categorical nature of this is well-suited to QIEA's per-Q-bit update mechanism.

---

## 5. Uncertainty in Alternative Fuel Costs

Fuel cost uncertainty is significantly higher for alternative fuels:
- **HFO price volatility**: σ ≈ $15/ton (2023–2025 data)
- **LNG price volatility**: σ ≈ $30/ton (global LNG spot markets)
- **Methanol price volatility**: σ ≈ $50/ton (immature market, supply chain risk)

This motivates our CVaR-robust formulation where the optimization objective is:
$$\min_{f,s,d,p} \; \mathbb{E}[J] + \lambda \cdot \text{CVaR}_{0.95}[J]$$

with $\lambda$ = risk aversion weight. CVaR captures the tail risk of alternative fuel price spikes.

**Optimization implication:** The robustness formulation increases the effective number of fitness evaluations (multiple scenario evaluations per solution). This increases computational cost but does not fundamentally change the representation requirements.

---

## 6. Implications for Algorithm Design

| Feature | QPSO (Existing) | DE (Existing) | QIEA (Proposed) | Hybrid QI-HFO (Proposed) |
|:---|:---:|:---:|:---:|:---:|
| Non-ordinal fuel mode | ❌ | ⚠️ Repair | ✅ | ✅ |
| Port-fuel compatibility | ❌ | ⚠️ Penalty | ✅ Filter | ✅ |
| Fleet GHG constraint | ⚠️ Penalty | ⚠️ Penalty | ✅ | ✅ |
| Per-vessel CII | ⚠️ Penalty | ✅ | ✅ | ✅ |
| CVaR robustness | ⚠️ Nested | ✅ | ✅ | ✅ |
| Methane slip | ⚠️ Penalty | ✅ | ✅ | ✅ |
| Fuel cost uncertainty | ⚠️ | ✅ | ✅ | ✅ |
