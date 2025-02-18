from state import State
from llm import llm_with_tools
from langchain_core.messages import ChatMessage

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}
