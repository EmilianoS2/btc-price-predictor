# Architecture — BTC Multi-Agent Research System

> **Status legend:** ✅ built and running · 🔜 planned (in this doc, not yet in code)

## System Overview

A LangGraph `StateGraph` runs seven nodes over one shared state object. Four **data nodes** fetch signal domains in parallel and each write their own slice; a **synthesis node** reads all four and produces the forecast; an **evaluator node** scores that forecast; a **conditional router** sends low-confidence forecasts to a **human-review** node, everything else to `END`. Nodes never call each other — they read from and write to the shared state, and LangGraph merges each node's returned slice.

Execution path:
```
START ─┬─→ news ─────┐
       ├─→ technical ─┤
       ├─→ onchain ───┼─→ synthesis ─→ evaluate ─→ (router) ─┬─→ review ─→ END
       └─→ macro ─────┘                                       └─────────→ END
```

---

## State Object  ✅

One shared `BTCResearchState` (`graph/state.py`). Each node returns only its own slot; LangGraph merges it in.

```python
class BTCResearchState(TypedDict):
    # Inputs — set before the graph runs
    target_asset: str               # e.g. "BTC"
    time_horizon_days: int          # e.g. 7

    # Data-node outputs (one slot each)
    news_signals: dict
    technical_signals: dict
    onchain_signals: dict
    macro_signals: dict

    # Synthesis output
    forecast: dict

    # Evaluator output
    eval_score: float               # 0.0–1.0 signal-agreement score
    eval_flags: list                # human-readable warnings
```

Nodes live in `graph/nodes.py` as thin wrappers; the worker functions that do the real fetching live as flat modules in the project root. The evaluator's logic lives in `graph/eval.py`.

---

## Nodes

### 1. News Node  ✅
**Worker:** `news_sentiment.collect_news_sentiment`
**Source:** CoinDesk RSS feed via `feedparser`, then Claude (`tool_use`) for sentiment scoring.
**Writes:** `news_signals`
```python
news_signals = {
    "headline_count": int,
    "sentiment_score": float,        # -1.0 to 1.0
    "sentiment_label": "bullish" | "bearish" | "neutral",
    "top_themes": list[str]
}
```

### 2. Technical Node  ✅
**Worker:** `technical_analysis.analyze_indicators`
**Source:** CoinGecko 30d price/volume → pandas + the `ta` library.
**Writes:** `technical_signals`
```python
technical_signals = {"rsi": float, "ema": float, "vwap": float}   # 14-period RSI/EMA
```
**Design note:** indicators are computed deterministically in Python. Claude interprets them at synthesis — it does not compute them.

### 3. On-Chain Node  ✅
**Worker:** `onchain_data.fetch_onchain_metrics`
**Source:** CoinMetrics community API (`AdrActCnt`, `FlowInExNtv`, `FlowOutExNtv`).
**Writes:** `onchain_signals`
```python
onchain_signals = {
    "active_addresses": int,
    "exchange_inflow_btc": float,
    "exchange_outflow_btc": float,
    "net_exchange_flow_btc": float   # outflow - inflow; negative = net outflow
}
```

### 4. Macro Node  ✅
**Worker:** `macro_context.collect_macro_context`
**Sources:** `yfinance` (S&P 500, `^GSPC`), alternative.me (Fear & Greed), CoinGecko (BTC 30d price).
**Writes:** `macro_signals`
```python
macro_signals = {
    "fear_greed_index": int, "fear_greed_label": str,
    "sp500_7d_change_pct": float,
    "btc_price_usd": float, "btc_30d_change_pct": float
}
```

### 5. Synthesis Node (`aggregate_node`)  ✅
**Worker:** `synthesis.run_synthesis`
**Source:** Claude (`claude-haiku-4-5-20251001`) via `tool_use`.
**Reads:** the whole state. **Writes:** `forecast`
```python
forecast = {
    "asset": str, "prediction_horizon": str,
    "direction": "bullish" | "bearish" | "neutral",
    "confidence": float,                       # 0.0–1.0
    "price_target_range": {"low": float, "high": float},
    "key_drivers": list[str], "risk_factors": list[str],
    "recommendation": "buy" | "sell" | "monitor",
    "escalate_to_human": bool
}
```
- **Structured output** is enforced by a `tool_use` JSON schema (forced `tool_choice`), not by prompting for JSON. Output is checked by `validate_synthesis_output`.
- **Escalation is deterministic:** `apply_escalation` sets `escalate_to_human = True` when `confidence <= 0.60`. The model does not decide it.

### 6. Evaluator Node (`evaluator_node`)  ✅
**Worker:** `graph/eval.py` `evaluator(state)`. **Reads:** all four signals + `forecast`. **Writes:** `eval_score`, `eval_flags`.

A **deterministic** quality pass (no Claude call — same philosophy as `apply_escalation`). It does not modify the forecast; it only scores and flags it. Separation of generation and evaluation is intentional.

- **Coverage check first.** If any signal slot is missing/empty, it bails early with `eval_score = 0.0` and a flag per missing signal (so the voting code never touches absent data).
- **Agreement score.** Reduces each signal to a bullish/bearish vote, then `eval_score = max(bullish, bearish) / total_votes`. This measures *consensus* (how aligned the signals are), independent of direction — a unanimous bearish read scores 1.0.
- **Low-agreement flag** appended when `eval_score < 0.60`.

```python
eval_score: float          # 1.0 = unanimous, 0.5 = even split, 0.0 = degraded (missing signal)
eval_flags: list[str]      # e.g. "onchain_signals missing — forecast ran without it"
                           #      "Low signal agreement (57%) — signals contradict, treat with caution"
```

### 7. Human-Review Node (`human_review_node`)  ✅ (stub)
The escalation branch. Reached only when the router sends the token here. Currently a placeholder (`return {}`) — the hook exists, but no notification/logging is wired yet.

---

## Routing  ✅

`router_node` is a **conditional-edge function** (not a node) — it reads state and returns the next destination:

```python
def router_node(state):
    if state['forecast']['escalate_to_human']:
        return "review"
    return END
```

Wired so the evaluator always runs on the main path, and routing happens after it:
```python
graph.add_edge("synthesis", "evaluate")
graph.add_conditional_edges("evaluate", router_node, {"review": "review", END: END})
```

---

## Graph Definition  ✅

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(BTCResearchState)
for name, fn in [("news", news_node), ("macro", macro_node), ("onchain", onchain_node),
                 ("technical", technical_node), ("synthesis", aggregate_node),
                 ("evaluate", evaluator_node), ("review", human_review_node)]:
    graph.add_node(name, fn)

# fan out the four data nodes in parallel
for n in ["news", "onchain", "technical", "macro"]:
    graph.add_edge(START, n)

# fan in: synthesis waits for all four (list-as-source = barrier)
graph.add_edge(["news", "macro", "onchain", "technical"], "synthesis")
graph.add_edge("synthesis", "evaluate")
graph.add_conditional_edges("evaluate", router_node, {"review": "review", END: END})

app = graph.compile()
```

**Parallelism note:** the four data nodes are independent, so they fan out from `START` and fan in at `synthesis`. Measured ~31% faster than the sequential version; the floor is the slowest single node plus synthesis (both on the critical path).

**Watching it run:** `app.stream(start)` yields one chunk per node as it finishes, instead of only the final state from `app.invoke(start)`.

---

## Implementation Notes

### FastAPI Layer  ✅
The graph is exposed as a REST API in `graph/api.py`: `GET /health` and `POST /forecast`, which maps a request body (`target_asset`, `time_horizon_days`) to `app.invoke(...)` and returns `forecast` + `eval_score` + `eval_flags`.

### Observability  ✅
`evaluator_node` is `@traceable` and calls `client.create_feedback(key="eval_score", ...)` on the current run, attaching `eval_score` to the LangSmith trace. Set `LANGSMITH_API_KEY` (+ related `LANGSMITH_*`/`LANGCHAIN_*` vars) to enable; if unset, the node's try/except swallows the error and `eval_score`/`eval_flags` are simply absent from the result.

### Graceful Degradation  ✅
Every data node (`news`, `macro`, `onchain`, `technical`, `synthesis`) wraps its worker call in try/except and returns an empty dict for its slot on failure, so one failing source degrades the run instead of crashing it. The evaluator's coverage check then flags any missing slot.

---

## Key Design Decisions

**Why LangGraph over hand-wired calls?** The shared state makes data flow inspectable, and the framework merges each node's output and runs independent nodes in parallel for free. The old `coordinator.py` did this merge by hand; it's gone.

**Why does Claude interpret but not compute indicators?** Determinism. RSI is a fact computed in Python; whether it's "oversold here" is interpretation, done by Claude at synthesis. Separate layers, separately testable.

**Why `tool_use` instead of prompting for JSON?** A forced tool schema guarantees output shape. "Return JSON" is probabilistic; a schema is structural.

**Why are escalation and evaluation deterministic, not Claude-judged?** A confidence threshold and a signal-agreement count are rules. Letting the model self-report quality or whether to escalate invites drift. `apply_escalation` and `evaluator` keep those rules explicit, cheap, and testable.

**Why separate the evaluator node from the human-review node?** The evaluator scores *every* forecast (main path); human-review is the *rare* escalation branch. They are different jobs — merging them would mean the evaluator only runs when escalation fires.
