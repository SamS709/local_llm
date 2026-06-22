"""Custom RAG MCP server for code retrieval"""
from typing import Literal
from mcp.server.fastmcp import FastMCP
import chromadb
from query import hybrid_search
 
# Available vector databases, mapped to their on-disk path.
# Add new entries here as new doc sets get indexed.
DB_PATHS = {
    "hugoVec": "hugoVec",
    "isaacsimVec": "IsaacSimVec",
    "isaaclabVec": "IsaacLabVec",
}
 
DbName = Literal["hugoVec", "isaacsimVec", "isaaclabVec"]
 
app = FastMCP("custom-rag-server")
 
# Cache clients/collections so we don't reconnect to disk on every call
_collections = {}
 
 
def get_collection(db: DbName):
    if db not in DB_PATHS:
        raise ValueError(f"Unknown db '{db}'. Valid options: {list(DB_PATHS.keys())}")
    if db not in _collections:
        client = chromadb.PersistentClient(path=DB_PATHS[db])
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
        db: Which documentation set to search. One of: "hugoVec" (Hugo framework docs),
            "isaaclabVec" (IsaacLab docs), "isaacsimVec" (IsaacSim docs).
        limit: Maximum number of results to return
    """
    collection = get_collection(db)
    results = hybrid_search(collection, query, k=limit, k_retrieval=int(1.5 * limit))
    formatted = "\n\n---\n\n".join(
        f"File: {r['source']}\n\n{r['text']}" for r in results
    )
    return formatted or "No results found."
 
 
@app.tool()
async def get_file_context(filename: str, db: DbName) -> str:
    """
    Get all chunks from a specific file.
 
    Args:
        filename: The name of the file to retrieve
        db: Which documentation set to search. One of: "hugoVec" (Hugo docs),
            "isaaclabVec" (IsaacLab docs), "isaacsimVec" (IsaacSim docs).
    """
    collection = get_collection(db)
    results = collection.get(
        where={"source": filename},
        include=["documents", "metadatas"],
    )
    return "\n".join(results["documents"])
 
 
if __name__ == "__main__":
    app.run()
