from dotenv import load_dotenv; load_dotenv()

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

from graph import build_graph, stream_graph_updates

memory =  MemorySaver() 

graph = build_graph(memory)


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
            # fallback if input is not available
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
    
