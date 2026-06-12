# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A LangGraph-powered multi-agent system that produces a structured 7-day BTC price forecast. Four independent data nodes gather news, technical, on-chain, and macro signals onto a shared state object; a synthesis node asks Claude to produce the final forecast; a deterministic evaluator scores signal agreement; low-confidence forecasts route to a human-review stub. The graph is runnable as a one-shot CLI script or as a FastAPI service.

## Architecture

`graph/graph.py` builds a LangGraph `StateGraph(BTCResearchState)` with 7 nodes:

```
START ─┬─→ news ─────┐
       ├─→ technical ─┤
       ├─→ onchain ───┼─→ synthesis ─→ evaluate ─→ (router) ─┬─→ review ─→ END
       └─→ macro ─────┘                                       └─────────→ END
```

- **`news_node`** — CoinDesk RSS headlines → Claude (`tool_use`) sentiment score
- **`technical_node`** — RSI/EMA/VWAP from 30d CoinGecko price+volume via pandas + `ta`
- **`onchain_node`** — active addresses + exchange in/out flows (CoinMetrics community API)
- **`macro_node`** — S&P 500 7d change (`yfinance`), Fear & Greed index (alternative.me), BTC 30d change (CoinGecko)
- **`aggregate_node`** (synthesis) — reads all 4 signal slots, calls Claude with a forced `tool_use` schema to produce `forecast`. `apply_escalation` in `synthesis.py` deterministically sets `forecast.escalate_to_human = True` when `confidence <= 0.60` — the model does not decide this.
- **`evaluator_node`** — runs `graph/eval.py`'s `evaluator()`: reduces each signal domain to a bullish/bearish vote and computes `eval_score` (signal agreement, 0-1) + `eval_flags`. Also `@traceable` and logs `eval_score` to LangSmith via `client.create_feedback(...)`.
- **`human_review_node`** — stub (`return {}`), reached only when escalated.
- **`router_node`** — a conditional-edge function (not a graph node): sends to `review` if `forecast["escalate_to_human"]`, else `END`.

The four data nodes fan out from `START` and fan in at `synthesis` (run in parallel). Node wrappers live in `graph/nodes.py`; each calls a worker function from a flat module in the project root (`news_sentiment.py`, `technical_analysis.py`, `onchain_data.py`, `macro_context.py`, `synthesis.py`) and writes only its own state slot — workers themselves are framework-agnostic and untouched by LangGraph concerns.

**Error-handling pattern**: every node wraps its worker call in `try/except` and returns an empty dict (`{}`) for its slot on failure, so one failing data source degrades the run instead of crashing the whole graph. `evaluator_node`'s coverage check then flags any missing slot (e.g. `"news_signals missing — forecast ran without it"`).

For full per-node output schemas and design rationale (why `tool_use` over prompted JSON, why escalation/evaluation are deterministic, etc.), see `architecture.md`.

## Running

One-shot CLI run from the project root — streams each node's output chunk as it completes:
```bash
python graph/graph.py
```

As a service (see Import Layout gotcha below for why you must `cd graph` first):
```bash
cd graph
uvicorn api:app --reload
```
- `GET /health`
- `POST /forecast` — body `{"target_asset": "BTC", "time_horizon_days": 7}` → `{"forecast": {...}, "eval_score": float, "eval_flags": [...]}`. This synchronously runs the full graph (multiple external API calls + 2 Claude calls), so a single request takes 10-30s+.

## Setup

```bash
pip install -r requirements.txt
```

`.env` in the project root:

| Variable | Required for |
|---|---|
| `ANTHROPIC_API_KEY` | News sentiment + synthesis Claude calls (`claude-haiku-4-5-20251001` via forced `tool_use`) |
| `LANGSMITH_API_KEY` (and related `LANGSMITH_*`/`LANGCHAIN_*` vars) | `evaluator_node`'s `client.create_feedback(...)` call in `graph/nodes.py`. If unset/invalid, that node's `try/except` swallows the error and `eval_score`/`eval_flags` will be missing from the result state. |

All data-source APIs (CoinDesk RSS, CoinGecko, CoinMetrics, alternative.me, yfinance) are keyless.

## State Object (`graph/state.py`)

`BTCResearchState` is a `TypedDict`. Every node reads the whole shared state but returns only its own slot(s); LangGraph merges them in:
- Inputs: `target_asset`, `time_horizon_days`
- Data slots: `news_signals`, `technical_signals`, `onchain_signals`, `macro_signals`
- `forecast` — synthesis output (schema below)
- `eval_score`, `eval_flags` — evaluator output

## Forecast Output Schema

```json
{
  "asset": "BTC",
  "prediction_horizon": "7 days",
  "direction": "bullish | bearish | neutral",
  "confidence": 0.0,
  "price_target_range": { "low": 0, "high": 0 },
  "key_drivers": ["..."],
  "risk_factors": ["..."],
  "recommendation": "buy | sell | monitor",
  "escalate_to_human": false
}
```
Shape is enforced by a forced `tool_use` schema plus `validate_synthesis_output` (assertions) in `synthesis.py` — not by prompting for JSON.

## Import Layout (gotcha)

`graph/*.py` use bare imports (`from nodes import ...`, `from state import BTCResearchState`, `from graph import app`) that only resolve when `graph/` itself is on `sys.path`:
- `python graph/graph.py` works from the project root because Python adds the *script's own* directory to `sys.path[0]`.
- `graph/api.py` does `from graph import app` — run uvicorn **from inside `graph/`** (`cd graph && uvicorn api:app`). Running `uvicorn graph.api:app` from the project root treats `graph` as a package and breaks this import.
- `graph/nodes.py` additionally appends the project root to `sys.path` so it can import the root-level worker modules (`news_sentiment`, `macro_context`, etc.).
- `graph/graph.py`'s module-level `app = graph.compile()` is safe to import as a library; the CLI demo loop (`app.stream(...)`) is gated behind `if __name__ == "__main__":`.
