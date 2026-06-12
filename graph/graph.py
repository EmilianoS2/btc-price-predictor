from nodes import news_node, macro_node, onchain_node, technical_node, aggregate_node, human_review_node, evaluator_node
from langgraph.graph import StateGraph, END, START
from state import BTCResearchState


graph = StateGraph(BTCResearchState)
graph.add_node("news", news_node)
graph.add_node("macro", macro_node)
graph.add_node("onchain", onchain_node)
graph.add_node("technical", technical_node)
graph.add_node("synthesis", aggregate_node)
graph.add_node("review", human_review_node)
graph.add_node("evaluate", evaluator_node)

def router_node(state: BTCResearchState):
    try:
        if state['forecast']['escalate_to_human'] == True:
            return "review"
        else:
            return END
    except Exception as e:
        print(f"Router Node faled: {e}")
        return END

graph.add_edge(START, "news")
graph.add_edge(START, "onchain")
graph.add_edge(START, "technical")
graph.add_edge(START, "macro")
graph.add_edge(["news", "macro", "onchain", "technical"], "synthesis")
graph.add_edge("synthesis", "evaluate")
graph.add_conditional_edges("evaluate", router_node, {"review": "review", END: END})

app = graph.compile()

if __name__ == "__main__":
    print("Sheet BEFORE run:")
    start = {"target_asset": "BTC", "time_horizon_days": 7}
    print(f"  {start}\n")

    try:
        for chunk in app.stream(start):
            print(chunk)
    except Exception as e:
        print(f"Start faled: {e}")