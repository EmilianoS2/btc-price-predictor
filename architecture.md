# Architecture — BTC Multi-Agent Research System

## System Overview

The system is a LangGraph `StateGraph`: five nodes operating on one shared state object. Four **data nodes** each fetch a signal domain and write their slice; one **synthesis node** runs last, reads all four slices, and asks Claude to produce the final forecast. Nodes never call each other — they read from and write to the shared state.

---

## State Object

All nodes read from and write to a single `BTCResearchState` (`graph/state.py`). This is the backbone of the system.

```python
class BTCResearchState(TypedDict):
    # Inputs — filled before the graph runs
    target_asset: str               # e.g. "BTC"
    time_horizon_days: int          # e.g. 7

    # Output slots — each data node fills its own
    news_signals: dict
    technical_signals: dict
    onchain_signals: dict
    macro_signals: dict

    # Synthesis output
    forecast: dict
```

Each node returns only its own slot (e.g. `{"news_signals": {...}}`); LangGraph merges it into the shared state. There is no manual assembly step.

---

## Nodes

Node wrappers live in `graph/nodes.py`. Each is a thin doorway that calls a worker function (a flat module in the project root) and labels the result for its slot. The workers do the real fetching and stay independently testable.

### 1. News Node
**Worker:** `news_sentiment.collect_news_sentiment`
**Source:** CoinDesk RSS feed via `feedparser`, then Claude (`tool_use`) for sentiment scoring.
**Writes:** `news_signals`

```python
news_signals = {
    "headline_count": int,
    "sentiment_label": "bullish" | "bearish" | "neutral",
    "sentiment_score": float,        # -1.0 to 1.0
    "top_themes": list[str]
}
```

### 2. Technical Node
**Worker:** `technical_analysis.analyze_indicators`
**Source:** CoinGecko 30d price/volume → pandas + the `ta` library.
**Writes:** `technical_signals`

```python
technical_signals = {
    "rsi": float,        # 14-period RSI
    "ema": float,        # 14-period EMA
    "vwap": float
}
```

**Design note:** Indicators are computed in Python and stay deterministic. Claude interprets them at synthesis time — it does not compute them.

### 3. On-Chain Node
**Worker:** `onchain_data.fetch_onchain_metrics`
**Source:** CoinMetrics community API (`AdrActCnt`, `FlowInExNtv`, `FlowOutExNtv`).
**Writes:** `onchain_signals`

```python
onchain_signals = {
    "active_addresses": int,
    "exchange_inflow_btc": float,
    "exchange_outflow_btc": float,
    "net_exchange_flow_btc": float   # outflow - inflow; negative = net inflow
}
```

### 4. Macro Node
**Worker:** `macro_context.collect_macro_context`
**Sources:** `yfinance` (S&P 500, `^GSPC`), alternative.me (Fear & Greed), CoinGecko (BTC 30d price).
**Writes:** `macro_signals`

```python
macro_signals = {
    "fear_greed_index": int,
    "fear_greed_label": str,
    "sp500_7d_change_pct": float,
    "btc_price_usd": float,
    "btc_30d_change_pct": float
}
```

### 5. Synthesis Node (`aggregate_node`)
**Worker:** `synthesis.run_synthesis`
**Source:** Claude (`claude-haiku-4-5-20251001`) via `tool_use`.
**Reads:** the whole state (all four signal slots). **Writes:** `forecast`

This is the only **consumer** node — it receives the shared state and passes it to `run_synthesis`, which feeds the gathered signals to Claude under a fixed tool schema.

```python
forecast = {
    "asset": str,
    "prediction_horizon": str,
    "direction": "bullish" | "bearish" | "neutral",
    "confidence": float,                       # 0.0 to 1.0
    "price_target_range": {"low": float, "high": float},
    "key_drivers": list[str],
    "risk_factors": list[str],
    "recommendation": "buy" | "sell" | "monitor",
    "escalate_to_human": bool
}
```

**Structured output:** enforced by a `tool_use` JSON schema (`tool_choice` forces the tool), not by asking Claude to "return JSON." Output is validated by `validate_synthesis_output`.

**Deterministic escalation:** `apply_escalation` overrides `escalate_to_human` in code — `True` when confidence ≤ 0.60. The model does not decide it.

---

## Graph Definition

```python
from langgraph.graph import StateGraph, END
from nodes import news_node, macro_node, onchain_node, technical_node, aggregate_node
from state import BTCResearchState

graph = StateGraph(BTCResearchState)
graph.add_node("news", news_node)
graph.add_node("macro", macro_node)
graph.add_node("onchain", onchain_node)
graph.add_node("technical", technical_node)
graph.add_node("synthesis", aggregate_node)

graph.set_entry_point("news")
graph.add_edge("news", "onchain")
graph.add_edge("onchain", "technical")
graph.add_edge("technical", "macro")
graph.add_edge("macro", "synthesis")
graph.add_edge("synthesis", END)

app = graph.compile()
```

**Note on parallelism:** the four data nodes run sequentially today, but they have no dependencies on each other — only synthesis depends on all four. They are the natural candidates for parallel fan-out via LangGraph's `Send` API.

---

## File Structure

```
Stock-Forecast/
├── graph/
│   ├── state.py            # BTCResearchState TypedDict
│   ├── nodes.py            # node wrappers (call workers, label slots)
│   └── graph.py            # StateGraph definition + invoke
├── news_sentiment.py       # worker: CoinDesk RSS + Claude sentiment
├── technical_analysis.py   # worker: CoinGecko + ta indicators
├── onchain_data.py         # worker: CoinMetrics metrics
├── macro_context.py        # worker: yfinance / Fear&Greed / CoinGecko
├── synthesis.py            # worker: Claude tool_use forecast + escalation
├── CLAUDE.md
└── architecture.md
```

---

## Observability

Not yet wired. LangSmith tracing is a planned addition — set `LANGSMITH_API_KEY` and the standard `LANGCHAIN_TRACING_V2` env vars when added. There is currently no tracing in the code.

---

## Key Design Decisions

**Why LangGraph over hand-wired calls?**
The shared state object makes data flow between nodes a first-class, inspectable thing. The old `coordinator.py` assembled a dict by hand and passed it forward; LangGraph does that merge automatically as the graph runs.

**Why does Claude interpret but not compute indicators?**
Determinism. RSI at 18.6 is a fact computed in Python. Whether that's "oversold in this context" is interpretation, done by Claude at synthesis. Keeping computation and interpretation in separate layers makes each independently testable.

**Why `tool_use` instead of prompting for JSON?**
A forced tool schema guarantees the shape of the output. Asking a model to "return JSON" is probabilistic; a schema is structural.

**Why decide escalation in code, not in the prompt?**
A confidence threshold is a deterministic rule. Letting the model self-report whether to escalate invites drift. `apply_escalation` makes the rule explicit and testable.
