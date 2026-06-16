from __future__ import annotations

import pandas as pd

from .components import MicrogridConfig


def summarize(results: pd.DataFrame, config: MicrogridConfig) -> dict[str, float]:
    generator_on = results["diesel_kw"] > 0
    generator_startups = int((generator_on & ~generator_on.shift(fill_value=False)).sum())
    generator_hours = float(generator_on.sum())
    diesel_energy_kwh = float(results["diesel_kw"].sum())

    fuel_liters = float(
        (generator_on * config.fuel_intercept_lph + results["diesel_kw"] * config.fuel_slope_l_per_kwh).sum()
    )

    optimal_operation = generator_on & (
        results["diesel_kw"].between(config.diesel_optimal_min_kw, config.diesel_optimal_max_kw)
    )
    optimal_operation_pct = float(optimal_operation.sum() / generator_hours * 100.0) if generator_hours else 0.0

    return {
        "fuel_liters": fuel_liters,
        "diesel_energy_kwh": diesel_energy_kwh,
        "generator_startups": float(generator_startups),
        "generator_hours": generator_hours,
        "curtailment_kwh": float(results["curtailment_kw"].sum()),
        "unmet_load_kwh": float(results["unmet_load_kw"].sum()),
        "optimal_operation_pct": optimal_operation_pct,
        "soc_mean": float(results["soc"].mean()),
        "soc_min": float(results["soc"].min()),
        "soc_max": float(results["soc"].max()),
    }
