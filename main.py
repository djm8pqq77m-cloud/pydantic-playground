from agents import agent
from pydantic_ai.usage import UsageLimits


if __name__ == "__main__":
    print("\n=== Assistant Web Search ===\n")

    query = input("Pose une question → ")

    run_result = agent.run_sync(query)
    answer = run_result.output

    print("\n Réponse finale : \n")
    print(answer.final_answer)

    print(f"\n Nombre d'appels web_search : {answer.tool_calls}")

    if answer.web_search_history:
        print("\n Historique des recherches : ")
        for idx, call in enumerate(answer.web_search_history, 1):
            print(f"\n--- Recherche #{idx} ---")
            print(f"Query      : {call.query}")
            print(f"Used for   : {call.used_for}")
            print(f"Synthèse   : {call.answer}")
            print("Sources    :")
            for s in call.sources[:2]:  # on affiche 2 max pour ne pas noyer le terminal
                print(f"  - {s.title} ({s.url})")
    else:
        print("\nAucune recherche web n'a été utilisée.")


    print("\n --- Fin du run --- \n")