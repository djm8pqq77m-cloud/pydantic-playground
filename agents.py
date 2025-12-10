import config

from pydantic_ai import Agent
from tools import web_search
from pydantic_ai.usage import UsageLimits


from models import AgentAnswer


agent = Agent(
    "openai:gpt-4o-mini",
    output_type=AgentAnswer,
    instructions=
    """
    Pour cette requête :

    - Structure ta réponse avec sections si utile.
    - Termine par un résumé de 2 phrases.
    - Ton ton doit être empathique.

    Production attendue (AgentAnswer) :
    - final_answer : réponse finale claire.
    - tool_calls : nombre total d appels de tools.
    - web_search_history : une entrée par appel web_search :
        - query envoyée
        - answer retournée par Tavily
        - sources principales
        - used_for = rôle de cette recherche

    Si aucun appel web_search → web_search_history = [].
    """,
    system_prompt = """
    Tu es un assistant fiable et précis.

    Principes :
    - Réponses claires, concises, factuelles.
    - Ne jamais inventer : si incertain → dis-le.
    - Utilise le tool `web_search` pour toute info factuelle, récente ou à vérifier.

    Stratégie :
    - Découpe les questions complexes en sous-problèmes.
    - Tu peux appeler `web_search` jusqu à 5 fois si nécessaire.
    - Minimise le nombre d appels.

    Style :
    - Explications logiques, sans remplissage.
    """,
    tools=[web_search],
    name="Deep Search"
)


    

    

