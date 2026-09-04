import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from ddgs import DDGS
from tools.tool_registry import registry

@registry.register(
    name="web_search",
    description="Searches the web for external information, news, or technical documentation.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query string."}
        },
        "required": ["query"]
    }
)
def web_search(query: str) -> str:
    try:
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return "No web results found."
        
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"