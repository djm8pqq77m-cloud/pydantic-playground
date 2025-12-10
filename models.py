from pydantic import BaseModel, HttpUrl, Field

### MODELE POUR TOOL : web_search

class WebSearchSource(BaseModel):
    """
    Représente une source individuelle issue d'une recherche web Tavily.
    """
    title: str
    url: HttpUrl
    snippet: str


class WebSearchResult(BaseModel):
    """
    Regroupe la requête envoyée, une réponse synthétique générée à partir des sources,
    ainsi que la liste détaillée des sources utilisees.
    """
    query: str
    answer: str | None   =  None            
    sources: list[WebSearchSource]
    used_for: str | None = Field(
        default=None,
        description="Sous-question ou aspect précis que cette recherche devait éclairer."
    )
    

### MODELE POUR AGENT

class AgentAnswer(BaseModel):
    """
    Format que l'agent doit renvoyer

    Regles : 
    - final_answer = réponse finale à renvoyer à l'utilisateur.
    - tool_calls = nombre total d'appels de tools durant ce run.
    - web_search_history = détail de chaque appel au tool web_search.
    - reasoning_summary = optionnel, résumé court de la décision (pour debugging interne).
    """
    final_answer : str 
    tool_calls : int 
    web_search_history: list[WebSearchResult] = Field(
        default_factory=list,
        description="Historique des appels à web_search sur ce run."
    )
    reasoning_summary : str | None = Field(default=None)