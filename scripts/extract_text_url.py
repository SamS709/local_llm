import trafilatura
import json
from pathlib import Path

def extraire_texte(html: str) -> str:
    """Extrait le contenu principal d'une page HTML en texte propre."""
    return trafilatura.extract(html) or ""


def extraire_donnees(html: str) -> dict:
    """Extrait le contenu et ses métadonnées (titre, auteur, date)."""
    brut = trafilatura.extract(html, output_format="json", with_metadata=True)
    if not brut:
        return {}
    donnees = json.loads(brut)
    return {
        "titre": donnees.get("title"),
        "auteur": donnees.get("author"),
        "date": donnees.get("date"),
        "texte": donnees.get("text", ""),
    }

def extraire_markdown(html: str) -> str:
    """Extrait le contenu principal en Markdown — titres et listes conservés."""
    return trafilatura.extract(html, output_format="markdown") or ""

def constituer_corpus(urls: list[str]) -> list[dict]:
    """Télécharge et extrait une liste d'URL en documents structurés."""
    corpus = []
    for url in urls:
        html = trafilatura.fetch_url(url)
        if html is None:
            continue  # page injoignable : on passe à la suivante
        donnees = extraire_donnees(html)
        if donnees.get("texte"):
            donnees["source"] = url
            corpus.append(donnees)
    return corpus



def ecrire_corpus(corpus: list[dict], dossier: str) -> None:
    """Écrit chaque document du corpus dans un fichier JSON."""
    base = Path(dossier)
    base.mkdir(parents=True, exist_ok=True)
    for i, document in enumerate(corpus):
        (base / f"doc_{i:03d}.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        
if __name__ == "__main__":
    corpus = constituer_corpus(["https://github.com/gohugoio/hugoDocs/blob/master/content/en/_common/embedded-get-page-images.md", "https://github.com/gohugoio/hugoDocs/blob/master/content/en/_common/glob-patterns.md"])
    ecrire_corpus(corpus, "corpus")
    