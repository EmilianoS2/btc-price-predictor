from typing import TypedDict


class BTCResearchState(TypedDict):
    # Inputs — filled before the graph runs
    target_asset: str
    time_horizon_days: int

    # Output slots — each data node fills its own
    news_signals: dict
    technical_signals: dict
    onchain_signals: dict
    macro_signals: dict

    # Synthesis output
    forecast: dict

    # Evals
    eval_score: float
    eval_flags: list
