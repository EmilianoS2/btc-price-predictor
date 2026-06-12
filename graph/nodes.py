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
from eval import evaluator
from state import BTCResearchState
from langsmith import Client, traceable, get_current_run_tree

client = Client()

def news_node(state: BTCResearchState) -> dict:
    try:
        return {"news_signals": collect_news_sentiment()}
    except Exception as e:
        print(f"News failed: {e}")
        return {"news_signals": {}}
def macro_node(state: BTCResearchState) -> dict:
    try:
        return {"macro_signals": collect_macro_context()}
    except Exception as e:
        print(f"Macro failed: {e}")
        return {"macro_signals": {}}
    
def onchain_node(state: BTCResearchState) -> dict:
    try:
        return {"onchain_signals": fetch_onchain_metrics()}  
    except Exception as e:
        print(f"Onchain failed: {e}")
        return {"onchain_signals": {}}

def technical_node(state: BTCResearchState) -> dict:
    try:
        return {"technical_signals": analyze_indicators()}
    except Exception as e:
        print(f"Techincal failed: {e}")
        return {"technical_signals": {}}
    
def aggregate_node(state: BTCResearchState) -> dict:
    try:
        return {"forecast": run_synthesis(state)}
    except Exception as e:
        print(f"Forecast failed: {e}")
        return {"forecast": {}}
    
def human_review_node(state: BTCResearchState) -> dict:
    return {}

@traceable
def evaluator_node(state: BTCResearchState) -> dict:
    try:
        run = get_current_run_tree()
        evals = evaluator(state)
        client.create_feedback(key="eval_score", score=evals['eval_score'], run_id=run.trace_id)
        return evals
    except Exception as e:
        print(f"Evaluator failed: {e}")
        return {"Evaluator": {}}