"""Documentation search tools for detected technologies."""
import aiohttp
from langchain_core.tools import tool


@tool
async def search_langchain_docs(query: str) -> str:
    """Search LangChain documentation for relevant snippets.

    Args:
        query: Search query string

    Returns:
        Relevant documentation snippets as a string
    """
    # For demonstration, fetch LangChain docs homepage and search for query
    url = "https://python.langchain.com/en/latest/index.html"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return f"Error fetching LangChain docs: HTTP {resp.status}"
                text = await resp.text()
        # Simple snippet extraction: find first occurrence of query and surrounding text
        idx = text.lower().find(query.lower())
        if idx == -1:
            return "No relevant LangChain documentation found for query."
        start = max(0, idx - 200)
        end = min(len(text), idx + 200)
        snippet = text[start:end]
        return snippet
    except Exception as e:
        return f"Error searching LangChain docs: {str(e)}"


@tool
async def search_fastapi_docs(query: str) -> str:
    """Search FastAPI documentation for relevant snippets.

    Args:
        query: Search query string

    Returns:
        Relevant documentation snippets as a string
    """
    url = "https://fastapi.tiangolo.com/en/latest/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return f"Error fetching FastAPI docs: HTTP {resp.status}"
                text = await resp.text()
        idx = text.lower().find(query.lower())
        if idx == -1:
            return "No relevant FastAPI documentation found for query."
        start = max(0, idx - 200)
        end = min(len(text), idx + 200)
        snippet = text[start:end]
        return snippet
    except Exception as e:
        return f"Error searching FastAPI docs: {str(e)}"


@tool
async def search_nextjs_docs(query: str) -> str:
    """Search Next.js documentation for relevant snippets.

    Args:
        query: Search query string

    Returns:
        Relevant documentation snippets as a string
    """
    url = "https://nextjs.org/docs"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return f"Error fetching Next.js docs: HTTP {resp.status}"
                text = await resp.text()
        idx = text.lower().find(query.lower())
        if idx == -1:
            return "No relevant Next.js documentation found for query."
        start = max(0, idx - 200)
        end = min(len(text), idx + 200)
        snippet = text[start:end]
        return snippet
    except Exception as e:
        return f"Error searching Next.js docs: {str(e)}"
