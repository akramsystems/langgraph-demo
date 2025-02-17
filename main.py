from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from basic_tool import BasicToolNode


load_dotenv()

# Define the tools
tool = TavilySearchResults(max_results=2)
tools = [tool]
tool_node = BasicToolNode(tools=tools)


# Define the LLM with tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def route_tools(state: State) -> str:
    """
    Use in the conditional_edge to route to the ToolNode if the last message has tool calls.  Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError("No AI message found in the state")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def build_graph() -> StateGraph:
    # Build the graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    # Add Conditional Edge
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        {"tools": "tools", END: END},
    )
    
    # Add edges
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    return graph_builder.compile()

graph = build_graph()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

def run_chatbot():
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break

            stream_graph_updates(user_input)
        except Exception as e:
            # fallback if input is not available
            user_input = "What do you know about LangGraph?"
            print("User: ", user_input)
            stream_graph_updates(user_input)




if __name__ == "__main__":
    # VISUALIZE THE GRAPH
    # img_data = graph.get_graph().draw_ascii()
    img_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img_data)
    # print(img_data)
    # run_chatbot()
    
