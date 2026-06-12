# BTC Multi-Agent Research System

A LangGraph-powered multi-agent system that produces a structured 7-day BTC price forecast. Four data nodes gather news, technical, on-chain, and macro signals in parallel; a synthesis node asks Claude to produce the forecast; a deterministic evaluator scores signal agreement; low-confidence forecasts route to a human-review stub.

## Architecture

```
START ─┬─→ news ─────┐
       ├─→ technical ─┤
       ├─→ onchain ───┼─→ synthesis ─→ evaluate ─→ (router) ─┬─→ review ─→ END
       └─→ macro ─────┘                                       └─────────→ END
```

The four data nodes fan out from `START` and fan in at `synthesis` (run in parallel). See `architecture.md` for full per-node schemas and design rationale, and `CLAUDE.md` for development notes.

## Data Sources

| Node | Domain | Source |
|------|--------|--------|
| `news_sentiment.py` | Headline sentiment, themes | CoinDesk RSS + Claude (`tool_use`) |
| `technical_analysis.py` | RSI, EMA, VWAP | CoinGecko 30d price/volume |
| `onchain_data.py` | Active addresses, exchange flows | CoinMetrics community API |
| `macro_context.py` | Fear & Greed, S&P 500 7d change, BTC 30d change | alternative.me, Yahoo Finance, CoinGecko |

## Output Schema

```json
{
  "asset": "BTC",
  "prediction_horizon": "7 days",
  "direction": "bullish | bearish | neutral",
  "confidence": 0.0,
  "price_target_range": {
    "low": 0,
    "high": 0
  },
  "key_drivers": ["..."],
  "risk_factors": ["..."],
  "recommendation": "buy | sell | monitor",
  "escalate_to_human": false
}
```

If `confidence` falls below `0.60`, `escalate_to_human` is set to `true` by deterministic threshold logic — not by Claude's self-report.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```
`LANGSMITH_API_KEY` (and related `LANGSMITH_*`/`LANGCHAIN_*` vars) are optional — without them, the graph still runs but `eval_score`/`eval_flags` will be missing from the result.

## Running

One-shot CLI run from the project root, streaming each node's output as it completes:
```bash
python graph/graph.py
```

As a FastAPI service (run from inside `graph/` — see the Import Layout note in `CLAUDE.md`):
```bash
cd graph
uvicorn api:app --reload
```
- `GET /health`
- `POST /forecast` — body `{"target_asset": "BTC", "time_horizon_days": 7}` → `{"forecast": {...}, "eval_score": float, "eval_flags": [...]}`. Runs the full graph synchronously (multiple external API calls + 2 Claude calls), so a single request takes 10-30s+.

## APIs Used

All data-source APIs are keyless.

- [CoinDesk RSS](https://www.coindesk.com/arc/outboundfeeds/rss/) — news headlines
- [CoinGecko](https://www.coingecko.com/en/api) — price/volume data
- [CoinMetrics](https://docs.coinmetrics.io/api/v4) — on-chain metrics
- [alternative.me](https://alternative.me/crypto/fear-and-greed-index/) — Fear & Greed Index
- [Yahoo Finance](https://pypi.org/project/yfinance/) — S&P 500 data
- [Anthropic](https://docs.anthropic.com) — Claude API for sentiment scoring and synthesis
- [LangSmith](https://docs.smith.langchain.com) — optional tracing and eval feedback
