from technical_analysis import analyze_indicators
from macro_context import collect_macro_context
from onchain_data import fetch_onchain_metrics
from news_sentiment import collect_news_sentiment

def run_coordinator():
    technical = analyze_indicators()
    macro = collect_macro_context()
    onchain = fetch_onchain_metrics()
    news = collect_news_sentiment()
    return {
        "technical": technical,
        "macro": macro,
        "onchain": onchain,
        "news": news
    }
