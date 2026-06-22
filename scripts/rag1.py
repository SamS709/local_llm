#!/usr/bin/env python3
"""
TP 07 : DevOps Buddy - Assistant local complet
Objectif : Combiner toutes les fonctionnalités Ollama dans un assistant interactif
Features utilisées : chat, streaming, structured output, embeddings
"""

from ollama import chat, embed
from pydantic import BaseModel
import math


# === Configuration ===
MODEL = 'qwen_tuned2:latest'
MODEL_EMBED = 'nomic-embed-text:latest'
SYSTEM_PROMPT = '''Tu es DevOps Buddy, un assistant expert DevOps/DevSecOps.
Tu réponds en français de manière concise et technique.
Tu donnes des exemples de commandes quand c'est pertinent.
Tu structures tes réponses avec des listes à puces.'''


# === Base de connaissances embarquée ===
KNOWLEDGE_BASE = [
    {"topic": "docker", "content": "Docker utilise des conteneurs pour isoler les applications. Commandes: docker build, docker run, docker compose"},
    {"topic": "kubernetes", "content": "Kubernetes orchestre les conteneurs. Concepts: Pod, Deployment, Service, Ingress. Commandes: kubectl get, kubectl apply"},
    {"topic": "ansible", "content": "Ansible automatise la configuration. Concepts: playbook, inventory, role, task. Commande: ansible-playbook"},
    {"topic": "terraform", "content": "Terraform gère l'infrastructure as code. Concepts: provider, resource, module, state. Commandes: terraform init, plan, apply"},
    {"topic": "gitlab", "content": "GitLab CI/CD pipeline avec .gitlab-ci.yml. Concepts: stages, jobs, artifacts, cache, runners"},
    {"topic": "prometheus", "content": "Prometheus collecte les métriques. Concepts: scraping, PromQL, alertmanager, exporters"},
]


# Pré-calculer les embeddings de la base de connaissances
print("🔄 Chargement de la base de connaissances...")
knowledge_embeddings = []
for item in KNOWLEDGE_BASE:
    response = embed(model=MODEL_EMBED, input=item["content"])
    knowledge_embeddings.append(response.embeddings[0])
print(f"✅ {len(KNOWLEDGE_BASE)} documents indexés\n")


# === Fonctions utilitaires ===
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a ** 2 for a in vec1))
    norm2 = math.sqrt(sum(b ** 2 for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0


def find_relevant_context(query: str, top_k: int = 2) -> str:
    """Recherche les documents pertinents pour enrichir le contexte"""
    query_emb = embed(model=MODEL_EMBED, input=query).embeddings[0]

    scores = []
    for i, doc_emb in enumerate(knowledge_embeddings):
        score = cosine_similarity(query_emb, doc_emb)
        scores.append((score, KNOWLEDGE_BASE[i]))

    scores.sort(reverse=True)
    top_docs = scores[:top_k]

    context = "\n".join([f"- {doc['content']}" for _, doc in top_docs])
    return context


# === Schéma pour les commandes structurées ===
class CommandSuggestion(BaseModel):
    command: str
    description: str
    warning: str | None = None


def get_structured_command(query: str) -> CommandSuggestion | None:
    """Obtenir une suggestion de commande structurée"""
    try:
        response = chat(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': 'Tu suggères des commandes DevOps. Réponds uniquement en JSON.'},
                {'role': 'user', 'content': f'Suggère une commande pour: {query}'}
            ],
            format=CommandSuggestion.model_json_schema(),
            options={'temperature': 0, 'num_predict': 200}
        )
        return CommandSuggestion.model_validate_json(response.message.content)
    except Exception as e:
        print(f"⚠️ Erreur structured output: {e}")
        return None


# === Chat avec RAG ===
def chat_with_rag(question: str, history: list) -> str:
    """Répond à une question avec contexte enrichi"""
    # Trouver le contexte pertinent
    context = find_relevant_context(question)

    # Construire le prompt enrichi
    augmented_question = f"""Contexte (base de connaissances):
{context}

Question de l'utilisateur: {question}"""

    # Ajouter au historique
    history.append({'role': 'user', 'content': augmented_question})

    # Appeler le modèle avec streaming
    response_text = ""
    stream = chat(
        model=MODEL,
        messages=history,
        stream=True,
        options={'temperature': 0.3}
    )

    for chunk in stream:
        content = chunk.message.content
        print(content, end='', flush=True)
        response_text += content

    print()  # Nouvelle ligne après le streaming

    # Ajouter la réponse à l'historique
    history.append({'role': 'assistant', 'content': response_text})

    return response_text


# === Main ===
def main():
    print("=" * 60)
    print("🤖 DevOps Buddy - Assistant DevOps Local (Ollama)")
    print("=" * 60)
    print(f"Modèle: {MODEL}")
    print("Commandes spéciales:")
    print("  /cmd <action> : Obtenir une commande structurée")
    print("  /quit         : Quitter")
    print("-" * 60)

    history = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("\n👤 Vous: ").strip()

            if not user_input:
                continue

            if user_input.lower() == '/quit':
                print("👋 À bientôt!")
                break

            if user_input.startswith('/cmd '):
                # Mode commande structurée
                query = user_input[5:]
                print("\n🔧 Recherche de commande...")
                result = get_structured_command(query)
                if result:
                    print(f"\n📋 Commande: {result.command}")
                    print(f"📝 Description: {result.description}")
                    if result.warning:
                        print(f"⚠️  Attention: {result.warning}")
                else:
                    print("❌ Impossible de générer la commande")
            else:
                # Mode conversation avec RAG
                print("\n🤖 DevOps Buddy: ", end='')
                chat_with_rag(user_input, history)

        except EOFError:
            print("\n👋 À bientôt!")
            break
        except KeyboardInterrupt:
            print("\n👋 Interruption - À bientôt!")
            break


if __name__ == "__main__":
    main()