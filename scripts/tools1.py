from ollama import Client

MODEL = "qwen_tuned2:latest"
HOST = "http://192.168.1.20:11434"
def calculer(expression: str) -> str:
    """Évalue une expression mathématique simple."""
    allowed = set("0123456789+-*/. ()")
    if not all(c in allowed for c in expression):
        return "Expression non autorisée."
    return str(eval(expression, {"__builtins__": {}}, {}))

def recherche_doc(query: str) -> str:
    """Retourne un extrait fictif de doc interne."""
    db = {
        "ollama": "Ollama est un runtime local pour LLM open-source.",
        "h100": "NVIDIA H100 : 80 Go HBM3, idéal pour LLM jusqu'à 70B paramètres.",
    }
    for key, val in db.items():
        if key in query.lower():
            return val
    return "Aucun résultat."

TOOLS = [
    {"type": "function", "function": {
        "name": "calculer",
        "description": "Calculer une expression mathématique.",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
    }},
    {"type": "function", "function": {
        "name": "recherche_doc",
        "description": "Rechercher dans la doc interne (Ollama, H100).",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    }},
]

DISPATCH = {"calculer": calculer, "recherche_doc": recherche_doc}

# Le LLM choisit lequel utiliser
client = Client(host="http://localhost:11434")
def ask(question: str) -> None:
    messages = [{"role": "user", "content": question}]
    response = client.chat(model=MODEL, messages=messages, tools=TOOLS, options={"temperature": 0})
    msg = response["message"]
    if not msg.get("tool_calls"):
        print("→", msg.get("content", ""))
        return
    messages.append(msg)
    for call in msg["tool_calls"]:
        name = call["function"]["name"]
        result = DISPATCH[name](**call["function"]["arguments"])
        print(f"  Tool: {name} → {result}")
        messages.append({"role": "tool", "content": str(result), "name": name})
    final = client.chat(model=MODEL, messages=messages, options={"temperature": 0})
    print("→", final["message"]["content"])

ask("Combien font 234 * 17 ?")
ask("C'est quoi le H100 ?")