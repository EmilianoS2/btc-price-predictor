"""
Does each node produce an output?
technical_signals: {'rsi': 37.8, 'ema': 62836, 'vwap': 72497}
onchain_signals:   {..., 'net_exchange_flow_btc': 3624.3}   ← POSITIVE this time
macro_signals:     {'fear_greed_index': 10, 'sp500_7d_change_pct': -1.76,
                    'btc_price_usd': 62308, 'btc_30d_change_pct': -23.01}
"""
from state import BTCResearchState

def evaluator(state: BTCResearchState):
    flags = []
    for name in ["news_signals", "technical_signals", "onchain_signals", "macro_signals"]:
        if not state.get(name):          # missing OR empty {} → both falsy
            flags.append(f"{name} missing — forecast ran without it")
    if flags:
        return {"eval_score": 0.0, "eval_flags": flags}
        
    macro, tech, onchain = state['macro_signals'], state['technical_signals'], state['onchain_signals']
    price = macro['btc_price_usd']
        
    votes = [
        'bullish' if macro['sp500_7d_change_pct'] >= 0 else 'bearish',
        'bullish' if macro['btc_30d_change_pct'] >= 0 else 'bearish',
        'bullish' if price >= tech['ema'] else 'bearish',
        'bullish' if price >= tech['vwap'] else 'bearish',
        'bearish' if onchain['net_exchange_flow_btc'] >= 0 else 'bullish',
        state['news_signals']['sentiment_label'], 
    ]
        
    if tech['rsi'] >= 70: votes.append('bullish')
    elif tech['rsi'] <= 30: votes.append('bearish')
    if macro['fear_greed_index'] >= 70: votes.append('bullish')
    elif macro['fear_greed_index'] <= 30: votes.append('bearish')

    bullish, bearish = votes.count('bullish'), votes.count('bearish')
    score = max(bullish, bearish) / len(votes)

    if score < 0.6:
        flags.append(f"Low signal agreement ({score:.0%}) — signals contradict, treat with caution")

    return {"eval_score": score, "eval_flags": flags}

