from graphviz import Digraph

STATUS_COLOR = {
    "PENDING": "gray",
    "SPLIT": "lightblue",
    "SEARCHED": "orange",
    "DONE": "lightgreen",
    "FAILED": "red",
}

def render_intent_graph(mem, *, max_text=80) -> Digraph:
    dot = Digraph(
        comment="Intent Orchestrator Graph",
        graph_attr={"rankdir": "TB"},
        node_attr={"shape": "box", "style": "rounded,filled"},
    )

    for node in mem.nodes.values():
        text = node.text.replace('"', "'")
        if len(text) > max_text:
            text = text[: max_text - 3] + "..."

        label = f"{text}\n[{node.status}]"

        dot.node(
            node.id,
            label=label,
            fillcolor=STATUS_COLOR.get(str(node.status), "white"),
        )

    for node in mem.nodes.values():
        if node.parent_id:
            dot.edge(node.parent_id, node.id)

    return dot
