from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool_node = ToolNode(tools=tools)



