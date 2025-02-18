from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from human_assistance import human_assistance

tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
# tool_node = ToolNode(tools=tools)



