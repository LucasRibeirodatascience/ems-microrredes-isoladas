from __future__ import annotations

from typing import Callable, Mapping

from .components import BatteryState, MicrogridConfig


class RuleBasedStrategy:
    """M1: current-state rule-based dispatch."""

    name = "M1"

    def reserve_soc(self, row: Mapping[str, float], state: BatteryState, config: MicrogridConfig) -> float:
        return config.battery_min_soc


class ForecastAwareStrategy(RuleBasedStrategy):
    """M2: raises the battery reserve when the solar forecast is low."""

    name = "M2"

    def __init__(self, low_forecast_kw: float = 100.0, reserve_soc_when_low: float = 0.35) -> None:
        self.low_forecast_kw = low_forecast_kw
        self.reserve_soc_when_low = reserve_soc_when_low

    def reserve_soc(self, row: Mapping[str, float], state: BatteryState, config: MicrogridConfig) -> float:
        forecast = float(row.get("pv_forecast_kw", row.get("pv_kw", 0.0)))
        if forecast < self.low_forecast_kw:
            return max(config.battery_min_soc, self.reserve_soc_when_low)
        return config.battery_min_soc


class RLPolicyStrategy(RuleBasedStrategy):
    """M3: public adapter for an external reinforcement-learning policy.

    The policy must return a float in [-1, 1], where negative values prioritize
    charging and positive values prioritize discharging. A trained private model
    is intentionally not included in this public repository.
    """

    name = "M3"

    def __init__(self, policy: Callable[[Mapping[str, float], BatteryState], float] | None = None) -> None:
        self.policy = policy

    def action(self, row: Mapping[str, float], state: BatteryState) -> float:
        if self.policy is None:
            return 0.0
        return max(-1.0, min(1.0, float(self.policy(row, state))))
