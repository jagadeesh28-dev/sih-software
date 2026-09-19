"""
Fleet Operational Cost (OPEX) Engine.
Implements transparent cost accounting for:
- Bunker fuel purchases (VLSFO, LNG, Bio-methanol, Ammonia, Hydrogen)
- Carbon allowance costs (EU ETS Directive 2023/959 / Global Carbon Levy)
- Shore power cold ironing electricity and connection fees
- Schedule demurrage penalty costs
- FuelEU statutory deficit penalties
"""

from typing import Any, Dict, Optional
from lca.fuel_registry import FuelPathwayRegistry


class FleetCostEngine:
    """
    Computes total operational expenditure (OPEX) with itemized breakdown.
    """

    def __init__(
        self,
        registry: Optional[FuelPathwayRegistry] = None,
        carbon_price_usd_tonne: float = 90.0,
        demurrage_rate_usd_hour: float = 1000.0,
        shore_power_tariff_usd_kwh: float = 0.18,
        shore_power_connect_fee_usd: float = 500.0,
        ets_scope: float = 1.0,
        bunker_prices_usd_tonne: Optional[Dict[str, float]] = None,
    ):
        self.registry = registry or FuelPathwayRegistry()
        self.carbon_price_usd_tonne = carbon_price_usd_tonne
        self.demurrage_rate_usd_hour = demurrage_rate_usd_hour
        self.shore_power_tariff_usd_kwh = shore_power_tariff_usd_kwh
        self.shore_power_connect_fee_usd = shore_power_connect_fee_usd
        self.ets_scope = ets_scope
        self.bunker_prices_usd_tonne = bunker_prices_usd_tonne or {}

    def compute_leg_costs(
        self,
        fuel_mass_tonnes: float,
        fuel_type: str,
        ttw_co2_tonnes: float,
        voyage_duration_hours: float,
        schedule_deadline_hours: float,
        use_shore_power: bool = False,
        port_hours: float = 0.0,
        hotel_load_kw: float = 0.0,
        fueleu_penalty_usd: float = 0.0,
    ) -> Dict[str, float]:
        """
        Compute transparent itemized costs for a voyage leg.
        """
        # 1. Bunker Fuel Cost
        pathway = self.registry.get_pathway(fuel_type)
        default_price = pathway.get("price_usd_per_tonne", 620.0)
        fuel_price_usd_per_tonne = self.bunker_prices_usd_tonne.get(fuel_type.lower(), default_price)
        fuel_cost = fuel_mass_tonnes * fuel_price_usd_per_tonne

        # 2. Carbon Allowance / Tax Cost (EU ETS basis on direct combustion CO2)
        carbon_cost = ttw_co2_tonnes * self.ets_scope * self.carbon_price_usd_tonne

        # 3. Shore Power (Cold Ironing) at berth
        if use_shore_power and port_hours > 0.0 and hotel_load_kw > 0.0:
            kwh_consumed = hotel_load_kw * port_hours
            shore_power_cost = (kwh_consumed * self.shore_power_tariff_usd_kwh) + self.shore_power_connect_fee_usd
        else:
            shore_power_cost = 0.0

        # 4. Schedule Delay / Demurrage Penalty
        delay_hours = max(0.0, voyage_duration_hours - schedule_deadline_hours)
        schedule_penalty_cost = delay_hours * self.demurrage_rate_usd_hour

        # 5. Total OPEX
        total_opex = (
            fuel_cost
            + carbon_cost
            + shore_power_cost
            + schedule_penalty_cost
            + fueleu_penalty_usd
        )

        return {
            "fuel_cost_usd": round(fuel_cost, 2),
            "carbon_cost_usd": round(carbon_cost, 2),
            "shore_power_cost_usd": round(shore_power_cost, 2),
            "schedule_penalty_cost_usd": round(schedule_penalty_cost, 2),
            "fueleu_penalty_usd": round(fueleu_penalty_usd, 2),
            "total_opex_usd": round(total_opex, 2),
            "delay_hours": round(delay_hours, 2),
        }
