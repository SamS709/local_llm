"""
Quick smoke test for search_technical_docs (and get_file_context).

Run this from the same directory as your server.py / query.py, e.g.:

    python test_search_technical_docs.py hugoVec "how do I add a shortcode"

It calls the tool functions directly (no MCP transport involved), so it's a
fast way to check that:
  - chromadb can open the on-disk collection
  - hybrid_search returns results
  - the formatted output looks sane

Usage:
    python test_search_technical_docs.py <db_name> [query] [limit]

Examples:
    python test_search_technical_docs.py hugoVec
    python test_search_technical_docs.py isaaclabVec "reset environment" 5
"""
import asyncio
import sys
import os
# Import directly from your server module. Adjust this if your file
# isn't literally named server.py.
if __name__=="__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
from scripts.rag.srv.custom_mcp_rag import search_technical_docs, get_file_context, DB_PATHS



async def main():
    db = sys.argv[1] if len(sys.argv) > 1 else "isaaclabVec"
    query = sys.argv[2] if len(sys.argv) > 2 else "getting started"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    if db not in DB_PATHS:
        print(f"[FAIL] '{db}' is not a known db. Valid options: {list(DB_PATHS.keys())}")
        sys.exit(1)

    print(f"--- search_technical_docs(query={query!r}, db={db!r}, limit={limit}) ---")
    try:
        result = await search_technical_docs(query=query, db=db, limit=limit)
    except Exception as e:
        print(f"[FAIL] search_technical_docs raised: {type(e).__name__}: {e}")
        sys.exit(1)

    if not result or result.strip() == "No results found.":
        print("[WARN] Tool ran without error but returned no results.")
        print("       Check that the collection at the configured path is actually populated.")
    else:
        preview = result if len(result) < 2000 else result[:2000] + "\n...[truncated]"
        print(preview)
        print(f"\n[OK] Got {len(result)} chars back.")

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())


def test_mcp():
    """Wrapper so that srv/__init__.py can import it."""
    return asyncio.run(main())


