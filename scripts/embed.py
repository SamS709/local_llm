import math
from ollama import chat, embed

MODEL_EMBED = 'nomic-embed-text:latest'

KNOWLEDGE_BASE = [
    "Docker utilise des conteneurs pour isoler les applications. Commandes: docker build, docker run, docker compose",
    "Kubernetes orchestre les conteneurs. Concepts: Pod, Deployment, Service, Ingress. Commandes: kubectl get, kubectl apply",
    "Ansible automatise la configuration. Concepts: playbook, inventory, role, task. Commande: ansible-playbook",
    "Terraform gère l'infrastructure as code. Concepts: provider, resource, module, state. Commandes: terraform init, plan, apply",
    "GitLab CI/CD pipeline avec .gitlab-ci.yml. Concepts: stages, jobs, artifacts, cache, runners",
    "Prometheus collecte les métriques. Concepts: scraping, PromQL, alertmanager, exporters",
]

def vectoriser(texte: str) -> list[float]:
    vec = embed(model=MODEL_EMBED, input=texte).embeddings[0]
    return vec
    
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a ** 2 for a in vec1))
    norm2 = math.sqrt(sum(b ** 2 for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0


def indexer(textes: list[str]) -> list[dict]:
    """Vectorise une liste de textes en documents prêts pour la recherche."""
    return [{"texte": t, "vecteur": vectoriser(t)} for t in textes]

def rechercher(question: str, corpus: list[dict], k: int = 3) -> list[dict]:
    """Classe les documents du corpus par similarité avec la question."""
    v_question = vectoriser(question)
    classes = sorted(
        corpus,
        key=lambda doc: cosine_similarity(v_question, doc["vecteur"]),
        reverse=True,
    )
    return classes[:k]


if __name__ == "__main__":
    texte = "Qu'est ce que Kubernetees veut dire ?"
    classes = rechercher(texte, indexer(KNOWLEDGE_BASE))
    print(classes[0]["texte"])
    