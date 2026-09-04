from duckduckgo_search import DDGS
from tools.tool_registry import registry

@registry.register(
    name="web_search",
    description="Searches the web for current events, live information, or facts YVES does not know.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the internet."
            }
        },
        "required": ["query"]
    }
)
def web_search(query: str) -> str:
    """Performs a web search using DuckDuckGo and returns key snippets."""
    try:
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return "No relevant web results found."
        
        summary = []
        for item in results:
            summary.append(f"Title: {item['title']}\nSnippet: {item['body']}\nSource: {item['href']}\n")
        
        return "\n".join(summary)
    except Exception as e:
        return f"Failed to perform search: {str(e)}"