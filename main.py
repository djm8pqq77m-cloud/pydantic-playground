import asyncio
import config

from orchestrator import answer_query
from debug_view import print_nodes, print_splits_from_trace


if __name__ == "__main__":
    query = input("Your question: ").strip()
   
    answer, mem = asyncio.run(answer_query(query, debug=True))

    print("\n=== FINAL ANSWER ===\n")
    print(answer)

    print_nodes(mem)
    print_splits_from_trace(mem)
