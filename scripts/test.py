"""Custom RAG MCP server for code retrieval"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import chromadb
from scripts.rag.scripts.query import dense_search

# Initialize your vector database connection




if __name__ == "__main__":
    path = "hugoVec"
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection("docs")


    results = collection.get(
        where={"source": "hugo_config"},
        include=["documents", "metadatas"],
    )
    print(collection)