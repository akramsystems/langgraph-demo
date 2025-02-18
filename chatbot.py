from state import State
from llm import llm_with_tools


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
