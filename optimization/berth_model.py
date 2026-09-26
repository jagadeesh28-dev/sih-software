"""
Berth-phase (alongside) energy accounting, shared by Phase4FleetEvaluator and SIHObjectiveEngine.

While berthed the hotel load H [kW] must be supplied for P [h] either by the shore grid or by the
vessel's own generators. The two cases are mutually exclusive and symmetric:

    E_berth = H * P                                     [kWh]

    shore power ON  (cold ironing):
        C = E_berth * tariff + connection_fee           (grid electricity; no fuel, no ETS)
        GHG = E_berth * grid_factor / 1e6               [t CO2e]

    shore power OFF (onboard generation, selected pathway fuel):
        m_vlsfo_eq = E_berth * SFOC                     [kg VLSFO-equivalent]
        m_fuel = LHV conversion of m_vlsfo_eq to the pathway (FleetEmissionsEngine)
        C = m_fuel * bunker_price + TtW_CO2 * carbon_price   (FleetCostEngine, same as voyage fuel)
        GHG = WtW(m_fuel, pathway)                      (FleetEmissionsEngine, same as voyage fuel)

Assumptions: SFOC = 0.220 kg VLSFO-eq/kWh (the constant already used for the hotel-load floor);
auxiliary generators burn the vessel's selected pathway fuel; grid factor, tariff and fee come
from configs/fuels.yaml; FuelEU is assessed on the sea passage only (berth energy excluded).
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Optional

from common.config_loader import load_config

SFOC_KG_VLSFO_PER_KWH = 0.220   # auxiliary generator specific fuel consumption (VLSFO-equivalent)
DEFAULT_PORT_HOURS = 2.0        # assumed berth duration per demand in the fleet scenario (scenario input)


def grid_emission_factor_g_per_kwh(fuels_config: Optional[Dict[str, Any]] = None) -> float:
    if fuels_config is None:
        return _configured_grid_factor()
    return float(fuels_config.get("shore_power", {}).get("grid_emission_factor_g_co2e_kwh", 450.0))


@lru_cache(maxsize=1)
def _configured_grid_factor() -> float:
    return grid_emission_factor_g_per_kwh(load_config("fuels.yaml"))


@dataclass(frozen=True)
class BerthResult:
    use_shore_power: bool
    energy_kwh: float
    fuel_kg: float = 0.0
    fuel_cost_usd: float = 0.0
    carbon_cost_usd: float = 0.0
    electricity_cost_usd: float = 0.0
    wtt_ghg_t: float = 0.0
    ttw_ghg_t: float = 0.0
    methane_slip_t: float = 0.0
    fuel_wtw_ghg_t: float = 0.0
    grid_ghg_t: float = 0.0

    @property
    def cost_usd(self) -> float:
        return self.fuel_cost_usd + self.carbon_cost_usd + self.electricity_cost_usd

    @property
    def ghg_t(self) -> float:
        return self.fuel_wtw_ghg_t + self.grid_ghg_t

    @property
    def source(self) -> str:
        if self.energy_kwh <= 0.0:
            return "NONE"
        return "SHORE POWER" if self.use_shore_power else "ONBOARD GENERATION"


def berth_accounting(hotel_load_kw: float, port_hours: float, fuel_type: str, use_shore_power: bool,
                     emissions_engine, cost_engine, grid_factor_g_per_kwh: float) -> BerthResult:
    """Exactly one of the two berth cases; zero when there is no berth time or no hotel load."""
    kwh = max(0.0, float(hotel_load_kw)) * max(0.0, float(port_hours))
    if kwh <= 0.0:
        return BerthResult(use_shore_power=use_shore_power, energy_kwh=0.0)
    if use_shore_power:
        return BerthResult(
            use_shore_power=True, energy_kwh=kwh,
            electricity_cost_usd=kwh * cost_engine.shore_power_tariff_usd_kwh + cost_engine.shore_power_connect_fee_usd,
            grid_ghg_t=kwh * grid_factor_g_per_kwh / 1e6,
        )
    fuel_kg = emissions_engine.convert_fuel_mass_for_pathway(
        baseline_vlsfo_kg=kwh * SFOC_KG_VLSFO_PER_KWH, target_fuel_type=fuel_type)
    em = emissions_engine.compute_leg_emissions(fuel_mass_kg=fuel_kg, fuel_type=fuel_type)
    c = cost_engine.compute_leg_costs(fuel_mass_tonnes=fuel_kg / 1000.0, fuel_type=fuel_type,
                                      ttw_co2_tonnes=em["ttw_co2_tonnes"],
                                      voyage_duration_hours=0.0, schedule_deadline_hours=0.0)
    return BerthResult(
        use_shore_power=False, energy_kwh=kwh, fuel_kg=fuel_kg,
        fuel_cost_usd=c["fuel_cost_usd"], carbon_cost_usd=c["carbon_cost_usd"],
        wtt_ghg_t=em["wtt_tonnes_co2e"], ttw_ghg_t=em["ttw_total_tonnes_co2e"],
        methane_slip_t=em["methane_slip_tonnes_co2e"], fuel_wtw_ghg_t=em["wtw_total_tonnes_co2e"],
    )
