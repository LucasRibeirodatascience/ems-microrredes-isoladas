from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from .components import BatteryState, DispatchDecision, MicrogridConfig
from .strategies import RLPolicyStrategy, RuleBasedStrategy


def _available_discharge_kw(state: BatteryState, config: MicrogridConfig, reserve_soc: float) -> float:
    available_kwh = max(0.0, (state.soc - reserve_soc) * config.battery_capacity_kwh)
    return min(config.battery_max_discharge_kw, available_kwh * config.battery_discharge_efficiency)


def _available_charge_kw(state: BatteryState, config: MicrogridConfig) -> float:
    available_kwh = max(0.0, (config.battery_max_soc - state.soc) * config.battery_capacity_kwh)
    return min(config.battery_max_charge_kw, available_kwh / config.battery_charge_efficiency)


def _update_soc(
    state: BatteryState,
    charge_kw: float,
    discharge_kw: float,
    config: MicrogridConfig,
) -> BatteryState:
    charged_kwh = charge_kw * config.battery_charge_efficiency
    discharged_kwh = discharge_kw / config.battery_discharge_efficiency
    next_soc = state.soc + (charged_kwh - discharged_kwh) / config.battery_capacity_kwh
    next_soc = max(config.battery_min_soc, min(config.battery_max_soc, next_soc))
    return BatteryState(soc=next_soc)


def dispatch_step(
    row: Mapping[str, float],
    state: BatteryState,
    config: MicrogridConfig,
    strategy: RuleBasedStrategy,
) -> tuple[DispatchDecision, BatteryState]:
    load_kw = max(0.0, float(row["load_kw"]))
    pv_kw = max(0.0, float(row["pv_kw"]))
    pv_to_load_kw = min(load_kw, pv_kw)
    surplus_kw = max(0.0, pv_kw - load_kw)
    deficit_kw = max(0.0, load_kw - pv_kw)

    reserve_soc = strategy.reserve_soc(row, state, config)
    battery_charge_kw = 0.0
    battery_discharge_kw = 0.0

    if surplus_kw > 0:
        battery_charge_kw = min(surplus_kw, _available_charge_kw(state, config))
    elif deficit_kw > 0:
        max_discharge = _available_discharge_kw(state, config, reserve_soc)
        battery_discharge_kw = min(deficit_kw, max_discharge)

    if isinstance(strategy, RLPolicyStrategy):
        action = strategy.action(row, state)
        if action > 0 and deficit_kw > 0:
            battery_discharge_kw = min(deficit_kw, _available_discharge_kw(state, config, config.battery_min_soc) * action)
        elif action < 0 and surplus_kw > 0:
            battery_charge_kw = min(surplus_kw, _available_charge_kw(state, config) * abs(action))

    remaining_deficit_kw = max(0.0, deficit_kw - battery_discharge_kw)
    diesel_kw = 0.0
    unmet_load_kw = 0.0

    if remaining_deficit_kw > 0:
        diesel_kw = min(config.diesel_max_kw, max(config.diesel_min_kw, remaining_deficit_kw))
        unmet_load_kw = max(0.0, remaining_deficit_kw - diesel_kw)

    curtailment_kw = max(0.0, surplus_kw - battery_charge_kw)
    next_state = _update_soc(state, battery_charge_kw, battery_discharge_kw, config)

    decision = DispatchDecision(
        pv_to_load_kw=pv_to_load_kw,
        battery_charge_kw=battery_charge_kw,
        battery_discharge_kw=battery_discharge_kw,
        diesel_kw=diesel_kw,
        curtailment_kw=curtailment_kw,
        unmet_load_kw=unmet_load_kw,
        soc=next_state.soc,
    )
    return decision, next_state


def simulate(data: pd.DataFrame, config: MicrogridConfig, strategy: RuleBasedStrategy) -> pd.DataFrame:
    required_columns = {"timestamp", "load_kw", "pv_kw"}
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {', '.join(sorted(missing))}")

    state = BatteryState(soc=config.battery_initial_soc)
    rows: list[dict[str, float | str]] = []

    for _, raw_row in data.iterrows():
        row = raw_row.to_dict()
        decision, state = dispatch_step(row, state, config, strategy)
        rows.append(
            {
                "timestamp": row["timestamp"],
                "strategy": strategy.name,
                "load_kw": row["load_kw"],
                "pv_kw": row["pv_kw"],
                "pv_to_load_kw": decision.pv_to_load_kw,
                "battery_charge_kw": decision.battery_charge_kw,
                "battery_discharge_kw": decision.battery_discharge_kw,
                "diesel_kw": decision.diesel_kw,
                "curtailment_kw": decision.curtailment_kw,
                "unmet_load_kw": decision.unmet_load_kw,
                "soc": decision.soc,
            }
        )

    return pd.DataFrame(rows)
