from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .components import MicrogridConfig
from .metrics import summarize
from .simulator import simulate
from .strategies import ForecastAwareStrategy, RLPolicyStrategy, RuleBasedStrategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simula estrategias EMS para microrredes PV/BESS/Diesel.")
    parser.add_argument("--data", required=True, help="CSV horario com timestamp, load_kw e pv_kw.")
    parser.add_argument("--strategy", choices=["m1", "m2", "m3"], default="m1")
    parser.add_argument("--output", default="reports/results.csv", help="Arquivo CSV de saida.")
    return parser


def build_strategy(name: str):
    if name == "m1":
        return RuleBasedStrategy()
    if name == "m2":
        return ForecastAwareStrategy()
    return RLPolicyStrategy()


def main() -> None:
    args = build_parser().parse_args()
    data = pd.read_csv(args.data)
    config = MicrogridConfig()
    strategy = build_strategy(args.strategy)

    results = simulate(data, config, strategy)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)

    summary = summarize(results, config)
    summary_path = output_path.with_name(output_path.stem + "_summary.csv")
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    print(pd.DataFrame([summary]).to_string(index=False))
    print(f"Resultados salvos em: {output_path}")
    print(f"Resumo salvo em: {summary_path}")


if __name__ == "__main__":
    main()
