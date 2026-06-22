import unicodedata
import re

_BALISES_HTML = re.compile(r"<[^>]+>")
_INVISIBLES = re.compile(r"[​-‏‪-‮﻿­]")
_ESPACES = re.compile(r"[ \t]+")
_LIGNES_VIDES = re.compile(r"\n\s*\n+")


def normaliser_unicode(texte: str) -> str:
    """Ramène le texte à une forme Unicode canonique (NFC)."""
    return unicodedata.normalize("NFC", texte)


def retirer_html(texte: str) -> str:
    """Supprime les balises HTML résiduelles."""
    return _BALISES_HTML.sub("", texte)


def retirer_invisibles(texte: str) -> str:
    """Supprime les caractères invisibles (zero-width, BOM, soft hyphen)."""
    return _INVISIBLES.sub("", texte)


def normaliser_espaces(texte: str) -> str:
    """Réduit les espaces multiples et les lignes vides surnuméraires."""
    texte = _ESPACES.sub(" ", texte)
    texte = _LIGNES_VIDES.sub("\n\n", texte)
    lignes = [ligne.strip() for ligne in texte.splitlines()]
    return "\n".join(lignes).strip()

def nettoyer(texte: str) -> str:
    """Pipeline de nettoyage complet — l'ordre des étapes compte."""
    texte = normaliser_unicode(texte)
    texte = retirer_html(texte)
    texte = retirer_invisibles(texte)
    texte = normaliser_espaces(texte)
    return texte


