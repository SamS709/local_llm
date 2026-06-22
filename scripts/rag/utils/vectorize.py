from ollama import Client

MODEL_EMBED = 'nomic-embed-text:latest'
HOST = "http://100.116.131.79:11434/"

def vectoriser(textes: list[str], batch_size: int = 128, delay: float = 0.1) -> list[list[float]]:
    """Vectorise une liste de textes avec Ollama, par lots pour éviter de saturer le GPU."""
    all_embeddings = []
    n = len(textes)
    client = Client(host=HOST)
    for i in range(0, n, batch_size):
        batch = textes[i:i + batch_size]
        response = client.embed(model=MODEL_EMBED, input=batch)
        all_embeddings.extend(response.embeddings)
        print(f"  Vectorisé {min(i + batch_size, n)}/{n} chunks")
        # time.sleep(delay)
    return all_embeddings

if __name__ == "__main__":
    print(vectoriser(["coucou"]))
 
