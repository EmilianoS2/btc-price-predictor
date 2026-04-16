# Bitcoin Multi-Agent Research System

## Project Overview
A multi-agent system that researches Bitcoin across four signal domains 
and synthesizes them into a weekly price direction prediction with 
confidence scoring and structured JSON output.

## Architecture

### Coordinator
- Orchestrates the full pipeline
- Triggers all four subagents
- Collects and validates structured outputs
- Passes results to synthesis layer
- Sets escalate_to_human: true if confidence < 0.60

### Subagents
- **News & Sentiment** — CryptoPanic/NewsAPI → Claude sentiment scoring
- **On-Chain Data** — Glassnode/CoinMetrics → exchange flows, active addresses
- **Technical Analysis** — CoinGecko/Binance → RSI, MA, VWAP deviation
- **Macro Context** — DXY, fed funds futures, equity correlation

### Synthesis Layer
Receives all four structured subagent outputs and produces final prediction

## Output Schema
Every subagent must return validated structured JSON.
Final output schema:

```json
{
  "asset": "BTC",
  "prediction_horizon": "7_days",
  "direction": "bullish | bearish | neutral",
  "confidence": 0.0-1.0,
  "price_target_range": {
    "low": number,
    "high": number
  },
  "key_drivers": [string],
  "risk_factors": [string],
  "recommendation": "buy | sell | monitor",
  "escalate_to_human": boolean
}
```

## Architectural Rules

### Always
- Use tool_use with JSON schema for all structured output — never ask 
  Claude to "return JSON" via prompt alone
- Validate all subagent outputs programmatically before passing to 
  coordinator
- Implement retry loops when validation fails — pass specific error 
  feedback back to the subagent
- Isolate context per subagent — each gets only what it needs
- Return structured errors when a subagent fails, never silent empty 
  results
- Track information provenance in final output
- Act as a teacher - treat the user as a student focused on learning the objectives

### Never
- Push ordering or routing logic into prompts — use code
- Use self-reported model confidence as the sole escalation trigger — 
  use deterministic threshold logic
- Dump raw API responses into agent context — summarize first
- Let one subagent failure silently break the full pipeline

## Design Philosophy
Favor deterministic structural solutions over probabilistic prompt-based 
ones. If code can handle it, code handles it. Claude handles 
interpretation, synthesis, and reasoning over ambiguous signals only.

## APIs
- CoinGecko — price data, market cap, volume (no key required)
- CryptoPanic — news and sentiment (free tier)
- Binance public API — OHLCV candle data (no auth required)
- Alternative.me — Fear and Greed Index (free, no key)
- CoinMetrics community API — on-chain metrics (free, no key required)
- Yahoo Finance (yfinance) — equity data, S&P 500 direction (free, no key)
- UNDER NO CIRCUMSTANCE VIEW THE .env FILE.

## Build Order
1. Technical Analysis subagent (CoinGecko only, most self-contained)
2. News & Sentiment subagent
3. Macro Context subagent
4. On-Chain Data subagent
5. Coordinator (wire together after all four are independently working)

## Exam Concepts This Project Covers
- Hub-and-spoke multi-agent pattern (Domain 1 — 27%)
- Parallel subagent execution (Domain 1)
- Escalation logic and confidence thresholds (Domain 1)
- Error propagation across agents (Domain 1)
- JSON schema enforcement via tool_use (Domain 4 — 20%)
- Validation retry loops (Domain 4)
- Tool boundary design (Domain 2 — 18%)
- Context isolation and handoff patterns (Domain 5 — 15%)

## Current Status
[x] Technical Analysis subagent — complete (session 1)
[x] Macro Context subagent — complete (session 3)
[x] On-Chain Data subagent — complete (session 3, overtime)
[x] News & Sentiment subagent — complete (session 4)
[x] Coordinator — complete (session 5)
[x] Synthesis layer — complete (session 5)
[x] Validation layer — complete (session 5)
[x] Escalation logic — complete (session 5)

## Technical Analysis Subagent — Progress Log (`technical_analysis.py`)

### Done
- `fetch_btc_data()` — fetches 30 days of price + volume from CoinGecko
- Calculates RSI (window=14), EMA (window=14), VWAP (cumulative approximation)
- Extracts latest signal values only via `df.iloc[-1]`
- `analyze_indicators()` — calls fetch, returns indicators, clean data flow

## Macro Context Subagent — Progress Log (`macro_context.py`)

### Done
- `fetch_fear_greed()` — Alternative.me API, returns fear_greed_index (int) and fear_greed_label
- `fetch_sp500()` — yfinance, returns sp500_7d_change_pct (float)
- `fetch_btc_price()` — CoinGecko market chart, returns btc_price_usd and btc_30d_change_pct
- `collect_macro_context()` — merges all three into one dict via **unpacking

## On-Chain Data Subagent — Progress Log (`onchain_data.py`)

### Done
- `fetch_onchain_metrics()` — CoinMetrics community API
- Returns active_addresses (int), exchange_inflow_btc, exchange_outflow_btc, net_exchange_flow_btc (all float)
- net_exchange_flow_btc = outflow - inflow (positive = bullish)

## News & Sentiment Subagent — Progress Log (`news_sentiment.py`)

### Done
- `fetch_headlines()` — CoinGecko news API, returns list of 20 headline strings
- `score_sentiment()` — Claude API with tool_use + forced tool_choice, returns structured sentiment dict
- `collect_news_sentiment()` — wires fetch and score together, single entry point
- `validate_sentiment_output()` — programmatic assertions on all four output fields