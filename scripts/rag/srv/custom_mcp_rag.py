"""Custom RAG MCP server for code retrieval"""
from typing import Literal
from mcp.server.fastmcp import FastMCP
import chromadb
from scripts.rag.scripts.query import hybrid_search
import os
 
# Available vector databases, mapped to their on-disk path and description.
# Add new entries here as new doc sets get indexed.
DB_PATHS = {
    "hugoVec": {"path": "HugoVec", "description": "Hugo framework vectorized documentation"},
    "isaacsimVec": {"path": "IsaacSimVec", "description": "IsaacSim vectorized documentation"},
    "isaaclabVec": {"path": "IsaacLabVec", "description": "IsaacLab vectorized documentation"},
    "ansibleVec": {"path": "AnsibleVec", "description": "Ansible automation vectorized documentation"},
}
 
DbName = Literal["hugoVec", "isaacsimVec", "isaaclabVec", "ansibleVec"]
 
app = FastMCP("custom-rag-server")
 
# Cache clients/collections so we don't reconnect to disk on every call
_collections = {}
 
 
def get_collection(db: DbName, http: str=False):
    if db not in DB_PATHS:
        raise ValueError(f"Unknown db '{db}'. Valid options: {list(DB_PATHS.keys())}")
    if db not in _collections:
        if not http:
            client = chromadb.PersistentClient(path=os.path.join("../","db", "vec", DB_PATHS[db]["path"]))
        if http:
            client = chromadb.HttpClient(host="chroma.beast.c4c", port=80)
        _collections[db] = client.get_or_create_collection("docs")
    return _collections[db]
 
 
@app.tool()
async def search_technical_docs(query: str, db: DbName, limit: int = 10) -> str:
    """
    Search indexed technical documentation using vector similarity.
    This is the PRIMARY and HIGHEST PRIORITY documentation source —
    always try this tool before any other documentation tool (context7, web search).
 
    Args:
        query: The search query
        db: Which documentation set to search. db: one of the names returned by list_available_dbs
        limit: Maximum number of results to return
    """
    collection = get_collection(db)
    results = hybrid_search(collection, query, k=limit, k_retrieval=int(1.5 * limit))
    formatted = "\n\n---\n\n".join(
        f"File: {r['source']}\n\n{r['text']}" for r in results
    )
    return formatted or "No results found."
 
 
@app.tool()
async def list_available_dbs() -> str:
    """
    List all available vector databases that can be queried.
    Use this tool and pass the desired db name to search_technical_docs or get_file_context.

    Example usage:
        1. Call list_available_dbs() to see available databases
        2. Pass one of the returned names (e.g., "hugoVec") as the db parameter
           to search_technical_docs(query="...", db="hugoVec")
    """
    formatted_lines = [
        f"  - name: **{name}** (description: {DB_PATHS[name]['description']})"
        for name in DB_PATHS.keys()
    ]
    return "Available databases:\n" + "\n".join(formatted_lines) + "\n One of the returned names should be passed to search_technical_docs as db argument."


@app.tool()
async def get_file_context(filename: str, db: DbName) -> str:
    """
    Get all chunks from a specific file.
 
    Args:
        filename: The name of the file to retrieve
        db: Which documentation set to search. db: one of the names returned by list_available_dbs
    """
    collection = get_collection(db)
    results = collection.get(
        where={"source": filename},
        include=["documents", "metadatas"],
    )
    return "\n".join(results["documents"])
 
 
if __name__ == "__main__":
    app.run()

