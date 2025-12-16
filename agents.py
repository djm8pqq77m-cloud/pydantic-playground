from pydantic import BaseModel, Field
from pydantic_ai import Agent

from models import *




splitter_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=list[str],
    system_prompt=(
        """
        Split a user request into actionable sub-intents.

        Goal:
          Produce a SMALL list (2 to 5) of specific, independently solvable sub-intents.

        Rules:
          - Each sub-intent must be concrete and directly searchable/answerable.
          - Avoid vague items like "research more" or "learn about X".
          - Preserve key constraints (time window, location, entity names).
          - Do NOT add commentary.

        Output:
          Return ONLY a JSON array of strings (no extra text).
        """
    ).strip(),
)

estimator_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=EstimatorDecision,
    system_prompt=(
        """
        Decide how to route a single intent.

        Actions:
          - done: Answerable reliably without web browsing.
          - search: ONE focused web query is sufficient.
          - resplit: Decompose into 2 to 5 sub-intents.

        Use 'resplit' when:
          - Multiple distinct aspects are requested (e.g., list + explain, compare across dimensions).
          - A time window (today/current/last X) exists AND more than one thing is asked.
          - More than one web query would be needed.
          - Scope/criteria are unclear (missing entity/time/location/constraints).

        Use 'search' only when:
          - The intent is single-aspect and well-scoped.
          - The query includes key constraints (time window/location/entity).

        Use 'done' only when:
          - The answer is stable/common knowledge and not dependent on recent facts.

        Output:
          Return valid EstimatorDecision JSON:
            - action: one of ["done","search","resplit"]
            - reason: one short sentence
            - query: REQUIRED if action="search", else null
            - specificity_score: float in [0.0, 1.0]
        """
    ).strip(),
)

answerer_agent = Agent(
    "openai:gpt-4o",
    output_type=str,
    system_prompt=(
        """
        Answer an intent without web browsing.

        Rules:
          - Be concise and accurate.
          - If critical information is missing or likely time-sensitive, say what is missing.
          - Do NOT fabricate citations or exact figures.

        Output:
          Return plain text only.
        """
    ).strip(),
)

composer_agent = Agent(
    "openai:gpt-4o",
    output_type=FinalAnswer,
    system_prompt=(
        """
        Compose the final response from evidence.

        Inputs:
          - user_question
          - evidence: a list of items where each item has:
              - intent
              - either 'answer' (no-web) OR 'web' (WebSearchResult with sources)

        Rules:
          - Answer the user's question directly and structure the response clearly.
          - Prefer evidence.web.answer when present; if missing, rely on evidence.web.sources[*].snippet.
          - If evidence is incomplete, state what is missing (do not guess).
          - Include a short "Sources" section with bullet-point URLs when sources exist.

        Output:
          Return FinalAnswer JSON: {"answer": "..."} (no extra keys).
        """
    ).strip(),
)
