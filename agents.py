from pydantic import BaseModel, Field
from pydantic_ai import Agent

from models import *




splitter_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=list[str],
    system_prompt=(
        """
        You are a task-splitting agent.

        CRITICAL CONSTRAINTS (must never be violated):

        1) Grounded context
        - Every sub-intent MUST stay strictly grounded in the parent intent.
        - You MUST reuse the same entities, location, and scope as the parent.
        - You MUST NOT introduce new locations, cities, countries, or domains.
        - You MUST NOT generalize or broaden the scope.

        2) No placeholders or invented entities
        - NEVER use placeholders such as:
        "Company A/B/C", "Space A/B/C", "Coworking Space X", or similar.
        - NEVER invent entities that were not explicitly mentioned or already discovered.

        3) No speculative splitting
        - If the parent intent does not already contain concrete entities,
        DO NOT split by entity.
        - In that case, produce at most ONE sub-intent focused on
        discovering concrete entities first.

        4) Lexical anchoring
        - Each sub-intent MUST explicitly reuse at least one key term
        from the parent intent (e.g. location, constraint, price, time).
        - If this is not possible, DO NOT output the sub-intent.

        5) Failure is acceptable
        - If the intent cannot be safely split without violating the rules,
        return an empty list.

        OUTPUT RULES:
        - Output ONLY a JSON array of strings.
        - Each string must be a concrete, executable sub-intent.
        - Return at most 3 sub-intents. If you need more, prioritize the 3 most critical.
        - No explanations, no commentary.

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
