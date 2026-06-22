from scripts.rag.create_docs.extract_text import extract_markdowns
from scripts.rag.create_docs.clean_text import nettoyer
from scripts.rag.create_docs.chunk_text import chunk_par_sections_markdown
from scripts.rag.utils.vectorize import vectoriser
import chromadb

def nettoyer_corpus(corpus: list[dict]) -> list[dict]:
    for doc in corpus:
        for key in doc.keys():
            doc[key] = nettoyer(doc[key])
    return corpus


def create_vec_db_from_markdowns(corpus: list[dict], path: str):
    chunks = []

    print("\nCreatung chunks ...")
    for doc in corpus:
        for chunk in chunk_par_sections_markdown(doc["text"]):
            chunks.append({
                "source": doc["source"],
                "title":  chunk["title"],
                "text":   chunk["text"],
            })
    print("\nCreatung vectors ...")
    vecteurs = vectoriser([c["text"] for c in chunks])
    
    # 3. Chargement dans ChromaDB
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection("docs")

    print("\nFilling Database ...")
    max_batch_size = 5000  # ChromaDB's limit was reported as 5461; stay safely under it
    n = len(chunks)
    for i in range(0, n, max_batch_size):
        batch_chunks = chunks[i:i + max_batch_size]
        batch_vecteurs = vecteurs[i:i + max_batch_size]
        collection.add(
            ids=[f"chunk-{j:05d}" for j in range(i, i + len(batch_chunks))],
            documents=[c["text"] for c in batch_chunks],
            embeddings=batch_vecteurs,
            metadatas=[
                {
                    "source": c["source"],
                    "title":  c["title"],
                    "text":   c["text"],
                }
                for c in batch_chunks
            ],
        )
        print(f"  Inséré {min(i + max_batch_size, n)}/{n} chunks")

    
    
if __name__ == "__main__":
    corpus = extract_markdowns("hugoDocs", threshold=200)
    corpus = nettoyer_corpus(corpus)
    create_vec_db_from_markdowns(corpus, "hugoVec")
    