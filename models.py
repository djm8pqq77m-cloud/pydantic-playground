from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, model_validator
from pydantic_ai import Agent


# =========================
# Models
# =========================

class NodeStatus(str, Enum):
    PENDING = "pending"
    SPLIT = "split"
    SEARCHED = "searched"
    DONE = "done"
    FAILED = "failed"


class IntentNode(BaseModel):
    id: str
    parent_id: str | None = None
    text: str
    depth: int = 0
    status: NodeStatus = NodeStatus.PENDING

    search_query: str | None = None
    answer: str | None = None
    sources: list[str] = Field(default_factory=list)
    notes: dict[str, Any] = Field(default_factory=dict)
    web_result: WebSearchResult | None = None


class TraceEvent(BaseModel):
    event: str
    node_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class EstimatorAction(str, Enum):
    RESPLIT = "resplit"
    SEARCH = "search"
    DONE = "done"


class EstimatorDecision(BaseModel):
    action: EstimatorAction
    reason: str
    query: str | None = None
    specificity_score: float | None = None


class WebSearchSource(BaseModel):
    title: str
    url: HttpUrl
    snippet: str


class WebSearchResult(BaseModel):
    query: str
    answer: str | None = None
    sources: list[WebSearchSource]
    used_for: str | None = Field(default=None)


class Evidence(BaseModel):
    intent: str
    answer: str | None = None         
    web: WebSearchResult | None = None 

    @model_validator(mode="after")
    def _check_has_answer_or_web(self):
        if self.answer is None and self.web is None:
            raise ValueError("Evidence must have either `answer` or `web`.")
        return self


class FinalAnswer(BaseModel):
    answer: str



# =========================
# Memory + Config
# =========================

@dataclass
class Memory:
    nodes: dict[str, IntentNode] = field(default_factory=dict)
    stack: list[str] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)

    def add_node(self, node: IntentNode) -> None:
        self.nodes[node.id] = node

    def log(self, event: str, node_id: str | None = None, **payload: Any) -> None:
        self.trace.append(TraceEvent(event=event, node_id=node_id, payload=payload))


@dataclass(frozen=True)
class OrchestratorConfig:
    max_depth: int = 3
    max_nodes: int = 30
    max_searches: int = 10


def _new_id() -> str:
    return uuid.uuid4().hex



