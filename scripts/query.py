from vectorize import vectoriser
import chromadb
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

MODELE_RERANK = "BAAI/bge-reranker-v2-m3"   # cross-encoder multilingue


def tokenize(text):
    """Simple tokenizer: lowercase + split on non-alphanumeric chars."""
    return re.findall(r"[\w\-]+", text.lower())


# cache pour ne pas reconstruire l'index BM25 à chaque appel
_bm25_cache = {}


def _get_bm25_index(collection):
    """Construit (ou récupère depuis le cache) l'index BM25 pour cette collection."""
    cache_key = collection.name
    if cache_key not in _bm25_cache:
        all_docs = collection.get()
        documents = all_docs["documents"]
        metadatas = all_docs["metadatas"]
        tokenized_corpus = [tokenize(doc) for doc in documents]
        bm25 = BM25Okapi(tokenized_corpus)
        _bm25_cache[cache_key] = (bm25, documents, metadatas)
    return _bm25_cache[cache_key]


def dense_search(collection, question, k=3, filtre=None):
    """Recherche les k documents les plus proches, avec filtre optionnel."""
    resultat = collection.query(
        query_embeddings=vectoriser([question]),
        n_results=k,
        where=filtre,
    )
    return [
        {"text": texte, "title": meta["title"], "source": meta["source"]}
        for texte, meta in zip(resultat["documents"][0], resultat["metadatas"][0])
    ]


def bm25_search(collection, question, k=3, filtre=None):
    """Recherche les k documents les plus pertinents selon BM25."""
    bm25, documents, metadatas = _get_bm25_index(collection)

    tokenized_query = tokenize(question)
    scores = bm25.get_scores(tokenized_query)

    indices = range(len(scores))
    if filtre is not None:
        # applique le filtre manuellement si fourni (BM25 n'a pas de "where" natif)
        indices = [
            i for i in indices
            if all(metadatas[i].get(key) == value for key, value in filtre.items())
        ]

    top_indices = sorted(indices, key=lambda i: scores[i], reverse=True)[:k]

    return [
        {"text": documents[i], "title": metadatas[i]["title"], "source": metadatas[i]["source"]}
        for i in top_indices
    ]


def fusion_rrf(classements: list[list[str]], k_rrf: int = 60) -> list[str]:
    """Fusionne plusieurs classements (listes de textes) avec Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores, key=lambda d: scores[d], reverse=True)


def rerank(question: str, candidats: list[str], k: int = 3) -> list[str]:
    """Seconde passe : le cross-encoder note chaque paire et reclasse."""
    global _reranker_model
    model = CrossEncoder(MODELE_RERANK)
    paires = [(question, candidat) for candidat in candidats]
    scores = model.predict(paires)
    classement = sorted(zip(candidats, scores), key=lambda c: c[1], reverse=True)
    return [texte for texte, _ in classement[:k]]

def hybrid_search(collection, question, k=3, filtre=None, k_retrieval=10):
    """Combine recherche dense et BM25 via RRF."""
    dense_results = dense_search(collection, question, k=2*k_retrieval, filtre=filtre)
    bm25_results = bm25_search(collection, question, k=2*k_retrieval, filtre=filtre)

    dense_ranking = [r["text"] for r in dense_results]
    bm25_ranking = [r["text"] for r in bm25_results]

    fusion = fusion_rrf([dense_ranking, bm25_ranking])

    lookup = {r["text"]: r for r in dense_results}
    lookup.update({r["text"]: r for r in bm25_results if r["text"] not in lookup})

    # Reranking final avec CrossEncoder
    top_texts = fusion
    reranked_texts = rerank(question, top_texts, k=k)
    
    return [lookup[texte] for texte in reranked_texts]


if __name__ == "__main__":
    path = "hugoVec"
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection("docs")

    # print(dense_search(collection, "Template bug"))
    print(hybrid_search(collection, "printUnusedTemplates flag", k=3, k_retrieval=int(1.5*3)))
    # print(hybrid_search(collection, "Template bug"))