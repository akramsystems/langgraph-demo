from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from state import State
from chatbot import chatbot
from tools import tools

def build_graph() -> CompiledStateGraph:
    # Build the graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    
    tool_node = ToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    # Add Conditional Edge
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    
    # Add edges
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str, graph: CompiledStateGraph, config: dict):
    # Note the thread_id is a specific convention for the memory checkpoint
    # to save the state of the conversation
    # we would need to change this if we want to save the state of the conversation
    # for multiple users and/or conversations

    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values",
    )

    for event in events:
        event["messages"][-1].pretty_print()
