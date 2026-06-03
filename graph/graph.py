from nodes import news_node, macro_node, onchain_node, technical_node, aggregate_node, human_review_node
from langgraph.graph import StateGraph, END, START
from state import BTCResearchState


graph = StateGraph(BTCResearchState)
graph.add_node("news", news_node)
graph.add_node("macro", macro_node)
graph.add_node("onchain", onchain_node)
graph.add_node("technical", technical_node)
graph.add_node("synthesis", aggregate_node)
graph.add_node("review", human_review_node)

def router_node(state: BTCResearchState):
    if state['forecast']['escalate_to_human'] == True:
        return "review"
    else:
        return END

graph.add_edge(START, "news")
graph.add_edge(START, "onchain")
graph.add_edge(START, "technical")
graph.add_edge(START, "macro")
graph.add_edge(["news", "macro", "onchain", "technical"], "synthesis")
graph.add_conditional_edges("synthesis", router_node, {"review": "review", END: END})

app = graph.compile()

print("Sheet BEFORE run:")
start = {"target_asset": "BTC", "time_horizon_days": 7}
print(f"  {start}\n")

for chunk in app.stream(start):
    print(chunk)
