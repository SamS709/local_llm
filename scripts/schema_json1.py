from typing import Literal
from ollama import Client
from pydantic import BaseModel, EmailStr, Field

MODEL = "qwen_tuned2:latest"
HOST = "http://localhost:11434"

class TicketSupport(BaseModel):
    """Ticket extrait d'un email entrant."""
    expediteur_nom: str
    expediteur_email: EmailStr
    expediteur_role: str | None = None
    entreprise: str
    numero_client: str | None = None
    categorie: Literal["authentification", "facturation", "performance", "bug", "autre"] # Literal assure l'appartenance à l'une des catégories listées: le modèle n'a pas le choix.
    priorite: Literal["basse", "normale", "haute", "critique"]
    resume: str = Field(description="Synthèse en 1-2 phrases du problème exposé.")

EMAIL = """
De: paul.martin@datalab.io
Objet: Latence très élevée depuis hier
Vos endpoints /v1/embeddings prennent 8-12 secondes depuis hier soir.
Numéro client : DTL-998. — Paul, CTO Datalab
"""

client = Client(host=HOST)
response = client.chat(
    model=MODEL,
    messages=[{"role": "user", "content": EMAIL}],
    # Pydantic génère le JSON Schema automatiquement
    format=TicketSupport.model_json_schema(),
    options={"temperature": 0},
)

# Validation + objet typé en une ligne
ticket = TicketSupport.model_validate_json(response["message"]["content"])
print(ticket)
print(ticket.categorie)        # autocomplétion IDE
print(ticket.priorite)