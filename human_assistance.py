from langgraph.types import interrupt
from langchain_core.tools import tool

@tool
def human_assistance(query: str) -> str:
    """Use this to ask the human for assistance."""
    human_response = interrupt(query)
    return human_response

