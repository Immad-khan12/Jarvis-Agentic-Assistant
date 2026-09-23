import os
import requests


def search_web(query: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API Key is missing in environment settings."

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "search_depth": "basic"},
            timeout=15
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Web search failed: {str(e)}"

    results = response.json().get("results", [])
    if not results:
        return "No web results found."

    summaries = [f"- {r.get('title', 'Untitled')}: {r.get('content', '')}" for r in results[:3]]
    return "\n".join(summaries)