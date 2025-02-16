from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

class State(TypedDict):
    messages: Annotated[list, add_messages]




def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile the graph
graph = graph_builder.compile()

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
    img_data = graph.get_graph().draw_ascii()
    print(img_data)
    run_chatbot()
