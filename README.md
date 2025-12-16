# PydanticAI Intent Orchestrator

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-green)](#)
[![PydanticAI](https://img.shields.io/badge/PydanticAI-enabled-purple)](#)

A minimal **code-driven** orchestrator that builds an intent tree and (optionally) uses web search for up-to-date answers.

- Orchestrator = deterministic Python (not an LLM)
- Specialized LLM agents: split → estimate → answer → compose
- Debuggable state via `Memory` (nodes, stack, trace)

---

## What this is

This project implements a small orchestration loop:

1. **Splitter** proposes 2–5 actionable sub-intents when an intent is too broad.
2. **Estimator** routes each intent to one action:
   - `done` (answer without web),
   - `search` (one focused web query),
   - `resplit` (split into sub-intents).
3. **Web search** (Tavily) fetches recent facts and sources when needed.
4. **Composer** synthesizes a final answer from collected evidence.

The orchestrator itself is plain Python code so execution stays deterministic, bounded, and easy to debug.

---

## Project layout

```text
.
├── main.py           # CLI entrypoint
├── orchestrator.py   # orchestration loop (deterministic)
├── agents.py         # PydanticAI agents (split/estimate/answer/compose)
├── models.py         # Pydantic models (Memory, IntentNode, Evidence, etc.)
├── web_search.py     # Tavily integration (returns WebSearchResult)
└── debug_view.py     # pretty-print Memory (nodes + trace)
```

---

## Requirements

- Python 3.10+ recommended
- `pydantic` (v2)
- `pydantic-ai`
- A model provider key (e.g., OpenAI)
- Tavily key if you enable web search

---

## Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

```bash
export OPENAI_API_KEY="..."
export TAVILY_API_KEY="..."   # required if using Tavily web search
```

---

## Run

```bash
python main.py
```

You will be prompted:

```text
Your question:
```

---

## How it works (core concepts)

### IntentNode fields

- `text` = human-readable intent (LLM-facing)
- `search_query` = search-engine query (produced by the estimator)
- `web_result` = structured search output (`WebSearchResult`)
- `answer` = resolved answer (web summary or no-web answerer)
- `status` = `PENDING | SPLIT | SEARCHED | DONE | FAILED`

### Memory (state)

- `mem.nodes` = all nodes created (the intent tree)
- `mem.stack` = node IDs left to process (DFS via `.pop()`)
- `mem.trace` = logs (decisions, searches, splits)

---

## Configuration

Tune `OrchestratorConfig`:

- `max_nodes`: cap processed nodes (prevents runaway splitting)
- `max_depth`: cap split depth
- `max_searches`: cap web calls (controls cost)

---

## Debugging

Use debug mode to inspect internal state (nodes, queries, statuses, decisions, splits).

Recommended trace events:

- `received_prompt`
- `estimator_decision`
- `search_start` / `search_done` / `search_error`
- `split_done` (include `sub_intents`)
- `final_synthesized`

---

## Troubleshooting

### Markdown does not render on GitHub

Make sure the file is named **`README.md`** (not `README.me`) and you did not wrap the whole file in triple backticks.

### It never splits

Your estimator may be too “search-first”. Use multi-aspect prompts (compare + pricing + constraints) or tighten the estimator prompt to prefer `resplit` for multi-aspect intents.

### Web search feels slow or blocks

If your Tavily client is synchronous, wrap the call with `asyncio.to_thread(...)` inside `web_search.py` so it does not block the event loop.

### Empty web summary

Some searches return no synthetic summary. The composer should then rely on `sources[*].snippet` and URLs.

---

## Good test questions

- Split + web:
  - Compare Tavily vs SerpAPI vs Brave Search API: pricing, rate limits, Python integration, pros/cons. Provide sources.
- Local/time-sensitive:
  - Find 5 coworking spaces in Shoreditch with day passes under £25, open after 8pm, include links.
- Recent updates:
  - What changed in PydanticAI in the last 90 days? Provide sources.
