from langchain_community.tools.tavily_search import TavilySearchResults
from core.config import settings
search_tool = TavilySearchResults(
    tavily_api_key=settings.TAVILY_API_KEY,
    max_results=5
)
