from __future__ import annotations

from typing import Iterable


def print_nodes(mem) -> None:
    """
    Print the intent tree in a readable way.
    Assumes:
      - mem.nodes: dict[id, IntentNode]
      - each node has: depth, status, text, search_query?, web_result?, answer?
    """
    nodes = sorted(mem.nodes.values(), key=lambda n: (n.depth, n.id))

    print("\n=== NODES (intent tree) ===\n")
    for n in nodes:
        indent = "  " * getattr(n, "depth", 0)
        status = getattr(n, "status", "?")
        text = getattr(n, "text", "")

        print(f"{indent}- [{status}] {text}")

        est = (getattr(n, "notes", {}) or {}).get("estimator")
        if est:
            action = est.get("action")
            reason = est.get("reason")
            print(f"{indent}  estimator: {action} | {reason}")
            if est.get("query"):
                print(f"{indent}  estimator_query: {est['query']}")

        q = getattr(n, "search_query", None)
        if q:
            print(f"{indent}  query: {q}")

        wr = getattr(n, "web_result", None)
        if wr is not None:
            sources = getattr(wr, "sources", []) or []
            print(f"{indent}  sources: {len(sources)}")

        ans = getattr(n, "answer", None)
        if ans:
            preview = str(ans).replace("\n", " ")[:120]
            print(f"{indent}  answer: {preview}...")


def print_splits_from_trace(mem) -> None:
    """
    Print split events with parent intent text.
    """
    print("\n=== SPLITS (from trace) ===\n")

    for ev in getattr(mem, "trace", []):
        if ev.event != "split_done":
            continue

        node_id = ev.node_id
        parent_text = (
            mem.nodes[node_id].text
            if node_id in mem.nodes
            else "<unknown intent>"
        )

        subs = (ev.payload or {}).get("sub_intents", [])

        print(f'- "{parent_text}" split into {len(subs)} intents:')
        for s in subs:
            print(f"  • {s}")
