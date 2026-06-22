from litellm import completion
import os

# Load environment variables from .env file
# Définition des outils
def search_kb(query: str) -> str:
    """Simule une recherche dans une base de connaissances."""
    kb = {
        "kubernetes pods": "Un Pod est la plus petite unité déployable dans Kubernetes.",
        "docker container": "Un conteneur Docker est une instance d'une image.",
        "helm chart": "Helm est un gestionnaire de packages pour Kubernetes.",
    }
    for key, value in kb.items():
        if key in query.lower():
            return value
    return "Aucune information trouvée."

def calculate(expression: str) -> str:
    """Calcule une expression mathématique."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur: {e}"

TOOLS = {"search_kb": search_kb, "calculate": calculate}

# Prompt ReAct
react_prompt = """Tu es un assistant qui résout des problèmes en alternant réflexion et action.
Outils disponibles:
- search_kb(query): Recherche dans la base de connaissances
- calculate(expression): Calcule une expression mathématique
Format de réponse:
Thought: [ta réflexion]
Action: [nom_outil]
Action Input: [paramètre]
---
Observation: [résultat - fourni par le système]
Thought: [réflexion sur le résultat]
...
Final Answer: [réponse finale]

### EXAMPLE
Thought: I should use a tool to get the temperature in Paris
Action: get_temperature
Action Input: Paris
---
Observation: 25
Thought: The temperature in Paris given by the get_temperature tool is 25 degrees, which should be in degrs Celcius.
...
Final Answer: The temperature in Paris in 25 degrees Celcius.
Question: Qu'est-ce qu'un Pod Kubernetes et combien de pods aurais-je si j'en déploie 3 réplicas ?"""

# Boucle ReAct
messages = [{"role": "user", "content": react_prompt}]
max_iterations = 5

for i in range(max_iterations):
    try:
        # Using Ollama with lite_llm
        response = completion(
            model="ollama/qwen_tuned2:latest",  # Format for Ollama models
        messages=messages,
            api_base="http://localhost:11434"  # Ollama default address
        )

        content = response.choices[0].message.content
        print(content)
        
        # Réponse finale ?
        if "Final Answer:" in content:
            break
        
        # Extraire et exécuter l'action
        if "Action:" in content and "Action Input:" in content:
            lines = content.split("\n")
            action = next((l.replace("Action:", "").strip() for l in lines if l.startswith("Action:")), None)
            action_input = next((l.replace("Action Input:", "").strip() for l in lines if l.startswith("Action Input:")), None)
            
            if action in TOOLS:
                result = TOOLS[action](action_input)
                observation = f"\nObservation: {result}\n"
                print(observation)
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": observation + "Continue:"})

    except Exception as e:
        print(f"Error occurred: {e}")
        print("Make sure Ollama is running and the model 'qwen_tuned2:latest' is pulled")
        break

