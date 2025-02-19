from dotenv import load_dotenv; load_dotenv()
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Interrupt, Command
from langchain_core.tools import tool

@tool
def human_assistance(query: str) -> dict:
    """Use this to ask the human for assistance."""

    # Pause execution and wait for human input
    human_response = interrupt({"question": query})

    # Return a structured tool response
    return {"response": human_response}




tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
tool_node = ToolNode(tools=tools)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def build_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot",tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.set_entry_point("chatbot")
    return graph_builder.compile(checkpointer=MemorySaver())




def stream_graph_updates(user_input: str, graph: CompiledStateGraph, config: dict):
    messages = [{"role": "user", "content": user_input}]

    # Stream the graph updates
    events = graph.stream(
        {"messages": messages},
        config=config,
        stream_mode="values",
    )

    for event in events:
        if 'messages' not in event:
            breakpoint()
            continue
        last_message = event["messages"][-1]
        # Check if AI is making a tool call
        if "tool_calls" in last_message.additional_kwargs:
            tool_call = last_message.additional_kwargs["tool_calls"][0]
            if tool_call['function']['name'] == "human_assistance":
                query = tool_call["function"]["arguments"]
                tool_call_id = tool_call["id"]

                # Prompt the user for input
                human_response = input(f"Human assistance needed: {query}\nYour response: ")

                # Resume execution with a structured tool response
                response_payload = {
                    "messages": [
                        {
                            "role": "tool",
                            "name": "human_assistance",
                            "content": human_response,
                            "tool_call_id": tool_call_id  # Ensure the response is linked properly
                        }
                    ]
                }

                print(f"[DEBUG] Resuming graph with response: {response_payload}")
                resumed_events = graph.stream(
                    Command(resume=response_payload),
                    config,
                    stream_mode="updates")

                for resumed_event in resumed_events:
                    if 'messages' in resumed_event:
                        resumed_event["messages"][-1].pretty_print()
        else:
            last_message.pretty_print()


graph = build_graph()


def run_chatbot():
    config = {"configurable": {"thread_id": "1"}}
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break
            stream_graph_updates(user_input, graph, config)
        except Exception as e:
            print("error", e)
            user_input = "Remember my name?"
            stream_graph_updates(user_input, graph, config)
            break





if __name__ == "__main__":
    # VISUALIZE THE GRAPH
    img_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img_data)
    img_data = graph.get_graph().draw_ascii()
    print(img_data)
    run_chatbot()
    
