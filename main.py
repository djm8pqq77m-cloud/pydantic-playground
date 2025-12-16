import asyncio
import config

from orchestrator import answer_query
from debug_view import print_nodes, print_splits_from_trace
from visualisation import render_intent_graph



if __name__ == "__main__":
    query = input("Your question: ").strip()
   
    answer, mem = asyncio.run(answer_query(query, debug=True))

    print("\n=== FINAL ANSWER ===\n")
    print(answer)

    dot = render_intent_graph(mem)
    dot.render("intent_graph", format="png", cleanup=True)  



