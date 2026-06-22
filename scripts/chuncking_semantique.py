# Utile pour les longs texte sans structure.


import statistics
import re

_FIN_PHRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])")

def segmenter_phrases(texte: str) -> list[str]:
    """Découpe un texte en phrases (segmentation simple par ponctuation)."""
    texte = " ".join(texte.split())
    if not texte:
        return []
    return [p.strip() for p in _FIN_PHRASE.split(texte) if p.strip()]

def chunk_semantique(texte: str) -> list[str]:
    phrases = segmenter_phrases(texte)
    if len(phrases) <= 1:
        return phrases
    vecteurs = _vectoriser(phrases)
    similarites = [
        _cosinus(vecteurs[i], vecteurs[i + 1])
        for i in range(len(phrases) - 1)
    ]
    

def seuil_adaptatif(similarites: list[float]) -> float:
    """Seuil de rupture : sous la moyenne moins un écart-type."""
    if len(similarites) < 2:
        return 0.0
    return statistics.mean(similarites) - statistics.pstdev(similarites)

def trouver_ruptures(similarites: list[float], seuil: float) -> list[int]:
    """Indices i tels qu'une rupture survient après la phrase i."""
    return [i for i, s in enumerate(similarites) if s < seuil]