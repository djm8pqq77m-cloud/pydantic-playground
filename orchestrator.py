from models import Memory, IntentNode, Evidence, OrchestratorConfig, NodeStatus, EstimatorAction, _new_id
from agents import splitter_agent, estimator_agent, answerer_agent, composer_agent
from web_search import web_search

import uuid, json





async def run_orchestrator(
    user_prompt: str,
    cfg: OrchestratorConfig = OrchestratorConfig(),
) -> tuple[str, Memory]:
    mem = Memory()

    root = IntentNode(id=_new_id(), text=user_prompt, depth=0)
    mem.add_node(root)
    mem.stack.append(root.id)
    mem.log("received_prompt", root.id, text=user_prompt)

    processed = 0
    search_count = 0

    while mem.stack:
        node_id = mem.stack.pop()
        node = mem.nodes[node_id]

        processed += 1
        if processed > cfg.max_nodes:
            mem.log("stop_max_nodes", node_id, max_nodes=cfg.max_nodes)
            node.status = NodeStatus.FAILED
            break

        if node.status in {NodeStatus.DONE, NodeStatus.FAILED}:
            continue

        # 1) estimator
        decision = (await estimator_agent.run(node.text)).output
        node.notes["estimator"] = decision.model_dump()
        mem.log("estimator_decision", node_id, **decision.model_dump())

        # 2) done (no web)
        if decision.action == EstimatorAction.DONE:
            node.answer = (await answerer_agent.run(node.text)).output
            node.status = NodeStatus.DONE
            continue

        # 3) search
        if decision.action == EstimatorAction.SEARCH:
            if search_count >= cfg.max_searches:
                node.status = NodeStatus.FAILED
                mem.log("stop_max_searches", node_id, max_searches=cfg.max_searches)
                continue

            if not decision.query:
                node.status = NodeStatus.FAILED
                mem.log("search_failed_no_query", node_id)
                continue

            node.search_query = decision.query
            search_count += 1

            mem.log("search_start", node_id, query=decision.query)
            try:
                web_result = await web_search(decision.query, used_for=node.text)
            except Exception as e:
                node.status = NodeStatus.FAILED
                mem.log("search_error", node_id, error=repr(e))
                continue
            mem.log("search_done", node_id, n_sources=len(web_result.sources))

            node.web_result = web_result
            node.answer = web_result.answer
            node.sources = [str(s.url) for s in web_result.sources]
            node.status = NodeStatus.SEARCHED
            continue

        # 4) resplit
        if node.depth >= cfg.max_depth:
            node.status = NodeStatus.FAILED
            mem.log("stop_max_depth", node_id, max_depth=cfg.max_depth)
            continue

        sub_intents = (await splitter_agent.run(node.text)).output
        node.status = NodeStatus.SPLIT
        mem.log("split_done", node_id, sub_intents=sub_intents)

        for txt in reversed(sub_intents):
            child = IntentNode(
                id=_new_id(),
                parent_id=node.id,
                text=txt,
                depth=node.depth + 1,
            )
            mem.add_node(child)
            mem.stack.append(child.id)

    evidence: list[Evidence] = []

    for n in mem.nodes.values():
        if n.status not in {NodeStatus.SEARCHED, NodeStatus.DONE}:
            continue

        if getattr(n, "web_result", None) is not None:
            evidence.append(
                Evidence(
                    intent=n.text,
                    web=n.web_result,
                )
            )
            continue

        if n.answer is not None:
            evidence.append(
                Evidence(
                    intent=n.text,
                    answer=n.answer,
                )
            )

    if not evidence:
        return "No reliable answer could be produced.", mem

    payload = {
    "user_question": user_prompt,
    "evidence": [e.model_dump(mode="json") for e in evidence],
}
    
    final = (await composer_agent.run(json.dumps(payload, ensure_ascii=False))).output
    return final.answer, mem




async def answer_query(query: str, *, debug: bool = False):
    final_answer, mem = await run_orchestrator(query)
    return (final_answer, mem) if debug else final_answer

