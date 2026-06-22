"""Local LLM Scripts Package."""

from .embed import vectoriser, cosine_similarity, indexer, rechercher
from .sub_urls import get_markdown_urls, get_markdown_urls_from_github_tree
from .ollama_http import OllamaClient as HTTPClient

__all__ = [
    "vectoriser",
    "cosine_similarity",
    "indexer",
    "rechercher",
    "get_markdown_urls",
    "get_markdown_urls_from_github_tree",
    "HTTPClient",
]