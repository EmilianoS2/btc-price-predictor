"""Node wrappers. Each node is a thin doorway: it calls a real worker
function and labels the result for its slot on the shared State sheet.
The workers (in the project root) are untouched."""
import sys
import os

# let this file import the worker functions from the project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from news_sentiment import collect_news_sentiment
from macro_context import collect_macro_context
from onchain_data import fetch_onchain_metrics
from technical_analysis import analyze_indicators
from synthesis import run_synthesis
from state import BTCResearchState


def news_node(state: BTCResearchState) -> dict:
    return {"news_signals": collect_news_sentiment()}

def macro_node(state: BTCResearchState) -> dict:
    return {"macro_signals": collect_macro_context()}

def onchain_node(state: BTCResearchState) -> dict:
    return {"onchain_signals": fetch_onchain_metrics()}  

def technical_node(state: BTCResearchState) -> dict:
    return {"technical_signals": analyze_indicators()}

def aggregate_node(state: BTCResearchState) -> dict:
    return {"forecast": run_synthesis(state)}

def human_review_node(state: BTCResearchState) -> dict:
    return {}
