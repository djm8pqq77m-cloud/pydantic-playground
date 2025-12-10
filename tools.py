from pydantic_ai import tools
from tavily import TavilyClient
from config import TAVILY_API_KEY

from models import WebSearchSource, WebSearchResult

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


@tools.Tool
def web_search(query: str) -> WebSearchResult:
    """
    Recherche des informations sur le web en fonction de la requête.

    Ce tool délègue la recherche à Tavily pour :
    - obtenir des faits récents ou des actualités,
    - vérifier une information incertaine,
    - récupérer des chiffres, dates, statistiques, prix ou autres données vérifiables.

    La réponse synthétique de Tavily est renvoyée dans `answer`. Si Tavily ne fournit
    pas de synthèse, `answer` contient un message générique et l'agent doit s'appuyer
    davantage sur les sources.
    """
    tavily_response = tavily_client.search(
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
        for r in tavily_response["results"]
    ]

    raw_answer = tavily_response.get("answer")
    if not raw_answer:
        raw_answer = (
            "Aucune réponse synthétique directe renvoyée par Tavily pour cette requête. "
            "Réfère-toi aux sources pour construire la réponse."
        )

    return WebSearchResult(
        query=query,
        answer=raw_answer,
        sources=sources,
    )