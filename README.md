# Bitcoin Multi-Agent Research System

A multi-agent system that researches Bitcoin across four signal domains and synthesizes them into a weekly price direction prediction with confidence scoring and structured JSON output.

## Architecture

```
                    [ Coordinator ]
                   /      |       \      \
           [Tech]   [Macro]  [OnChain]  [News]
                   \      |       /      /
                 [ Synthesis Layer ]
                         |
                   [ Final Output ]
```

The system follows a hub-and-spoke pattern. The coordinator triggers all four subagents in sequence, collects their structured outputs, and passes them to the synthesis layer which produces the final prediction.

## Subagents

| File | Domain | Data Source |
|------|--------|-------------|
| `technical_analysis.py` | RSI, EMA, VWAP | CoinGecko |
| `macro_context.py` | Fear & Greed, S&P 500, BTC 30d change | Alternative.me, Yahoo Finance, CoinGecko |
| `onchain_data.py` | Active addresses, exchange flows | CoinMetrics community API |
| `news_sentiment.py` | Headline sentiment, themes | CoinGecko News + Claude API |

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
```
pip install requests anthropic pandas ta yfinance python-dotenv
```

2. Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```

3. Run the system:
```
python synthesis.py
```

## APIs Used

All APIs are free tier or require no authentication except the Anthropic API.

- [CoinGecko](https://www.coingecko.com/en/api) — price data, news
- [Alternative.me](https://alternative.me/crypto/fear-and-greed-index/) — Fear & Greed Index
- [CoinMetrics](https://docs.coinmetrics.io/api/v4) — on-chain metrics
- [Yahoo Finance](https://pypi.org/project/yfinance/) — S&P 500 data
- [Anthropic](https://docs.anthropic.com) — Claude API for sentiment scoring and synthesis
