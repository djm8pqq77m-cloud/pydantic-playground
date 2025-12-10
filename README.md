# 🧠 Pydantic AI – Agent + Tools Starter

Ce projet illustre une architecture propre pour construire un agent intelligent avec **Pydantic AI**,  
des **tools personnalisés**, et une **réponse finale structurée** grâce aux modèles Pydantic.

---

## 📁 Structure du projet

```
project/
├── agents.py        # Définition des agents : prompts, result_type, tools connectés
├── tools.py         # Définition des tools (@tool) utilisés par l’agent
├── models.py        # Modèles Pydantic (AgentAnswer, ToolCall, etc.)
└── main.py          # Point d’entrée : exécution de l’agent
```

### 🔹 `tools.py`  
Contient **uniquement** les tools (fonctions Python décorées par `@tool`) :

- Chaque tool représente une **capacité externe** accessible à l’agent  
  (recherche web, calcul, accès fichier, API externe…).
- La **docstring** décrit ce que fait le tool.
- Le LLM **lit cette docstring** pour comprendre comment utiliser l’outil.

---

### 🔹 `models.py`  
Définit les modèles Pydantic utilisés pour :

- structurer la réponse finale de l’agent (`AgentAnswer`)
- éventuellement structurer la sortie des tools (`ToolCall`, `WebSearchResult`, etc.)

Un exemple typique :

```python
class AgentAnswer(BaseModel):
    final_answer: str
    tool_calls: int
    reasoning_summary: str | None = None
```

Ce modèle sert :

- de **result_type** dans Pydantic AI  
- de **response_model** dans FastAPI si on expose l’agent via une API

---

### 🔹 `agents.py`  
Fichier principal où l’on construit l’agent :

- choix du modèle (`gpt-4o-mini`, etc.)
- connexion des tools
- définition du `result_type`
- écriture du **system_prompt**, qui donne au LLM les règles de comportement

Exemples de règles dans le prompt :

- quand utiliser un tool  
- possibilité d’en appeler plusieurs  
- comment combiner les résultats  
- comment structurer la réponse finale

---

### 🔹 `main.py`  
Point d’entrée de l’application.  
Tu exécutes l’agent ici :

```python
from agents import agent

result = agent.run_sync("Explique-moi ce qu'est le surapprentissage.")
print(result.output)
```


## 🔧 Fonctionnement général

1. L’utilisateur fournit une requête  
2. L’agent analyse la question  
3. S’il manque d’information, il peut appeler un **tool**  
4. Il peut appeler ce tool **plusieurs fois** jusqu’à ce qu’il estime avoir assez d’éléments  
5. Il génère une **réponse finale structurée** conforme à `AgentAnswer`

---

## 🧠 Rôles respectifs

| Élément | Rôle |
|--------|------|
| **tools.py** | Déclare les outils utilisables par le LLM |
| **models.py** | Structure les données échangées |
| **agents.py** | Configure le cerveau : modèle, tools, règles (system_prompt) |
| **main.py** | Exécute l’agent : test / API / interface |

-


## 🚀 Pour lancer

```bash
python main.py
```

