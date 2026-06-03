# BTC Multi-Agent Research System

## Project Overview
A LangGraph-powered system that produces a structured 7-day BTC price forecast. Four data nodes gather news, technical, on-chain, and macro signals onto a shared state object; a synthesis node reads all four and asks Claude to produce the final forecast.

## Architecture
A LangGraph `StateGraph` runs five nodes over a shared `BTCResearchState`:
- `news_node` — CoinDesk RSS headlines → Claude sentiment score
- `technical_node` — RSI, EMA, VWAP from 30d price/volume
- `onchain_node` — active addresses + exchange in/out flows
- `macro_node` — S&P 500 7d change, Fear & Greed index, BTC 30d change
- `aggregate_node` — reads all four signal slots, calls Claude with `tool_use` to write the final forecast

Execution path: `news → onchain → technical → macro → synthesis → END`. The four data nodes are independent and could later run in parallel (LangGraph `Send` / fan-out).

Node wrappers live in `graph/nodes.py`; the worker functions that do the actual fetching live as flat modules in the project root and are called by the nodes.

## Stack
- Python 3.11+
- LangGraph — `StateGraph` orchestration and shared state
- Claude API (`claude-haiku-4-5-20251001`) — sentiment scoring and synthesis, via `tool_use` (structured JSON enforced by schema, not by prompt)
- pandas + `ta` — deterministic indicator computation (Claude interprets, it does not compute)
- Data sources (all keyless): CoinDesk RSS via `feedparser`, CoinGecko (price/volume), CoinMetrics community API (on-chain), alternative.me (Fear & Greed), `yfinance` (S&P 500)

## Running the System
```bash
pip install langgraph anthropic feedparser yfinance ta pandas requests python-dotenv
# add ANTHROPIC_API_KEY to .env
python graph/graph.py
```
(No `requirements.txt` yet — pin the packages above when you add one.)

## Output
The `forecast` slot returns a `tool_use` object:
```json
{
  "asset": "BTC",
  "prediction_horizon": "7 days",
  "direction": "bearish",
  "confidence": 0.72,
  "price_target_range": { "low": 64000, "high": 70500 },
  "key_drivers": ["..."],
  "risk_factors": ["..."],
  "recommendation": "monitor",
  "escalate_to_human": false
}
```
`escalate_to_human` is set **deterministically in code** (`apply_escalation` in `synthesis.py`): `True` when confidence ≤ 0.60. The model does not decide escalation.

## Environment Variables
| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key — the only required key; all data sources are keyless |
