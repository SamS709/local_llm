import chromadb
from ollama import embed

MODEL_EMBED = 'nomic-embed-text:latest'


def vectoriser(texte: str) -> list[float]:
    vec = embed(model=MODEL_EMBED, input=texte).embeddings[0]
    return vec
    
    
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documentation")

# Sample documents
documents = [
    "Un volume Docker conserve les données du conteneur.",
    "Terraform décrit une infrastructure en code déclaratif.",
]

# Generate embeddings for each document
embeddings = [vectoriser(doc) for doc in documents]

collection.add(
    ids=["doc-0", "doc-1"],
    documents=documents,
    embeddings=embeddings,
    metadatas=[
        {"sujet": "docker", "annee": 2026},
        {"sujet": "terraform", "annee": 2024},
    ],
)


def rechercher(collection, question, k=3, filtre=None):
    """Recherche les k documents les plus proches, avec filtre optionnel."""
    resultat = collection.query(
        query_embeddings=vectoriser([question]),
        n_results=k,
        where=filtre,
    )
    return [
        {"texte": texte, "sujet": meta["sujet"], "annee": meta["annee"]}
        for texte, meta in zip(resultat["documents"][0], resultat["metadatas"][0])
    ]
    
# Chercher uniquement dans les documents Docker de 2026.
filtre = {"$and": [{"sujet": "docker"}, {"annee": 2026}]}
resultats = rechercher(collection, "conteneur", k=5, filtre=filtre)

print(resultats)