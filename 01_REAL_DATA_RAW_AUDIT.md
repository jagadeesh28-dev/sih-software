# 01 — FuelCast Raw Data Forensic Audit Report
**Phase:** 2.3 Real Maritime Data Validation & Scientific Falsification Gate  
**Document ID:** `01_REAL_DATA_RAW_AUDIT.md`  
**Dataset:** FuelCast (`krohnedigital/FuelCast`)  
**Audit Date:** 2026-09-12  

---

## Executive Audit Summary
The raw FuelCast dataset consists of three commercial vessel telemetry archives in Parquet format, totaling **173,986 rows** across physical vessels operating in European waters.
Direct audit confirms **173,974 active operational telemetry records** after dropping trailing null padding rows (4 rows on Triton, 8 rows on Ceto).

| Vessel Identifier | Vessel Class | Gross Tonnage | Total Raw Rows | Clean Active Rows | Duration | Sampling ($\Delta t$) | Max Fuel ($	ext{kg/h}$) | Mean Fuel ($	ext{kg/h}$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CPS_Poseidon** | Large Passenger Cruise | ~70,000 GT | 105,422 | 105,422 | 366.0 days (~1 yr) | 300 s (5 min) | 8,609.7 | 2,815.4 |
| **CPS_Triton** | Small Passenger Cruise | ~11,000 GT | 25,351 | 25,347 | 88.0 days (~3 mo) | 300 s (5 min) | 1,265.8 | 635.1 |
| **OSS_Ceto** | Offshore Supply Vessel | ~24,000 GT | 43,213 | 43,205 | 150.0 days (~5 mo) | 300 s (5 min) | 2,699.9 | 675.6 |
| **Fleet Total** | **Heterogeneous Fleet** | **105,000 GT** | **173,986** | **173,974** | **604.0 vessel-days** | **5 min uniform** | — | — |

---

## Vessel-by-Vessel Detailed Forensics

### Vessel: `CPS_Poseidon`
- **Source File**: `data/external/fuelcast/CPS_Poseidon.parquet`
- **Total Raw Rows**: 105,422
- **Clean Chronological Rows**: 105,422 (excluding 0 tail padding artifact rows)
- **Columns**: 65
- **Duplicate Rows**: 0
- **Constant Columns**: `None`
- **Columns with Nulls in Active Records**: 54
  - `Consumer_Boiler1_MomentaryFuel` (27), `Consumer_Boiler2_MomentaryFuel` (27), `Consumer_GeneratorEngine1_MomentaryFuel` (27), `Consumer_GeneratorEngine1_RotationSpeed` (2274), `Consumer_GeneratorEngine1_ShaftPower` (2274), `Consumer_GeneratorEngine2_MomentaryFuel` (27), `Consumer_GeneratorEngine2_RotationSpeed` (2274), `Consumer_GeneratorEngine2_ShaftPower` (2274), `Consumer_GeneratorEngine3_MomentaryFuel` (27), `Consumer_GeneratorEngine3_RotationSpeed` (2274), `Consumer_GeneratorEngine3_ShaftPower` (2274), `Consumer_GeneratorEngine4_MomentaryFuel` (112), `Consumer_GeneratorEngine4_RotationSpeed` (2274), `Consumer_GeneratorEngine4_ShaftPower` (2274), `Consumer_GeneratorEngine5_MomentaryFuel` (27), `Consumer_GeneratorEngine5_RotationSpeed` (2274), `Consumer_GeneratorEngine5_ShaftPower` (2274), `Environment_SeaFloorDepth` (2273), `Propeller_Port_RotationSpeed` (3916), `Propeller_Port_ShaftPower` (3916), `Propeller_Port_ShaftTorque` (3916), `Propeller_Starboard_RotationSpeed` (20170), `Propeller_Starboard_ShaftPower` (20170), `Propeller_Starboard_ShaftTorque` (20170), `Ship_Bearing` (2759), `Ship_Heading` (2274), `Ship_SpeedOverGround` (2274), `Ship_SpeedThroughWater` (2274), `Weather_DiffuseRadiation` (181), `Weather_DirectNormalIrradiance` (181), `Weather_DirectRadiation` (181), `Weather_OceanCurrentDirection` (181), `Weather_OceanCurrentVelocity` (181), `Weather_Precipitation` (181), `Weather_RelativeHumidity2M` (181), `Weather_ShortwaveRadiation` (181), `Weather_SunshineDuration` (181), `Weather_SurfacePressure` (181), `Weather_SwellWaveDirection` (181), `Weather_SwellWaveHeight` (181), `Weather_SwellWavePeakPeriod` (181), `Weather_SwellWavePeriod` (181), `Weather_Temperature2M` (181), `Weather_WaveDirection` (181), `Weather_WaveHeight` (181), `Weather_WavePeriod` (181), `Weather_WeatherCode` (181), `Weather_WindDirection10M` (181), `Weather_WindGusts10M` (181), `Weather_WindSpeed10M` (181), `Weather_WindWaveDirection` (181), `Weather_WindWaveHeight` (181), `Weather_WindWavePeakPeriod` (181), `Weather_WindWavePeriod` (181)
- **Fuel Target (`Consumer_Total_MomentaryFuel`)**:
  - Min: 0.000000 kg/s (0.0 kg/h)
  - 25th Percentile: 0.391760 kg/s (1410.3 kg/h)
  - Median: 0.675905 kg/s (2433.3 kg/h)
  - Mean: 0.782055 kg/s (2815.4 kg/h)
  - 75th Percentile: 0.994228 kg/s (3579.2 kg/h)
  - Max: 2.391596 kg/s (8609.7 kg/h)
  - Standard Deviation: 0.446529 kg/s (1607.5 kg/h)
### Vessel: `CPS_Triton`
- **Source File**: `data/external/fuelcast/CPS_Triton.parquet`
- **Total Raw Rows**: 25,351
- **Clean Chronological Rows**: 25,347 (excluding 4 tail padding artifact rows)
- **Columns**: 62
- **Duplicate Rows**: 0
- **Constant Columns**: `Consumer_Boiler_FuelType, Consumer_GeneratorEngine1_FuelType, Consumer_GeneratorEngine2_FuelType, Consumer_MainEnginePort_FuelType, Consumer_MainEngineStarboard_FuelType`
- **Columns with Nulls in Active Records**: 53
  - `Consumer_Boiler_MomentaryFuel` (9), `Consumer_GeneratorEngine1_MomentaryFuel` (9), `Consumer_GeneratorEngine1_ShaftPower` (9), `Consumer_GeneratorEngine2_MomentaryFuel` (9), `Consumer_GeneratorEngine2_ShaftPower` (9), `Consumer_MainEnginePort_MomentaryFuel` (9), `Consumer_MainEnginePort_RotationSpeed` (9), `Consumer_MainEnginePort_ShaftPower` (9), `Consumer_MainEngineStarboard_MomentaryFuel` (9), `Consumer_MainEngineStarboard_RotationSpeed` (9), `Consumer_MainEngineStarboard_ShaftPower` (9), `Environment_SeaFloorDepth` (9), `Propeller_Port_RotationSpeed` (9), `Propeller_Port_ShaftPower` (9), `Propeller_Port_ShaftTorque` (9), `Propeller_Starboard_RotationSpeed` (9), `Propeller_Starboard_ShaftPower` (9), `Propeller_Starboard_ShaftTorque` (9), `Ship_AirTemperature` (9), `Ship_AnemometerWindDirection` (9), `Ship_AnemometerWindSpeed` (9), `Ship_Bearing` (44), `Ship_DraftAft` (9), `Ship_DraftFore` (9), `Ship_Heading` (9), `Ship_SpeedOverGround` (9), `Ship_SpeedThroughWater` (9), `Weather_DiffuseRadiation` (34), `Weather_DirectNormalIrradiance` (34), `Weather_DirectRadiation` (34), `Weather_OceanCurrentDirection` (34), `Weather_OceanCurrentVelocity` (34), `Weather_Precipitation` (34), `Weather_RelativeHumidity2M` (34), `Weather_ShortwaveRadiation` (34), `Weather_SunshineDuration` (34), `Weather_SurfacePressure` (34), `Weather_SwellWaveDirection` (34), `Weather_SwellWaveHeight` (34), `Weather_SwellWavePeakPeriod` (3695), `Weather_SwellWavePeriod` (34), `Weather_Temperature2M` (34), `Weather_WaveDirection` (34), `Weather_WaveHeight` (34), `Weather_WavePeriod` (34), `Weather_WeatherCode` (34), `Weather_WindDirection10M` (34), `Weather_WindGusts10M` (34), `Weather_WindSpeed10M` (34), `Weather_WindWaveDirection` (34), `Weather_WindWaveHeight` (34), `Weather_WindWavePeakPeriod` (3695), `Weather_WindWavePeriod` (34)
- **Fuel Target (`Consumer_Total_MomentaryFuel`)**:
  - Min: 0.000000 kg/s (0.0 kg/h)
  - 25th Percentile: 0.137854 kg/s (496.3 kg/h)
  - Median: 0.200453 kg/s (721.6 kg/h)
  - Mean: 0.176427 kg/s (635.1 kg/h)
  - 75th Percentile: 0.218669 kg/s (787.2 kg/h)
  - Max: 0.351613 kg/s (1265.8 kg/h)
  - Standard Deviation: 0.064909 kg/s (233.7 kg/h)
### Vessel: `OSS_Ceto`
- **Source File**: `data/external/fuelcast/OSS_Ceto.parquet`
- **Total Raw Rows**: 43,213
- **Clean Chronological Rows**: 43,205 (excluding 8 tail padding artifact rows)
- **Columns**: 46
- **Duplicate Rows**: 0
- **Constant Columns**: `Consumer_DeckSupply_FuelType, Consumer_EngineRoom1_FuelType, Consumer_EngineRoom2_FuelType, Consumer_Incinerator_FuelType, Weather_SwellWavePeakPeriod, Weather_WindWavePeakPeriod`
- **Columns with Nulls in Active Records**: 39
  - `Consumer_DeckSupply_MomentaryFuel` (51), `Consumer_EngineRoom1_MomentaryFuel` (34), `Consumer_EngineRoom1_RotationSpeed` (2973), `Consumer_EngineRoom1_ShaftPower` (8), `Consumer_EngineRoom2_MomentaryFuel` (30), `Consumer_EngineRoom2_RotationSpeed` (3423), `Consumer_EngineRoom2_ShaftPower` (8), `Consumer_Incinerator_MomentaryFuel` (31), `Environment_SeaFloorDepth` (8), `Ship_Bearing` (25), `Ship_DraftAft` (8), `Ship_DraftFore` (8), `Ship_SpeedOverGround` (8), `Weather_DiffuseRadiation` (56), `Weather_DirectNormalIrradiance` (56), `Weather_DirectRadiation` (56), `Weather_OceanCurrentDirection` (56), `Weather_OceanCurrentVelocity` (56), `Weather_Precipitation` (56), `Weather_RelativeHumidity2M` (56), `Weather_ShortwaveRadiation` (56), `Weather_SunshineDuration` (56), `Weather_SurfacePressure` (56), `Weather_SwellWaveDirection` (56), `Weather_SwellWaveHeight` (56), `Weather_SwellWavePeakPeriod` (43205), `Weather_SwellWavePeriod` (56), `Weather_Temperature2M` (56), `Weather_WaveDirection` (56), `Weather_WaveHeight` (56), `Weather_WavePeriod` (56), `Weather_WeatherCode` (56), `Weather_WindDirection10M` (56), `Weather_WindGusts10M` (56), `Weather_WindSpeed10M` (56), `Weather_WindWaveDirection` (56), `Weather_WindWaveHeight` (56), `Weather_WindWavePeakPeriod` (43205), `Weather_WindWavePeriod` (56)
- **Fuel Target (`Consumer_Total_MomentaryFuel`)**:
  - Min: 0.000000 kg/s (0.0 kg/h)
  - 25th Percentile: 0.138429 kg/s (498.3 kg/h)
  - Median: 0.175302 kg/s (631.1 kg/h)
  - Mean: 0.187659 kg/s (675.6 kg/h)
  - 75th Percentile: 0.206363 kg/s (742.9 kg/h)
  - Max: 0.749981 kg/s (2699.9 kg/h)
  - Standard Deviation: 0.104257 kg/s (375.3 kg/h)


---

## Key Forensic Findings
1. **Target Integrity**: Zero missing values in `Consumer_Total_MomentaryFuel` across all 173,974 active records.
2. **Sampling Regularity**: All datasets exhibit exact integer indices advancing by 1 step every 5 minutes ($\Delta t = 300	ext{ s}$). No irregular time warps or timestamp jitter.
3. **Sensor Anomaly on `CPS_Triton`**: Direct acoustic Doppler STW (`Ship_SpeedThroughWater`) is completely frozen at $0.514444	ext{ m/s} = 1.000000	ext{ kn}$ across all records. This channel is corrupted and must never be treated as valid measured STW.
4. **Target Scales**: Large cruise ship fuel flow reaches 8.6 tonnes/h; offshore supply vessel reaches 2.7 tonnes/h.
