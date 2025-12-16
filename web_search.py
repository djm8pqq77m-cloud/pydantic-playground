from tavily import TavilyClient
from config import TAVILY_API_KEY

import asyncio

from models import WebSearchSource, WebSearchResult

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


async def web_search(query: str, *, used_for: str | None = None) -> WebSearchResult:
    tavily_response = await asyncio.to_thread(
    tavily_client.search,
    query=query,
    max_results=5,
    include_answer=True,
    search_depth="advanced",
)

    sources = [
        WebSearchSource(
            title=r["title"],
            url=r["url"],
            snippet=r["content"][:500],
        )
        for r in tavily_response.get("results", [])
    ]

    answer = tavily_response.get("answer")

    return WebSearchResult(
        query=query,
        answer=answer,
        sources=sources,
        used_for=used_for,
    )


