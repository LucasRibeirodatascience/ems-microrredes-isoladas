from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MicrogridConfig:
    battery_capacity_kwh: float = 2000.0
    battery_initial_soc: float = 0.55
    battery_min_soc: float = 0.15
    battery_max_soc: float = 0.95
    battery_charge_efficiency: float = 0.95
    battery_discharge_efficiency: float = 0.95
    battery_max_charge_kw: float = 500.0
    battery_max_discharge_kw: float = 500.0
    diesel_min_kw: float = 80.0
    diesel_max_kw: float = 600.0
    diesel_optimal_min_kw: float = 240.0
    diesel_optimal_max_kw: float = 480.0
    fuel_intercept_lph: float = 8.0
    fuel_slope_l_per_kwh: float = 0.24


@dataclass
class BatteryState:
    soc: float

    @property
    def energy_fraction(self) -> float:
        return self.soc


@dataclass(frozen=True)
class DispatchDecision:
    pv_to_load_kw: float
    battery_charge_kw: float
    battery_discharge_kw: float
    diesel_kw: float
    curtailment_kw: float
    unmet_load_kw: float
    soc: float
